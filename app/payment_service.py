from functools import lru_cache

from app.services.ai_factory import get_ai_service
from app.services.payment_service import PaymentService


@lru_cache
def get_payment_service() -> PaymentService:
    return PaymentService(get_ai_service())


def explain_payment(message_type: str, content: str) -> str:
    return get_payment_service().explain_payment_message(message_type, content)


def answer_question(question: str) -> str:
    return get_payment_service().answer_payment_question(question)
