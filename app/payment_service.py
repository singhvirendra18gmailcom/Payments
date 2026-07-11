from functools import lru_cache

from app.services.ai_factory import get_ai_service
from app.services.payment_service import PaymentService


@lru_cache
def get_payment_service() -> PaymentService:
    return PaymentService(get_ai_service())

def answer_question(question: str):
    q = question.lower()

    if "mt103" in q:
        return "MT103 is used for international customer credit transfers over SWIFT."

    if "pacs.008" in q:
        return "pacs.008 is used in ISO 20022 for FI to FI customer credit transfer."

    if "pain.001" in q:
        return "pain.001 is used by customers or corporates to initiate payment instructions."

    if "camt.053" in q:
        return "camt.053 is an ISO 20022 account statement message."

    return "I can answer basic payment questions in Version 1. AI will be added in Version 2."

def explain_payment(message_type: str,content: str):
    message_type = message_type.upper()

    explanations = {
        "MT103": "MT103 is a SWIFT message used for customer credit transfer between banks.",
        "PACS.008": "pacs.008 is an ISO 20022 message used for FI to FI customer credit transfer.",
        "PAIN.001": "pain.001 is an ISO 20022 message used by a customer to initiate credit transfer instructions.",
        "CAMT.053": "camt.053 is an ISO 20022 bank statement message."
    }

    return explanations.get(
        message_type,
        "This payment message type is not available in Version 1."
    )

