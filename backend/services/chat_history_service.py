import asyncio
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import BaseMessage
from config import settings

GEMINI_TURNS = 6    # turns passed to Gemini (token budget) — 12 messages
UI_MESSAGES   = 50  # messages loaded into the chat window on patient select


def _get_history(session_id: str) -> SQLChatMessageHistory:
    return SQLChatMessageHistory(
        session_id=session_id,
        connection=settings.sync_database_url,
    )


async def load_history(session_id: str, limit: int = GEMINI_TURNS * 2) -> list[BaseMessage]:
    """Load last `limit` messages. Default is Gemini's token budget (20 messages).
    Pass limit=UI_MESSAGES when loading for display only."""
    if not session_id:
        return []
    messages = await asyncio.to_thread(lambda: _get_history(session_id).messages)
    return messages[-limit:]


async def save_exchange(session_id: str, human_msg: str, ai_msg: str) -> None:
    def _save():
        history = _get_history(session_id)
        history.add_user_message(human_msg)
        history.add_ai_message(ai_msg)
    await asyncio.to_thread(_save)
