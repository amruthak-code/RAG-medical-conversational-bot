from agents.state import AgentState
from services.chat_history_service import save_exchange


async def response_node(state: AgentState) -> dict:
    await save_exchange(
        session_id=state["session_id"],
        human_msg=state["query"],
        ai_msg=state["response"],
    )
    return {}
