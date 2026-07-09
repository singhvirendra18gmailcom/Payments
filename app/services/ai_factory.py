from app.config import AI_PROVIDER
from app.services.ai_service import AIService
from app.services.gemini_service import GeminiService


def get_ai_service() -> AIService:
    if AI_PROVIDER.lower() == "gemini":
        return GeminiService()

    raise ValueError(f"Unsupported AI provider: {AI_PROVIDER}")