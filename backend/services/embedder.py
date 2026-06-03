from typing import Optional
from sentence_transformers import SentenceTransformer

_embedder: Optional[SentenceTransformer] = None
MODEL_NAME = "all-MiniLM-L6-v2"
DIMENSION = 384


def get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(MODEL_NAME)
    return _embedder


def embed(texts: list[str]) -> list[list[float]]:
    return get_embedder().encode(texts, convert_to_numpy=True).tolist()
