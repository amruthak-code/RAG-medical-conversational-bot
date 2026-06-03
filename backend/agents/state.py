from typing import TypedDict
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    patient_id: str
    session_id: str
    query: str
    chunks: list[str]
    chat_history: list[BaseMessage]
    patient_info: dict
    triage_level: int
    alert_sent: bool
    response: str
    sources: list[str]
    emergency_contact_email: str
