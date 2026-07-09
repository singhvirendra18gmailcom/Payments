# Project Overview

AI Payment Assistant is a FastAPI backend application for learning and demonstrating modern backend development with a payment systems use case. The application combines JWT authentication, payment-domain APIs, document upload, logging, testing, and AI provider integration.

## Purpose

The project is designed to answer two practical needs:

- Help users understand payment messages and payment concepts such as SWIFT MT, ISO 20022, MT103, pacs.008, pain.001, and camt messages.
- Provide a clean backend learning project that covers real API design, authentication, service layering, testing, logging, configuration, and AI integration.

## Current Version

The current implementation is Version 2.

Version 2 introduces the AI service layer:

- `AIService` abstraction
- `GeminiService` for Google Gemini integration
- `LocalAIService` for deterministic local and test behavior
- `PaymentService` for payment-domain prompt construction
- AI health checks
- API error handling for AI provider failures
- Configuration validation at startup

## High-Level Architecture

```text
Client
  |
  v
FastAPI app
  |
  +-- Auth endpoints
  +-- Payment endpoints
  +-- Chat endpoints
  +-- Document endpoints
  +-- Health endpoints
  |
  +-- Auth layer
  |     +-- JWT
  |     +-- Password hashing
  |     +-- Current user dependency
  |
  +-- Service layer
  |     +-- PaymentService
  |     +-- AIService interface
  |     +-- GeminiService
  |     +-- LocalAIService
  |
  +-- Persistence
        +-- SQLAlchemy
        +-- SQLite
```

## Main Modules

### `app/main.py`

Application entry point.

Responsibilities:

- Creates the FastAPI app
- Registers API routes
- Adds request and response logging middleware
- Runs startup configuration validation
- Handles AI provider failures
- Exposes health, auth, payment, chat, and document endpoints

### `app/config.py`

Loads environment configuration.

Important settings:

- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `DATABASE_URL`
- `AI_PROVIDER`
- `GEMINI_API_KEY`
- `GEMINI_MODEL`

### `app/auth.py`

Authentication and authorization helpers.

Responsibilities:

- Hash passwords
- Verify passwords
- Create JWT access tokens
- Decode JWT tokens
- Provide `get_current_user` dependency

### `app/database.py`

Database setup.

Responsibilities:

- Creates SQLAlchemy engine
- Creates session factory
- Provides database connection configuration

### `app/models.py`

SQLAlchemy database models.

Currently includes the user model used for registration, login, and authenticated routes.

### `app/schemas.py`

Pydantic request and response schemas.

Includes:

- `RegisterRequest`
- `LoginRequest`
- `TokenResponse`
- `PaymentExplainRequest`
- `ChatRequest`

### `app/payment_service.py`

Endpoint-facing payment service facade.

Responsibilities:

- Provides `explain_payment`
- Provides `answer_question`
- Connects FastAPI routes to the service layer

### `app/services/ai_service.py`

Abstract AI provider interface.

Every AI provider must implement:

- `ask`
- `explain_payment`
- `health_check`

### `app/services/ai_factory.py`

AI provider factory.

Responsibilities:

- Reads `AI_PROVIDER`
- Creates the correct AI service
- Uses `LocalAIService` when configured for local mode
- Uses `GeminiService` when configured for Gemini with a real API key

### `app/services/gemini_service.py`

Google Gemini implementation of `AIService`.

Responsibilities:

- Creates Gemini client
- Sends prompts to Gemini
- Handles empty responses
- Raises provider failures so API routes can return `503`
- Provides Gemini health check

### `app/services/local_ai_service.py`

Local deterministic implementation of `AIService`.

Responsibilities:

- Returns predictable answers for common payment questions
- Avoids external API calls during tests
- Supports offline local development

### `app/services/payment_service.py`

Payment-domain business service.

Responsibilities:

- Builds prompts for payment explanation
- Builds prompts for field explanation
- Builds prompts for message comparison
- Delegates AI calls to the configured `AIService`

## Request Flow

### Authenticated Chat Request

```text
POST /chat/ask
  |
  v
JWT authentication
  |
  v
main.py chat_ask
  |
  v
app/payment_service.py
  |
  v
PaymentService
  |
  v
AIService provider
  |
  +-- LocalAIService
  +-- GeminiService
```

### Payment Explanation Request

```text
POST /payments/explain
  |
  v
JWT authentication
  |
  v
main.py payment_explain
  |
  v
PaymentService.explain_payment_message
  |
  v
Configured AI provider
```

## API Groups

### Health

- `GET /health`
- `GET /ai/health`

### Authentication

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

### Chat

- `POST /chat/ask`
- `POST /chat/ask-ai`

### Payments

- `POST /payments/explain`
- `POST /payments/explain-ai`

### Documents

- `POST /documents/upload`
- `GET /documents`

## AI Provider Modes

### Gemini Mode

Use Gemini mode when a real Gemini API key is available.

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your_real_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash
```

Gemini quota failures or API failures are returned from API routes as `503 Service Unavailable`.

### Local Mode

Use local mode for tests, offline development, and demos.

```env
AI_PROVIDER=local
```

Local mode does not call external APIs.

## Testing Strategy

The test suite covers:

- Authentication
- Login
- Health checks
- Chat API
- Payment explanation API
- Gemini service behavior

Tests use `AI_PROVIDER=local` from `tests/conftest.py`, which keeps tests deterministic and prevents real API calls.

Run tests:

```bash
.venv\Scripts\python.exe -m pytest -q
```

Run AI-focused tests:

```bash
.venv\Scripts\python.exe -m pytest tests/test_gemini_service.py tests/test_health.py -q
```

## Logging And Error Handling

Logs are written to:

```text
logs/app.log
```

The app logs:

- request method
- request path
- client host
- response status code
- request duration
- provider errors
- unexpected exceptions

AI provider failures return a structured `503` response:

```json
{
  "status": "error",
  "provider": "gemini",
  "message": "AI service is currently unavailable. Please try again later.",
  "error": "AI service is currently unavailable. Please try again later."
}
```

## Configuration Validation

Startup validation checks the required configuration before serving requests.

Validation includes:

- required secret key
- supported JWT algorithm
- positive token expiry
- database URL
- supported AI provider
- Gemini key and model when Gemini is selected

## Current Limitations

- Only Gemini and local providers are implemented.
- OpenAI and Ollama are planned but not implemented.
- Document upload stores files but does not yet perform RAG or document question answering.
- SQLite is used locally; PostgreSQL is planned.
- Startup validation still uses FastAPI `on_event`; lifespan migration is planned.

## Related Docs

- [Home](Home.md)
- [Roadmap](Roadmap.md)
- [README](../README.md)
