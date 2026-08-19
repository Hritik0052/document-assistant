from django.conf import settings
from openai import AsyncOpenAI


def openrouter_client() -> AsyncOpenAI:
    if not settings.LLM_CONFIGURED:
        raise RuntimeError(
            'OPEN_ROUTER_API_KEY is not set. Add your OpenRouter key to .env.'
        )
    return AsyncOpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
        timeout=60.0,
        default_headers={
            'HTTP-Referer': 'http://localhost:8000',
            'X-Title': 'RAG Document Q&A',
        },
    )
