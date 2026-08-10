import os

from google import genai
from google.genai import types


class RAGGenerationError(Exception):
    """Raised when the LLM cannot generate a RAG answer."""


class GeminiRAGService:

    def __init__(self) -> None:
        self.client = genai.Client()

        self.model = os.getenv(
            "GEMINI_CHAT_MODEL",
            os.getenv(
                "GEMINI_MODEL",
                "gemini-2.5-flash",
            ),
        )

    def generate_answer(
        self,
        *,
        question: str,
        context: str,
    ) -> str:
        """
        Generate an answer using only retrieved document context.
        """

        if not question or not question.strip():
            raise RAGGenerationError(
                "Question cannot be empty."
            )

        if not context or not context.strip():
            raise RAGGenerationError(
                "Retrieved context cannot be empty."
            )

        prompt = self._build_prompt(
            question=question,
            context=context,
        )

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "You are an AI payment-document assistant. "
                        "Answer questions only from the supplied "
                        "document context. "
                        "Do not invent facts that are not present "
                        "in the context. "
                        "If the context does not contain enough "
                        "information, clearly say that the document "
                        "does not provide enough information."
                    ),
                    temperature=0.2,
                    max_output_tokens=1200,
                ),
            )

            answer = response.text

            if not answer or not answer.strip():
                raise RAGGenerationError(
                    "Gemini returned an empty answer."
                )

            return answer.strip()

        except RAGGenerationError:
            raise

        except Exception as exc:
            raise RAGGenerationError(
                "Gemini RAG answer generation failed."
            ) from exc

    @staticmethod
    def _build_prompt(
        *,
        question: str,
        context: str,
    ) -> str:

        return f"""
Use the following retrieved document context to answer
the user's question.

DOCUMENT CONTEXT
----------------
{context}

USER QUESTION
-------------
{question}

INSTRUCTIONS
------------
- Answer only from the document context.
- Do not use unsupported assumptions.
- If the answer is not present in the context, say so.
- Be concise but complete.
- When appropriate, refer to the supplied source numbers.
"""