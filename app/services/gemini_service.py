from google import genai
from google.genai import types
from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.services.ai_service import AIService
from app.logger import logger


class GeminiService(AIService):

    SYSTEM_PROMPT = """
    You are a senior payment systems expert.
    Explain clearly with examples.
    """

    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is missing")

        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = GEMINI_MODEL

    def ask(self, question: str) -> str:
        try:
            if not question or not question.strip():
                raise ValueError("Question cannot be empty")

            response = self.client.models.generate_content(
                model=self.model,
                contents=question,
                config=types.GenerateContentConfig(
                    system_instruction=self.SYSTEM_PROMPT
                )
            )

            if not response or not response.text:
                return "AI could not generate a response. Please try again."

            return response.text

        except ValueError as ex:
            logger.warning(f"Validation error in GeminiService: {ex}")
            return str(ex)

        except Exception as ex:
            logger.exception("Gemini API error")
            return "AI service is currently unavailable. Please try again later."

    def explain_payment(self, message_type: str, content: str) -> str:
        prompt = f"""
Explain the following payment message.

Message Type:
{message_type}

Message Content:
{content}

Please include:

1. Purpose
2. Message Flow
3. Important Fields
4. Business Example
5. Common Validation Errors
"""

        return self.ask(prompt)

    def health_check(self) -> bool:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents="Say OK"
            )
            return bool(response and response.text)

        except Exception as ex:
            logger.exception("Gemini health check failed")
            return False
