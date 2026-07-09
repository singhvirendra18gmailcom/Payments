from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY
from app.services.ai_service import AIService
from app.config import GEMINI_MODEL


class GeminiService(AIService):
    """
    Google Gemini implementation of AIService.
    """

    SYSTEM_PROMPT = """
    You are an expert Payment Systems Assistant.

    Your expertise includes:
    - SWIFT MT Messages
    - ISO 20022
    - PACS.008
    - PACS.009
    - CAMT Messages
    - SEPA
    - UPI
    - NEFT
    - RTGS
    - Fedwire
    - CHIPS
    - Payment investigations
    - CBPR+

    Rules:
    - Give accurate payment domain answers.
    - Explain concepts with examples.
    - Use simple language unless technical detail is requested.
    """

    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = GEMINI_MODEL

    def ask(self, question: str) -> str:
        """
        Ask a general payment-related question.
        """

        try:

            response = self.client.models.generate_content(
                model=self.model,
                config=types.GenerateContentConfig(
                    system_instruction=self.SYSTEM_PROMPT
                ),
                contents=question,
            )

            return response.text

        except Exception as ex:
            raise Exception(f"Gemini Error: {str(ex)}")

    def explain_payment(self, message_type: str, content: str) -> str:
        """
        Explain payment message.
        """

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
        """
        Verify Gemini connectivity.
        """

        try:

            response = self.client.models.generate_content(
                model=self.model,
                contents="Hello"
            )

            return response.text is not None

        except Exception:
            return False