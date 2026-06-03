import re
import json
from google.genai import types
from langchain_core.messages import HumanMessage, AIMessage
from agents.state import AgentState
from services.gemini_service import get_client
from config import settings

MAX_HISTORY_MSG_CHARS = 300  # truncate long AI responses in history to cap tokens

SYSTEM_TEMPLATE = """\
You are a post-discharge care assistant. Follow these rules strictly:

GROUNDING RULES:
1. Answer using ONLY the patient profile and discharge records provided below.
2. If the answer is not in the records, say exactly: "I don't have that in your
   discharge records. Please contact your care provider." Do not guess.
3. You MAY provide general health information, but you MUST prefix it with
   "General information:" and never present it as this patient's specific instructions.
4. For every statement drawn from the records, note which record it came from in
   the "sources" list using the record labels (e.g. medications, red_flags,
   discharge_summary, diet_restrictions, followup_schedule, profile).

{profile_section}

{context_section}

Reply ONLY with valid JSON, no markdown:
{{"level": 1|2|3, "response": "...", "sources": ["<record labels used>"]}}
Triage: 1=self-care, 2=see doctor within 48h, 3=emergency (bold warning + call 911).
"""


def _build_profile_section(info: dict) -> str:
    # Only care-relevant fields are sent to the LLM. DOB, email, and the
    # emergency contact's email are deliberately withheld — they are PII that
    # the model does not need to answer post-discharge questions. (The alert
    # node reads emergency_contact_email directly from state, not via the LLM.)
    if not info:
        return ""
    lines = ["Patient Profile:"]
    if info.get("name"):
        lines.append(f"- Name: {info['name']}")
    if info.get("procedure"):
        lines.append(f"- Procedure: {info['procedure']} on {info.get('procedure_date', 'N/A')}")
    if info.get("followup_date"):
        lines.append(f"- Follow-up: {info['followup_date']} — {info.get('followup_contact', '')}")
    if info.get("emergency_contact_name"):
        lines.append(f"- Emergency Contact: {info['emergency_contact_name']}")
    return "\n".join(lines)


def _build_system_instruction(chunks: list[str], patient_info: dict) -> str:
    profile_section = _build_profile_section(patient_info)
    context_section = (
        "Relevant discharge records:\n" + "\n".join(chunks)
        if chunks
        else "No matching discharge records for this query."
    )
    return SYSTEM_TEMPLATE.format(
        profile_section=profile_section,
        context_section=context_section,
    )


def _to_genai_contents(history, current_query: str) -> list[types.Content]:
    contents = []
    for msg in history:
        # Truncate long history messages — old AI responses are verbose
        text = str(msg.content)[:MAX_HISTORY_MSG_CHARS]
        if isinstance(msg, HumanMessage):
            contents.append(types.Content(role="user", parts=[types.Part(text=text)]))
        elif isinstance(msg, AIMessage):
            contents.append(types.Content(role="model", parts=[types.Part(text=text)]))
    contents.append(types.Content(role="user", parts=[types.Part(text=current_query)]))
    return contents


def _parse(text: str) -> tuple[int, str, list[str]]:
    clean = re.sub(r"```(?:json)?|```", "", text).strip()
    try:
        data = json.loads(clean)
        level = int(data.get("level", 1))
        response = str(data.get("response", ""))
        sources = data.get("sources", [])
        if not isinstance(sources, list):
            sources = []
        sources = [str(s).strip().lower() for s in sources if str(s).strip()]
        return level, response, sources
    except Exception:
        m = re.search(r'"level"\s*:\s*([123])', clean)
        level = int(m.group(1)) if m else 1
        m2 = re.search(r'"response"\s*:\s*"(.*?)"(?=\s*[,}])', clean, re.DOTALL)
        response = m2.group(1) if m2 else clean
        return level, response, []


async def triage_node(state: AgentState) -> dict:
    contents = _to_genai_contents(state["chat_history"], state["query"])

    result = await get_client().aio.models.generate_content(
        model=settings.gemini_model,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=_build_system_instruction(state["chunks"], state["patient_info"]),
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )

    level, response, sources = _parse(result.text)
    return {"triage_level": level, "response": response, "sources": sources}
