from typing import Optional
from pinecone import Pinecone, ServerlessSpec
from config import settings
from services.embedder import embed, DIMENSION

_index = None

EMBED_COLUMNS = [
    "discharge_summary",
    "medications",
    "red_flags",
    "diet_restrictions",
    "followup_schedule",
]


def get_index():
    global _index
    if _index is not None:
        return _index

    pc = Pinecone(api_key=settings.pinecone_api_key.strip())
    existing = {i.name for i in pc.list_indexes()}

    if settings.pinecone_index_name not in existing:
        pc.create_index(
            name=settings.pinecone_index_name,
            dimension=DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(
                cloud=settings.pinecone_cloud,
                region=settings.pinecone_region,
            ),
        )

    _index = pc.Index(settings.pinecone_index_name)
    return _index


def upsert_patient_docs(patient_id: str, docs: dict[str, str]) -> None:
    index = get_index()

    doc_types = [k for k, v in docs.items() if v and str(v).strip()]
    texts = [str(docs[k]).strip() for k in doc_types]
    if not texts:
        return

    embeddings = embed(texts)

    vectors = [
        {
            "id": f"{patient_id}_{doc_type}",
            "values": embedding,
            "metadata": {
                "patient_id": patient_id,
                "doc_type": doc_type,
                "text": text,
            },
        }
        for doc_type, embedding, text in zip(doc_types, embeddings, texts)
    ]
    index.upsert(vectors=vectors)


# all-MiniLM-L6-v2 produces low cosine scores: genuinely relevant chunks
# score ~0.2-0.35, noise scores <0.1. Threshold tuned against real query
# scores (see test data), not assumed. top_k=3 is the primary limiter.
SCORE_THRESHOLD = 0.12


def query_patient(patient_id: str, query: str, top_k: int = 3) -> list[str]:
    index = get_index()
    query_embedding = embed([query])[0]

    result = index.query(
        vector=query_embedding,
        top_k=top_k,
        filter={"patient_id": {"$eq": patient_id}},
        include_metadata=True,
        include_values=False,
    )

    return [
        f"[{m.metadata['doc_type']}]: {m.metadata['text']}"
        for m in result.matches
        if m.score >= SCORE_THRESHOLD
        and m.metadata
        and m.metadata.get("text")
    ]
