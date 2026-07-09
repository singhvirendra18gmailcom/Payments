# AI Payment Assistant Docs

AI Payment Assistant is a FastAPI backend for payment-domain question answering, payment message explanation, JWT authentication, document upload, and AI provider integration.

## Current Version

Version 2 is focused on the AI service layer.

Implemented:

- Gemini AI provider integration
- Local deterministic AI provider for tests and offline development
- AI chat and payment explanation APIs
- AI health check endpoint
- Request and response logging
- API failure handling for AI provider errors
- Startup configuration validation
- Unit tests for Gemini service and API health

## Quick Links

- [Project README](../README.md)
- [Project Overview](Project-Overview.md)
- [Installation](Installation.md)
- [Architecture](Architecture.md)
- [Authentication](Authentication.md)
- [AI Integration](AI-Integration.md)
- [Payment Service](Payment-Service.md)
- [Database Design](Database-Design.md)
- [API Documentation](API-Documentation.md)
- [Logging](Logging.md)
- [Testing](Testing.md)
- [Deployment](Deployment.md)
- [Release Notes](Release-Notes.md)
- [Roadmap](Roadmap.md)
- [Application Entry Point](../app/main.py)
- [AI Factory](../app/services/ai_factory.py)
- [Gemini Service](../app/services/gemini_service.py)
- [Local AI Service](../app/services/local_ai_service.py)
- [Payment Service](../app/services/payment_service.py)

## Main Capabilities

### Authentication

- Register users
- Login with email and password
- Issue JWT access tokens
- Protect APIs using bearer tokens

### Payment APIs

- Explain payment messages such as MT103, pacs.008, pain.001, and camt.053
- Answer payment-domain questions
- Use an AI-backed service abstraction for payment explanations

### AI Services

The app uses an `AIService` interface with provider implementations.

Current providers:

- `GeminiService`: Google Gemini API integration
- `LocalAIService`: deterministic local fallback for tests and offline development

Provider selection is controlled by:

```env
AI_PROVIDER=gemini
```

or:

```env
AI_PROVIDER=local
```

## Important Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Application health check |
| `GET` | `/ai/health` | AI provider health check |
| `POST` | `/auth/register` | Register a user |
| `POST` | `/auth/login` | Login and receive JWT |
| `GET` | `/auth/me` | Get current authenticated user |
| `POST` | `/chat/ask` | Ask a payment-domain question |
| `POST` | `/payments/explain` | Explain a payment message |
| `POST` | `/documents/upload` | Upload PDF, TXT, or DOCX documents |
| `GET` | `/documents` | List uploaded documents |

## Local Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://localhost:8000/docs
```

## Testing

Run all tests:

```bash
.venv\Scripts\python.exe -m pytest -q
```

Run AI-focused tests:

```bash
.venv\Scripts\python.exe -m pytest tests/test_gemini_service.py tests/test_health.py -q
```

Tests use `AI_PROVIDER=local` from `tests/conftest.py`, so they do not call external AI APIs.

## Logging

Application logs are written to:

```text
logs/app.log
```

The request middleware logs:

- request method
- request path
- client host
- response status code
- request duration
- stack traces for unexpected failures

## Configuration

Required configuration is loaded from environment variables through `app/config.py`.

Common settings:

```env
SECRET_KEY=my_super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./payment_assistant.db
AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash
```

For offline development:

```env
AI_PROVIDER=local
```

## Next Work

Likely next improvements:

- Add OpenAI provider support
- Add Ollama provider support
- Move startup validation to FastAPI lifespan handlers
- Add PostgreSQL support
- Add RAG and document question answering
- Add SWIFT and ISO 20022 parsers
