from functools import lru_cache

from app.config import AI_PROVIDER, GEMINI_API_KEY
from app.services.ai_service import AIService
from app.services.gemini_service import GeminiService
from app.services.local_ai_service import LocalAIService


PLACEHOLDER_GEMINI_KEYS = {
    "",
    "test_api_key_for_local_and_ci",
    "your_gemini_api_key",
}


@lru_cache
def get_ai_service() -> AIService:
    provider = AI_PROVIDER.lower().strip()

    if provider == "local":
        return LocalAIService()

    if provider == "gemini" and GEMINI_API_KEY.strip() in PLACEHOLDER_GEMINI_KEYS:
        return LocalAIService()

    if provider == "gemini":
        return GeminiService()

    raise ValueError(f"Unsupported AI provider: {AI_PROVIDER}")
