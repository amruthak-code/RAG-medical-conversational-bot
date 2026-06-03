from google import genai
from google.genai import types
from config import settings

_client: genai.Client | None = None

# Disable extended thinking — thinking models (gemini-3.5+) default to it,
# adding 30+ seconds of latency. Budget=0 forces immediate response.
_CONFIG = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_budget=0),
)


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key.strip())
    return _client


async def generate(prompt: str) -> str:
    response = await get_client().aio.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=_CONFIG,
    )
    return response.text
