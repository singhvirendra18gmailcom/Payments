from app.services.ai_service import AIService


class LocalAIService(AIService):
    """
    Deterministic fallback AI service for local development and tests.
    """

    def ask(self, question: str) -> str:
        q = question.lower().strip()

        if not q:
            raise ValueError("Question cannot be empty")

        if "mt103" in q:
            return "MT103 is used for international customer credit transfers over SWIFT."

        if "pacs.008" in q:
            return "pacs.008 is used in ISO 20022 for FI to FI customer credit transfer."

        if "pain.001" in q:
            return "pain.001 is used by customers or corporates to initiate payment instructions."

        if "camt.053" in q:
            return "camt.053 is an ISO 20022 account statement message."

        return "I can answer payment questions about SWIFT, ISO 20022, and payment flows."

    def explain_payment(self, message_type: str, content: str) -> str:
        message_type = message_type.upper().strip()

        explanations = {
            "MT103": "MT103 is a SWIFT message used for customer credit transfer between banks.",
            "PACS.008": "pacs.008 is an ISO 20022 message used for FI to FI customer credit transfer.",
            "PAIN.001": "pain.001 is an ISO 20022 message used by a customer to initiate credit transfer instructions.",
            "CAMT.053": "camt.053 is an ISO 20022 bank statement message.",
        }

        return explanations.get(
            message_type,
            f"{message_type} is not available in the local fallback knowledge base.",
        )

    def health_check(self) -> bool:
        return True
