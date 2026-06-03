from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from agents.graph import run_pipeline
from services.chat_history_service import load_history

router = APIRouter(prefix="/api", tags=["chat"])

TRIAGE_LABELS = {
    1: "Self-Care",
    2: "See a Doctor",
    3: "Emergency — Call 911",
}


class ChatRequest(BaseModel):
    patient_id: str
    session_id: str
    message: str


@router.get("/history/{patient_id}")
async def get_history(patient_id: str):
    if not patient_id.strip():
        raise HTTPException(status_code=400, detail="patient_id is required.")
    messages = await load_history(patient_id.strip(), limit=50)
    return {
        "patient_id": patient_id,
        "messages": [
            {
                "role": "human" if isinstance(m, HumanMessage) else "ai",
                "content": m.content,
            }
            for m in messages
        ],
    }


@router.post("/chat")
async def chat(request: ChatRequest):
    if not request.patient_id.strip():
        raise HTTPException(status_code=400, detail="patient_id is required.")
    if not request.session_id.strip():
        raise HTTPException(status_code=400, detail="session_id is required.")
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message is required.")

    result = await run_pipeline(
        patient_id=request.patient_id.strip(),
        session_id=request.session_id.strip(),
        query=request.message.strip(),
    )

    level = result.get("triage_level", 1)
    return {
        "patient_id": request.patient_id,
        "session_id": request.session_id,
        "response": result.get("response", ""),
        "triage_level": level,
        "triage_label": TRIAGE_LABELS.get(level, "Self-Care"),
        "alert_sent": result.get("alert_sent", False),
        "sources": result.get("sources", []),
    }
