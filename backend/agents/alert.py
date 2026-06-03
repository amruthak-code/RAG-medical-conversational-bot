from agents.state import AgentState
from services.sendgrid_service import send_emergency_alert


async def alert_node(state: AgentState) -> dict:
    await send_emergency_alert(
        patient_id=state["patient_id"],
        triggering_message=state["query"],
        to_email=state["emergency_contact_email"],
    )
    return {"alert_sent": True}
