from app.services.ai_service import AIService


class PaymentService:
    """
    Business service for payment-related operations.
    """

    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    def explain_payment_message(
        self,
        message_type: str,
        content: str
    ) -> str:
        """
        Explain a payment message.
        """

        prompt = f"""
You are a senior payment systems expert.

Explain the following payment message.

Message Type:
{message_type}

Message Content:
{content}

Please provide:

1. Purpose
2. Business Usage
3. Important Fields
4. Message Flow
5. Real-world Example
6. Common Validation Errors
"""

        return self.ai_service.ask(prompt)

    def explain_payment_field(
        self,
        message_type: str,
        field_name: str
    ) -> str:
        """
        Explain a specific payment field.
        """

        prompt = f"""
Explain field {field_name}
for message type {message_type}.

Include:

- Purpose
- Format
- Validation Rules
- Example
"""

        return self.ai_service.ask(prompt)

    def compare_messages(
        self,
        first_message: str,
        second_message: str
    ) -> str:
        """
        Compare two payment message types.
        """

        prompt = f"""
Compare the following payment messages.

Message 1:
{first_message}

Message 2:
{second_message}

Explain:

- Purpose
- Similarities
- Differences
- Typical Usage
- Example
"""

        return self.ai_service.ask(prompt)

    def answer_payment_question(
        self,
        question: str
    ) -> str:
        """
        Ask any payment-related question.
        """

        return self.ai_service.ask(question)