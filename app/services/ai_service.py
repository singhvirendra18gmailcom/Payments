from abc import ABC, abstractmethod


class AIService(ABC):
    """
    Abstract interface for all AI providers.

    Any AI provider (Gemini, OpenAI, Ollama, etc.)
    must implement this interface.
    """

    @abstractmethod
    def ask(self, question: str) -> str:
        """
        Ask a general question to the AI model.

        Args:
            question: User's question

        Returns:
            AI-generated response
        """
        pass

    @abstractmethod
    def explain_payment(self, message_type: str, content: str) -> str:
        """
        Explain a payment message.

        Args:
            message_type: MT103, PACS.008, MT202, etc.
            content: Payment message content

        Returns:
            AI-generated explanation
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Verify that the AI provider is reachable.

        Returns:
            True if healthy, otherwise False.
        """
        pass