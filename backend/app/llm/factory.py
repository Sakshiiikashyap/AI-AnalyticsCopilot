from functools import lru_cache

from app.llm.base import LLMProvider


@lru_cache
def get_llm_provider() -> LLMProvider:
    from app.llm.gemini_provider import GeminiProvider

    return GeminiProvider()