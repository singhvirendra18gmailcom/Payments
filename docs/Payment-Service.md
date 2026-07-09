# Payment Service

The payment service layer owns payment-domain prompt construction and delegates AI calls to the configured provider.

## Files

- `app/payment_service.py`
- `app/services/payment_service.py`
- `app/services/ai_service.py`
- `app/services/ai_factory.py`

## Two Service Files

The project currently has two payment service files with different responsibilities.

### `app/payment_service.py`

Endpoint-facing facade imported by `app/main.py`.

Exports:

- `explain_payment`
- `answer_question`
- `get_payment_service`

### `app/services/payment_service.py`

Business service class.

Methods:

- `explain_payment_message`
- `explain_payment_field`
- `compare_messages`
- `answer_payment_question`

## Request Flow

```text
Route handler
  |
  v
app/payment_service.py
  |
  v
PaymentService
  |
  v
AIService.ask()
```

## Payment Explanation

Endpoint:

```http
POST /payments/explain
```

Request:

```json
{
  "message_type": "MT103",
  "content": "Explain MT103"
}
```

The service builds a prompt asking for:

- purpose
- business usage
- important fields
- message flow
- real-world example
- common validation errors

## Payment Chat

Endpoint:

```http
POST /chat/ask
```

Request:

```json
{
  "question": "What is MT103 used for?"
}
```

## Supported Knowledge Areas

The current prompt and local provider focus on:

- SWIFT MT messages
- MT103
- ISO 20022
- pacs.008
- pain.001
- camt.053
- payment flows
- validation errors

## Error Handling

The route layer handles:

- `ValueError` as `400 Bad Request`
- provider errors as `503 Service Unavailable`

## Local Provider Behavior

In local mode, common payment questions return deterministic answers.

This makes tests stable and avoids external API calls.

## Tests

Relevant tests:

- `tests/test_payment.py`
- `tests/test_chat.py`

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest .\tests\test_payment.py .\tests\test_chat.py -q
```

## Future Improvements

- Add SWIFT MT103 parser.
- Add ISO 20022 XML parser.
- Add structured field-level validation.
- Add RAG over uploaded documents.
- Add provider-independent prompt templates.

## Related Docs

- [AI Integration](AI-Integration.md)
- [API Documentation](API-Documentation.md)
- [Architecture](Architecture.md)
