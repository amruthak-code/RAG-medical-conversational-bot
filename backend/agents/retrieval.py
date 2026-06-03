import asyncio
from sqlalchemy import select
from agents.state import AgentState
from services.pinecone_service import query_patient
from services.chat_history_service import load_history
from database import async_session_factory
from models import Patient

# Patient profiles are static — cache after first DB fetch to avoid
# hitting PostgreSQL on every chat request for the same patient.
_profile_cache: dict[str, dict] = {}


async def _get_patient_record(patient_id: str) -> dict:
    if patient_id in _profile_cache:
        return _profile_cache[patient_id]

    async with async_session_factory() as session:
        result = await session.execute(
            select(Patient).where(Patient.patient_id == patient_id)
        )
        p = result.scalar_one_or_none()
        if not p:
            return {}
        profile = {
            "name": p.patient_name,
            "dob": p.dob,
            "email": p.email,
            "procedure": p.procedure_name,
            "procedure_date": p.procedure_date,
            "followup_date": p.followup_date,
            "followup_contact": p.followup_contact,
            "emergency_contact_name": p.emergency_contact_name,
            "emergency_contact_email": p.emergency_contact_email or "",
        }

    _profile_cache[patient_id] = profile
    return profile


# Pure greetings/acknowledgements — no medical retrieval needed for these.
_CONVERSATIONAL = {
    "hi", "hello", "hey", "thanks", "thank you", "thank you so much",
    "ok", "okay", "got it", "great", "bye", "goodbye", "cool", "nice",
    "good morning", "good afternoon", "good evening", "good night",
    "yes", "no", "sure", "alright", "understood",
}


def _is_conversational(query: str) -> bool:
    cleaned = query.strip().lower().rstrip("!.?")
    return cleaned in _CONVERSATIONAL


async def retrieval_node(state: AgentState) -> dict:
    # Skip the Pinecone search for pure greetings/acknowledgements — it would
    # only return irrelevant chunks and waste a vector query + tokens.
    if _is_conversational(state["query"]):
        patient_info, chat_history = await asyncio.gather(
            _get_patient_record(state["patient_id"]),
            load_history(state["session_id"]),
        )
        chunks = []
    else:
        chunks, patient_info, chat_history = await asyncio.gather(
            asyncio.to_thread(query_patient, state["patient_id"], state["query"]),
            _get_patient_record(state["patient_id"]),
            load_history(state["session_id"]),
        )

    return {
        "chunks": chunks,
        "patient_info": patient_info,
        "emergency_contact_email": patient_info.get("emergency_contact_email", ""),
        "chat_history": chat_history,
    }
