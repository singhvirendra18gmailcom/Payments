# AI Integration

Version 2 adds an AI service layer with Google Gemini support and a deterministic local provider for tests and offline development.

## Files

- `app/services/ai_service.py`
- `app/services/ai_factory.py`
- `app/services/gemini_service.py`
- `app/services/local_ai_service.py`
- `app/services/payment_service.py`
- `app/payment_service.py`

## Service Contract

`AIService` defines the interface every AI provider must implement:

```text
ask(question) -> str
explain_payment(message_type, content) -> str
health_check() -> bool
```

## Providers

### GeminiService

`GeminiService` connects to Google Gemini using `google-genai`.

Responsibilities:

- create Gemini client
- send prompts
- return generated text
- raise provider failures for route-level `503` handling
- perform Gemini health checks

### LocalAIService

`LocalAIService` returns deterministic answers.

Use cases:

- tests
- offline development
- demos
- fallback when Gemini placeholder keys are configured

## Provider Selection

Provider selection happens in `app/services/ai_factory.py`.

```env
AI_PROVIDER=gemini
```

uses Gemini when a real API key is configured.

```env
AI_PROVIDER=local
```

uses the local deterministic provider.

## Gemini Configuration

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your_real_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash
```

## Local Configuration

```env
AI_PROVIDER=local
```

## AI Request Flow

```text
FastAPI route
  |
  v
app/payment_service.py
  |
  v
PaymentService
  |
  v
AIService
  |
  +-- GeminiService
  +-- LocalAIService
```

## AI Health

Endpoint:

```http
GET /ai/health
```

Healthy response:

```json
{
  "status": "healthy",
  "provider": "local",
  "available": true
}
```

## Error Handling

Provider errors are returned as `503 Service Unavailable`.

Example:

```json
{
  "status": "error",
  "provider": "gemini",
  "message": "AI service is currently unavailable. Please try again later.",
  "error": "AI service is currently unavailable. Please try again later."
}
```

Gemini quota failures such as `429 RESOURCE_EXHAUSTED` are logged and returned as `503`.

## Tests

Relevant tests:

- `tests/test_gemini_service.py`
- `tests/test_health.py`
- `tests/test_chat.py`
- `tests/test_payment.py`

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest .\tests\test_gemini_service.py .\tests\test_health.py -q
```

## Adding A New Provider

Steps:

1. Add provider config in `app/config.py`.
2. Create a provider class in `app/services/`.
3. Implement `AIService`.
4. Update `app/services/ai_factory.py`.
5. Update startup validation in `app/main.py`.
6. Add unit tests.

## Related Docs

- [Architecture](Architecture.md)
- [Payment Service](Payment-Service.md)
- [Testing](Testing.md)
