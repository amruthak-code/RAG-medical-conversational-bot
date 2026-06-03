from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.retrieval import retrieval_node
from agents.triage import triage_node
from agents.alert import alert_node
from agents.response import response_node


def _route_after_triage(state: AgentState) -> str:
    return "alert" if state.get("triage_level", 1) == 3 else "response"


def _build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("retrieval", retrieval_node)
    graph.add_node("triage", triage_node)
    graph.add_node("alert", alert_node)
    graph.add_node("response", response_node)

    graph.set_entry_point("retrieval")
    graph.add_edge("retrieval", "triage")
    graph.add_conditional_edges(
        "triage",
        _route_after_triage,
        {"alert": "alert", "response": "response"},
    )
    graph.add_edge("alert", "response")
    graph.add_edge("response", END)

    return graph


_compiled = _build_graph().compile()


async def run_pipeline(patient_id: str, session_id: str, query: str) -> AgentState:
    initial: AgentState = {
        "patient_id": patient_id,
        "session_id": session_id,
        "query": query,
        "chunks": [],
        "chat_history": [],
        "patient_info": {},
        "triage_level": 1,
        "alert_sent": False,
        "response": "",
        "sources": [],
        "emergency_contact_email": "",
    }
    return await _compiled.ainvoke(initial)
