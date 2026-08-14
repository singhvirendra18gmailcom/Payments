from google import genai
from google.genai import types

from app.ai.embedding_config import (
    EMBEDDING_DIMENSION,
    GEMINI_EMBEDDING_MODEL,
)


class EmbeddingGenerationError(Exception):
    """Raised when an embedding cannot be generated."""


class GeminiEmbeddingService:
    def __init__(self) -> None:
        self.client = genai.Client()
        self.model = GEMINI_EMBEDDING_MODEL
        self.dimension = EMBEDDING_DIMENSION

    def prepare_document_text(
        self,
        *,
        text: str,
        title: str | None = None,
    ) -> str:
        """
        Format document text for retrieval embeddings.
        """

        normalized_title = title or "none"

        return (
            f"title: {normalized_title} | "
            f"text: {text}"
        )

    def prepare_query_text(self, question: str) -> str:
        """
        Format a future search query using the same retrieval task.
        """

        return (
            f"task: question answering | "
            f"query: {question}"
        )

    def generate_document_embedding(
        self,
        *,
        text: str,
        title: str | None = None,
    ) -> list[float]:
        if not text or not text.strip():
            raise EmbeddingGenerationError(
                "Cannot generate an embedding for empty text."
            )

        prepared_text = self.prepare_document_text(
            text=text,
            title=title,
        )

        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=prepared_text,
                config=types.EmbedContentConfig(
                    output_dimensionality=self.dimension,
                ),
            )

            if not response.embeddings:
                raise EmbeddingGenerationError(
                    "Gemini returned no embedding."
                )

            vector = response.embeddings[0].values

            if not vector:
                raise EmbeddingGenerationError(
                    "Gemini returned an empty embedding."
                )

            if len(vector) != self.dimension:
                raise EmbeddingGenerationError(
                    "Unexpected embedding dimension: "
                    f"expected {self.dimension}, received {len(vector)}."
                )

            return list(vector)

        except EmbeddingGenerationError:
            raise

        except Exception as exc:
            raise EmbeddingGenerationError(
                "Gemini embedding generation failed."
            ) from exc


    def generate_query_embedding(
        self,
        question: str,
    ) -> list[float]:
        """
        Generate an embedding for a semantic-search question.
        """

        if not question or not question.strip():
            raise EmbeddingGenerationError(
                "Search question cannot be empty."
            )

        prepared_question = self.prepare_query_text(
            question.strip()
        )

        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=prepared_question,
                config=types.EmbedContentConfig(
                    output_dimensionality=self.dimension,
                ),
            )

            if not response.embeddings:
                raise EmbeddingGenerationError(
                    "Gemini returned no query embedding."
                )

            vector = response.embeddings[0].values

            if not vector:
                raise EmbeddingGenerationError(
                    "Gemini returned an empty query embedding."
                )

            if len(vector) != self.dimension:
                raise EmbeddingGenerationError(
                    "Unexpected query embedding dimension: "
                    f"expected {self.dimension}, "
                    f"received {len(vector)}."
                )

            return [float(value) for value in vector]

        except EmbeddingGenerationError:
            raise

        except Exception as exc:
            raise EmbeddingGenerationError(
                "Query embedding generation failed."
            ) from exc