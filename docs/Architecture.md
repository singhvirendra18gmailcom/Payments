# Architecture

AI Payment Assistant follows a small layered backend architecture. FastAPI owns the HTTP layer, SQLAlchemy owns persistence, and the service layer owns payment-domain and AI-provider behavior.

## Architecture Goals

- Keep HTTP route logic thin and readable.
- Keep AI provider code behind an interface.
- Keep tests deterministic by using a local AI provider.
- Make future providers such as OpenAI or Ollama easy to add.
- Return clean API errors for provider failures.

## System View

```text
Client
  |
  v
FastAPI app
  |
  +-- Request logging middleware
  +-- Configuration validation
  +-- API routes
  |
  +-- Auth layer
  |     +-- Password hashing
  |     +-- JWT creation
  |     +-- JWT validation
  |
  +-- Service layer
  |     +-- Payment service facade
  |     +-- PaymentService
  |     +-- AIService interface
  |     +-- AI provider factory
  |
  +-- AI providers
  |     +-- GeminiService
  |     +-- LocalAIService
  |
  +-- Persistence
        +-- SQLAlchemy
        +-- SQLite
```

## Runtime Layers

### HTTP Layer

Implemented in:

- `app/main.py`
- `app/schemas.py`

Responsibilities:

- Define routes.
- Validate request bodies through Pydantic schemas.
- Apply authentication dependencies.
- Convert service errors into HTTP responses.
- Log request and response metadata.

Important route groups:

- health routes
- auth routes
- payment routes
- chat routes
- document routes
- AI health routes

### Auth Layer

Implemented in:

- `app/auth.py`
- `app/models.py`
- `app/database.py`

Responsibilities:

- Hash user passwords.
- Verify login credentials.
- Create JWT access tokens.
- Decode JWT access tokens.
- Load the current authenticated user.
- Provide database sessions to route handlers.

### Service Layer

Implemented in:

- `app/payment_service.py`
- `app/services/payment_service.py`

Responsibilities:

- Keep route handlers simple.
- Build payment-domain AI prompts.
- Expose payment explanation and chat operations.
- Delegate AI calls to the configured provider.

There are two payment service files with different roles:

- `app/payment_service.py` is the endpoint-facing facade imported by `main.py`.
- `app/services/payment_service.py` is the business service that builds payment prompts and calls `AIService`.

### AI Provider Layer

Implemented in:

- `app/services/ai_service.py`
- `app/services/ai_factory.py`
- `app/services/gemini_service.py`
- `app/services/local_ai_service.py`

Responsibilities:

- Hide provider-specific implementation details.
- Provide a common interface for AI calls.
- Select the configured provider at runtime.
- Keep tests independent from external APIs.

## AI Service Interface

`AIService` defines the provider contract:

```text
ask(question) -> str
explain_payment(message_type, content) -> str
health_check() -> bool
```

Every provider must implement this interface.

Current implementations:

- `GeminiService`
- `LocalAIService`

## Provider Selection

Provider selection happens in `app/services/ai_factory.py`.

```text
AI_PROVIDER=local
  |
  v
LocalAIService
```

```text
AI_PROVIDER=gemini
GEMINI_API_KEY=<real key>
  |
  v
GeminiService
```

If `AI_PROVIDER=gemini` uses a placeholder API key, the factory falls back to `LocalAIService`.

## Request Flow

### `POST /chat/ask`

```text
Client
  |
  v
POST /chat/ask
  |
  v
JWT authentication
  |
  v
main.py chat_ask()
  |
  v
app/payment_service.py answer_question()
  |
  v
PaymentService.answer_payment_question()
  |
  v
AIService.ask()
  |
  +-- LocalAIService.ask()
  +-- GeminiService.ask()
```

### `POST /payments/explain`

```text
Client
  |
  v
POST /payments/explain
  |
  v
JWT authentication
  |
  v
main.py payment_explain()
  |
  v
app/payment_service.py explain_payment()
  |
  v
PaymentService.explain_payment_message()
  |
  v
AIService.ask()
```

### `GET /ai/health`

```text
Client
  |
  v
GET /ai/health
  |
  v
main.py ai_health()
  |
  v
get_ai_service()
  |
  v
AIService.health_check()
```

## Persistence Flow

```text
Route handler
  |
  v
get_db()
  |
  v
SQLAlchemy Session
  |
  v
SQLite database
```

The database is configured in `app/database.py`.

The current app creates tables on startup with:

```python
Base.metadata.create_all(bind=engine)
```

## Configuration Flow

```text
.env
  |
  v
app/config.py
  |
  v
app/main.py validate_configuration()
  |
  v
startup validation
```

Startup validation checks required values before the app begins serving requests.

Validated settings include:

- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `DATABASE_URL`
- `AI_PROVIDER`
- `GEMINI_API_KEY`
- `GEMINI_MODEL`

## Error Handling

Route handlers convert domain and provider errors into HTTP responses.

```text
ValueError
  |
  v
400 Bad Request
```

```text
AI provider failure
  |
  v
503 Service Unavailable
```

Gemini API quota failures, network failures, and provider exceptions are logged and returned as structured `503` responses.

Example:

```json
{
  "status": "error",
  "provider": "gemini",
  "message": "AI service is currently unavailable. Please try again later.",
  "error": "AI service is currently unavailable. Please try again later."
}
```

## Logging Flow

Request logging is implemented as FastAPI middleware in `app/main.py`.

```text
Incoming request
  |
  v
log method, path, client
  |
  v
route handler
  |
  v
log status code and duration
```

Logs are written to:

```text
logs/app.log
```

## Testing Architecture

Tests live in `tests/`.

Important files:

- `tests/conftest.py`
- `tests/test_auth.py`
- `tests/test_chat.py`
- `tests/test_gemini_service.py`
- `tests/test_health.py`
- `tests/test_login.py`
- `tests/test_payment.py`

`tests/conftest.py` sets:

```python
os.environ["AI_PROVIDER"] = "local"
```

This keeps tests deterministic and avoids real Gemini API calls.

Gemini service unit tests mock the Gemini client directly.

## Extension Points

### Add A New AI Provider

To add a provider such as OpenAI or Ollama:

1. Create a new service class under `app/services/`.
2. Implement the `AIService` interface.
3. Add provider configuration in `app/config.py`.
4. Update `get_ai_service()` in `app/services/ai_factory.py`.
5. Add provider validation in `app/main.py`.
6. Add unit tests for the provider.

### Add RAG

Likely future components:

- document parser
- embedding service
- vector database client
- retrieval service
- RAG prompt builder

These should sit behind service interfaces in `app/services/`.

## Current Constraints

- SQLite is used for local persistence.
- Gemini and local are the only implemented AI providers.
- Uploaded documents are stored but not yet used for RAG.
- FastAPI startup validation currently uses `on_event`; a lifespan handler is a future improvement.

## Related Docs

- [Home](Home.md)
- [Installation](Installation.md)
- [Project Overview](Project-Overview.md)
- [Roadmap](Roadmap.md)
