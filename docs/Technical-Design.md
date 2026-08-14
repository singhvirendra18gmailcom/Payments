# Technical Design Document

## 1. Overview

AI Payment Assistant is a FastAPI backend for payment-domain question answering, payment message explanation, JWT-secured user access, document upload, and AI-provider integration.

The current runtime version exposed by FastAPI is `3.0.0`.

The application is intentionally small and layered:

- FastAPI handles HTTP routing, request validation, dependency injection, and API responses.
- SQLAlchemy handles relational persistence.
- Auth helpers handle password hashing, JWT creation, and current-user lookup.
- Payment services hold payment-domain behavior.
- AI services hide provider-specific Gemini or local deterministic behavior behind an interface.
- Tests use a local AI mode to avoid external network calls.

## 2. Goals

- Provide API endpoints for authentication, payment explanation, chat, document upload, and health checks.
- Keep AI provider details isolated behind a stable `AIService` contract.
- Support deterministic local behavior for tests and offline development.
- Keep request logging and AI error responses consistent.
- Preserve a path for future RAG, document indexing, additional AI providers, and production database support.

## 3. Non-Goals

- The current system does not parse SWIFT or ISO 20022 messages into structured fields.
- Uploaded documents are stored on disk but are not indexed or used for retrieval-augmented generation.
- There is no Alembic migration layer yet.
- There is no production-grade PostgreSQL, secret manager, rate limiter, or centralized logging integration.
- There is no frontend implementation in this repository.

## 4. System Context

```text
API Client
  |
  v
FastAPI Application
  |
  +-- Authentication and JWT authorization
  +-- Payment explanation and chat routes
  +-- Document upload and listing routes
  +-- Health and AI health routes
  |
  +-- SQLAlchemy + SQLite
  |
  +-- AIService interface
        |
        +-- LocalAIService
        +-- GeminiService
```

## 5. Runtime Architecture

```text
app/main.py
  |
  +-- app/schemas.py
  +-- app/auth.py
  |     +-- app/database.py
  |     +-- app/models.py
  |
  +-- app/payment_service.py
  |
  +-- app/services/payment_service.py
        |
        +-- app/services/ai_factory.py
              |
              +-- app/services/local_ai_service.py
              +-- app/services/gemini_service.py
              +-- app/services/ai_service.py
```

### 5.1 HTTP Layer

File: `app/main.py`

Responsibilities:

- Creates the FastAPI app.
- Exposes API route groups for health, authentication, chat, payments, documents, and AI health.
- Creates database tables through `Base.metadata.create_all(bind=engine)`.
- Creates `app/uploads` at startup/import time.
- Runs startup configuration validation.
- Logs every request and response through middleware.
- Converts `ValueError` into `400` responses in route handlers.
- Converts AI/provider exceptions into structured `503` JSON responses.

### 5.2 Schema Layer

File: `app/schemas.py`

Pydantic schemas:

| Schema | Purpose |
|--------|---------|
| `RegisterRequest` | User registration body with name, email, and password |
| `LoginRequest` | JSON login body, currently defined but not used by `/auth/login` |
| `TokenResponse` | Bearer token response |
| `PaymentExplainRequest` | Payment explanation input |
| `ChatRequest` | Chat question input |

`/auth/login` uses FastAPI's `OAuth2PasswordRequestForm`, so clients must submit form fields named `username` and `password`.

### 5.3 Authentication Layer

Files:

- `app/auth.py`
- `app/models.py`
- `app/database.py`

Responsibilities:

- Create request-scoped SQLAlchemy sessions through `get_db()`.
- Hash passwords with Passlib using Argon2.
- Verify submitted passwords.
- Create JWT access tokens with an expiry claim.
- Decode bearer tokens and load the current user.
- Reject missing, invalid, expired, or userless tokens with `401`.

Authentication flow:

```text
POST /auth/register
  |
  v
Check duplicate email
  |
  v
Hash password with Argon2
  |
  v
Insert users row
```

```text
POST /auth/login
  |
  v
Find user by form_data.username
  |
  v
Verify password
  |
  v
Return JWT bearer token
```

```text
Protected endpoint
  |
  v
OAuth2PasswordBearer extracts token
  |
  v
jwt.decode()
  |
  v
Read email from sub claim
  |
  v
Load user from database
```

### 5.4 Persistence Layer

Files:

- `app/database.py`
- `app/models.py`

Configured by:

```env
DATABASE_URL=sqlite:///./payment_assistant.db
```

Current database setup:

- SQLAlchemy engine created from `DATABASE_URL`.
- SQLite uses `connect_args={"check_same_thread": False}` for FastAPI request compatibility.
- `SessionLocal` creates ORM sessions.
- Tables are created automatically through `Base.metadata.create_all(bind=engine)`.

Current table:

| Table | Column | Type | Notes |
|-------|--------|------|-------|
| `users` | `id` | Integer | Primary key, indexed |
| `users` | `name` | String | Required |
| `users` | `email` | String | Required, unique, indexed |
| `users` | `hashed_password` | String | Required |
| `users` | `created_at` | DateTime | Defaults to UTC timestamp |

### 5.5 Payment Service Layer

There are two payment service modules with different current responsibilities.

File: `app/payment_service.py`

This is the route-facing compatibility module imported by `app/main.py` for:

- `/payments/explain`
- `/chat/ask`

Current behavior:

- `answer_question(question)` returns hard-coded local answers for `MT103`, `pacs.008`, `pain.001`, and `camt.053`.
- `explain_payment(message_type, content)` returns hard-coded local explanations for supported message types.
- `get_payment_service()` exists and returns `PaymentService(get_ai_service())`, but the two current route-facing functions do not call it.

File: `app/services/payment_service.py`

This is the newer AI-backed business service. It accepts an `AIService` instance and builds prompts for:

- full payment message explanation
- field-level explanation
- message comparison
- general payment question answering

Current direct route usage:

- `/payments/explain-ai` creates `PaymentService(get_ai_service())` and calls `explain_payment_message()`.

Design implication:

- The project currently supports both deterministic legacy endpoints and direct AI-backed endpoints.
- A future cleanup should decide whether `/payments/explain` and `/chat/ask` should remain deterministic or delegate to `PaymentService`.

### 5.6 AI Provider Layer

Files:

- `app/services/ai_service.py`
- `app/services/ai_factory.py`
- `app/services/local_ai_service.py`
- `app/services/gemini_service.py`

`AIService` defines this provider contract:

```text
ask(question: str) -> str
explain_payment(message_type: str, content: str) -> str
health_check() -> bool
```

Provider selection:

```text
AI_PROVIDER=local
  -> LocalAIService
```

```text
AI_PROVIDER=gemini and GEMINI_API_KEY is a placeholder
  -> LocalAIService
```

```text
AI_PROVIDER=gemini and GEMINI_API_KEY is real
  -> GeminiService
```

`get_ai_service()` is cached with `lru_cache`, so the selected provider is reused after first construction.

`LocalAIService`:

- Performs deterministic, offline answers.
- Validates empty questions.
- Returns `True` for health checks.
- Supports known payment concepts through fixed string responses.

`GeminiService`:

- Uses `google-genai`.
- Creates `genai.Client(api_key=GEMINI_API_KEY)`.
- Sends prompts with a payment-domain system instruction.
- Returns fallback text if Gemini returns no text.
- Raises a runtime unavailable error if the provider call fails.
- Implements health check by asking the model to return `OK`.

## 6. API Design

### 6.1 Health

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/health` | No | Application health |
| `GET` | `/ai/health` | No | Configured AI provider health |

### 6.2 Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/register` | No | Register user |
| `POST` | `/auth/login` | No | Login with OAuth2 form data |
| `GET` | `/auth/me` | Bearer token | Return current user profile |

### 6.3 Payments

| Method | Endpoint | Auth | Implementation |
|--------|----------|------|----------------|
| `POST` | `/payments/explain` | Bearer token | Hard-coded route-facing payment facade |
| `POST` | `/payments/explain-ai` | No | AI-backed `PaymentService` |

### 6.4 Chat

| Method | Endpoint | Auth | Implementation |
|--------|----------|------|----------------|
| `POST` | `/chat/ask` | Bearer token | Hard-coded route-facing payment facade |
| `POST` | `/chat/ask-ai` | No | Direct configured AI service |

### 6.5 Documents

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/documents/upload` | Bearer token | Upload `.pdf`, `.txt`, or `.docx` file |
| `GET` | `/documents` | Bearer token | List uploaded files |

Documents are stored under:

```text
app/uploads
```

## 7. Key Request Flows

### 7.1 Protected Payment Explanation

```text
Client
  |
  v
POST /payments/explain
  |
  v
get_current_user()
  |
  v
payment_explain()
  |
  v
app.payment_service.explain_payment()
  |
  v
Return deterministic explanation
```

### 7.2 AI Payment Explanation

```text
Client
  |
  v
POST /payments/explain-ai
  |
  v
explain_payment_ai()
  |
  v
get_ai_service()
  |
  v
PaymentService.explain_payment_message()
  |
  v
AIService.ask()
  |
  +-- LocalAIService.ask()
  +-- GeminiService.ask()
```

### 7.3 Login And Authenticated User Lookup

```text
Client
  |
  v
POST /auth/login
  |
  v
OAuth2PasswordRequestForm(username, password)
  |
  v
Verify password hash
  |
  v
Return bearer token
  |
  v
Protected route uses Authorization: Bearer <token>
  |
  v
Decode JWT sub claim
  |
  v
Load User by email
```

### 7.4 Document Upload

```text
Client
  |
  v
POST /documents/upload
  |
  v
get_current_user()
  |
  v
Validate extension
  |
  v
Write file to app/uploads/<filename>
  |
  v
Return filename and uploaded status
```

## 8. Configuration Design

Configuration is loaded from `.env` by `python-dotenv` in `app/config.py`.

| Variable | Default | Purpose |
|----------|---------|---------|
| `SECRET_KEY` | `test_secret_key_for_local_and_ci` | JWT signing key |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | JWT expiry window |
| `DATABASE_URL` | `sqlite:///./payment_assistant.db` | SQLAlchemy database URL |
| `AI_PROVIDER` | `gemini` | AI provider selector |
| `GEMINI_API_KEY` | `test_api_key_for_local_and_ci` | Gemini API key |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name |

Startup validation in `app/main.py` checks:

- non-empty `SECRET_KEY`
- supported `ALGORITHM`
- positive token expiry
- non-empty `DATABASE_URL`
- supported `AI_PROVIDER`
- required Gemini model and key when `AI_PROVIDER=gemini`
- warning when Gemini key is a known placeholder

## 9. Error Handling

Route behavior:

| Error Type | HTTP Response |
|------------|---------------|
| Duplicate registration email | `400` |
| Invalid login credentials | `401` |
| Missing or invalid bearer token | `401` |
| Validation `ValueError` in route handler | `400` |
| AI provider failure | `503` |

AI unavailable response shape:

```json
{
  "status": "error",
  "provider": "gemini",
  "message": "AI service is currently unavailable. Please try again later.",
  "error": "AI service is currently unavailable. Please try again later."
}
```

## 10. Logging Design

File: `app/logger.py`

Logs are written to:

```text
logs/app.log
```

Log outputs:

- file handler
- stream handler

Request middleware logs:

- request method
- request path
- client host
- response status code
- request duration in milliseconds
- exception stack traces for failed requests

Provider code logs:

- selected Gemini model
- Gemini initialization metadata
- Gemini API exceptions
- Gemini health check failures

Security note:

- `GeminiService` currently logs the first eight characters of the API key. This is useful for debugging, but should be removed or guarded before production use.

## 11. Security Design

Implemented controls:

- Password hashing uses Argon2 through Passlib.
- JWT access tokens include expiry.
- Protected endpoints use OAuth2 bearer-token dependency.
- Duplicate email registration is blocked.
- Startup configuration validation prevents empty core settings.

Current risks and gaps:

- Default development `SECRET_KEY` should not be used outside local or CI.
- Some AI routes are not authenticated: `/chat/ask-ai`, `/payments/explain-ai`, and `/ai/health`.
- Uploaded filenames are used directly in the destination path, so filename sanitization should be added.
- Uploaded file content is not scanned or size-limited.
- There is no rate limiting for login, chat, uploads, or AI endpoints.
- There is no refresh-token flow or token revocation.
- There is no role-based authorization.

## 12. Testing Design

Test files:

- `tests/conftest.py`
- `tests/test_auth.py`
- `tests/test_login.py`
- `tests/test_health.py`
- `tests/test_chat.py`
- `tests/test_payment.py`
- `tests/test_gemini_service.py`
- `tests/utils.py`

Testing strategy:

- API tests use `TestClient`.
- Helper functions register and login unique test users.
- `tests/conftest.py` sets `AI_PROVIDER=local`.
- Local AI mode keeps tests deterministic.
- Gemini service tests mock `genai.Client` and model responses.

Coverage areas:

- registration
- login
- protected endpoint authentication
- health checks
- deterministic chat response
- payment explanation response
- Gemini initialization, validation, empty response behavior, error handling, and health checks

Recommended additional tests:

- `/auth/me` success and failure cases
- unsupported payment message behavior
- empty chat and empty payment content validation
- document upload extension validation
- document listing authorization
- `/chat/ask-ai` and `/payments/explain-ai` route behavior
- AI factory provider-selection behavior
- startup configuration validation

## 13. Deployment Design

Supported modes:

- local Uvicorn
- Docker image
- Docker Compose

Dockerfile:

- base image: `python:3.13-slim`
- working directory: `/app`
- installs `requirements.txt`
- starts Uvicorn on `0.0.0.0:8000`

Docker Compose:

- builds the local image
- exposes port `8000:8000`
- reads `.env`
- mounts project source into `/app`
- restarts unless stopped

Production gaps:

- no production process tuning
- no PostgreSQL service
- no migration command
- no secret manager
- no centralized logs
- no healthcheck stanza in Docker Compose
- source mount is development-friendly but not production-oriented

## 14. Design Decisions

| Decision | Rationale | Tradeoff |
|----------|-----------|----------|
| FastAPI | Simple API layer, automatic validation and Swagger docs | Route file can grow without routers |
| SQLAlchemy ORM | Familiar persistence layer | No migrations yet |
| SQLite default | Easy local setup | Not suitable for concurrent production workloads |
| Argon2 password hashing | Strong password hashing algorithm | Requires native crypto dependencies |
| JWT bearer auth | Stateless protected endpoint access | No revocation model yet |
| AIService abstraction | Provider-agnostic service design | Factory and validation must be updated for each provider |
| Local AI provider | Deterministic tests and offline demos | Limited knowledge base |
| Gemini provider | Real AI responses for payment explanations | External API, quota, latency, and key management required |
| Disk document storage | Simple upload implementation | No metadata, scanning, indexing, or RAG |

## 15. Known Implementation Gaps

- Existing docs still describe Version 2 in several places, while FastAPI now exposes Version 3.0.0.
- `app/payment_service.py` still returns Version 1 style deterministic responses and does not delegate `answer_question()` or `explain_payment()` to the AI-backed `PaymentService`.
- `LoginRequest` exists but `/auth/login` uses `OAuth2PasswordRequestForm`.
- `tags_metadata` is declared but not passed to `FastAPI(openapi_tags=...)`.
- `/chat/ask-ai` and `/payments/explain-ai` are public, unlike `/chat/ask` and `/payments/explain`.
- `app/uploads` and `logs` are runtime directories and are currently untracked or locally generated.
- The SQLite database file is local runtime state.
- File uploads need path traversal protection, size limits, duplicate filename handling, and malware scanning before production use.
- Database table creation should move from `create_all()` to migrations for production.

## 16. Recommended Next Design Work

1. Decide the Version 3 API contract:
   - keep deterministic protected endpoints as compatibility routes, or
   - migrate `/chat/ask` and `/payments/explain` to the AI-backed service layer.
2. Split `app/main.py` into routers:
   - `auth`
   - `health`
   - `payments`
   - `chat`
   - `documents`
3. Add Alembic migrations.
4. Add upload safety controls:
   - safe filename handling
   - file size limit
   - duplicate handling
   - content-type validation
5. Add document metadata persistence and RAG design:
   - parser service
   - chunking service
   - embedding provider
   - vector store
   - retrieval service
6. Add provider-independent prompt templates.
7. Add authenticated access and rate limiting for AI endpoints.
8. Add production configuration guidance for PostgreSQL, secrets, logs, and deployment health checks.

