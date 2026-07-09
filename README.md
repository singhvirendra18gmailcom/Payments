# AI Payment Assistant

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.139-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

AI Payment Assistant is a FastAPI backend for explaining payment messages, answering payment-domain questions, and practicing production-style backend engineering with authentication, testing, logging, Docker, and AI provider integration.

## Overview

This project is focused on:

- FastAPI REST API development
- JWT authentication
- SQLite and SQLAlchemy
- Payment domain knowledge such as SWIFT MT and ISO 20022
- AI-assisted payment explanations and chat
- Provider-based AI service design
- Request and response logging
- Configuration validation
- Unit testing with Pytest
- Docker and GitHub Actions

Version 2 adds a real AI service layer with Gemini support and a deterministic local AI provider for tests and local fallback behavior.

## Current Features

### Version 2

- User registration and login
- JWT-protected APIs
- Current user API: `/auth/me`
- Payment message explanation API
- Basic AI chat API
- Gemini AI provider integration
- Local deterministic AI provider for tests and offline development
- AI health check endpoint
- Request and response logging
- API failure handling for AI provider errors
- Startup configuration validation
- Document upload and document listing APIs
- SQLite database
- Environment variable support
- Unit tests using Pytest
- Docker support

## Technology Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.13 |
| Backend | FastAPI |
| Database | SQLite |
| ORM | SQLAlchemy |
| Authentication | JWT |
| Validation | Pydantic |
| AI Provider | Google Gemini |
| Local AI Fallback | LocalAIService |
| Testing | Pytest |
| Logging | Python logging |
| Containerization | Docker |
| Environment Management | python-dotenv |

## Architecture

```text
Client
  |
  v
FastAPI REST APIs
  |
  +-- JWT Authentication
  +-- Payment APIs
  +-- Chat APIs
  +-- Document APIs
  +-- AI Health API
  |
  +-- PaymentService
  |     |
  |     v
  |   AIService interface
  |     |
  |     +-- GeminiService
  |     +-- LocalAIService
  |
  v
SQLite Database
```

Future architecture may add OpenAI, Ollama, RAG, ChromaDB, PostgreSQL, and PDF/document intelligence.

## Project Structure

```text
ai-payment-assistant/
  app/
    __init__.py
    auth.py
    config.py
    database.py
    logger.py
    main.py
    models.py
    payment_service.py
    schemas.py
    services/
      __init__.py
      ai_factory.py
      ai_service.py
      gemini_service.py
      local_ai_service.py
      payment_service.py
    uploads/
  docs/
    AI-Integration.md
    API-Documentation.md
    Architecture.md
    Authentication.md
    Database-Design.md
    Deployment.md
    Home.md
    Installation.md
    Logging.md
    Payment-Service.md
    Project-Overview.md
    Release-Notes.md
    Roadmap.md
    Testing.md
  logs/
    app.log
  tests/
    __init__.py
    conftest.py
    test_auth.py
    test_chat.py
    test_gemini_service.py
    test_health.py
    test_login.py
    test_payment.py
    utils.py
  Dockerfile
  docker-compose.yml
  requirements.txt
  README.md
```

## Documentation

The detailed project documentation lives under `docs/`.

Start here:

- [Docs Home](docs/Home.md)
- [Project Overview](docs/Project-Overview.md)
- [Installation](docs/Installation.md)
- [Architecture](docs/Architecture.md)
- [API Documentation](docs/API-Documentation.md)

Topic guides:

- [Authentication](docs/Authentication.md)
- [AI Integration](docs/AI-Integration.md)
- [Payment Service](docs/Payment-Service.md)
- [Database Design](docs/Database-Design.md)
- [Logging](docs/Logging.md)
- [Testing](docs/Testing.md)
- [Deployment](docs/Deployment.md)
- [Release Notes](docs/Release-Notes.md)
- [Roadmap](docs/Roadmap.md)

## Prerequisites

- Python 3.13+
- Git
- Docker Desktop, optional
- VS Code or PyCharm
- Gemini API key, required only when using `AI_PROVIDER=gemini`

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/ai-payment-assistant.git
cd ai-payment-assistant
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux or macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file:

```bash
cp .env.example .env
```

Supported settings:

```env
SECRET_KEY=my_super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./payment_assistant.db

AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash
```

For offline/local development without calling Gemini:

```env
AI_PROVIDER=local
```

Tests force `AI_PROVIDER=local` through `tests/conftest.py`, so they do not call external AI APIs.

## Configuration Validation

The app validates configuration on startup.

It checks:

- `SECRET_KEY` is present
- `ALGORITHM` is supported
- `ACCESS_TOKEN_EXPIRE_MINUTES` is greater than 0
- `DATABASE_URL` is present
- `AI_PROVIDER` is supported
- `GEMINI_API_KEY` and `GEMINI_MODEL` are present when `AI_PROVIDER=gemini`

Supported providers today:

```text
gemini
local
```

## Running Locally

Start the application:

```bash
uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://localhost:8000/docs
```

Open the health endpoints:

```text
http://localhost:8000/health
http://localhost:8000/ai/health
```

## Running Tests

Use the project virtual environment:

```bash
.venv\Scripts\python.exe -m pytest -q
```

Run a focused test file:

```bash
.venv\Scripts\python.exe -m pytest tests/test_gemini_service.py -q
```

Run coverage:

```bash
.venv\Scripts\python.exe -m pytest --cov=app
```

## Running with Docker

Build the image:

```bash
docker compose build
```

Start the application:

```bash
docker compose up
```

Open:

```text
http://localhost:8000/docs
```

Stop containers:

```bash
docker compose down
```

## API Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/health` | No | Application health check |
| GET | `/ai/health` | No | AI provider health check |
| POST | `/auth/register` | No | Register a new user |
| POST | `/auth/login` | No | Login and get JWT token |
| GET | `/auth/me` | Yes | Get current user |
| POST | `/payments/explain` | Yes | Explain payment messages |
| POST | `/chat/ask` | Yes | Ask payment-related questions |
| POST | `/documents/upload` | Yes | Upload PDF, TXT, or DOCX documents |
| GET | `/documents` | Yes | List uploaded documents |
| POST | `/chat/ask-ai` | No | Direct AI chat endpoint |
| POST | `/payments/explain-ai` | No | Direct AI payment explanation endpoint |

## Example API Requests

### Register User

```http
POST /auth/register
```

```json
{
  "name": "Virendra Singh",
  "email": "virendra@test.com",
  "password": "password123"
}
```

### Login

```http
POST /auth/login
```

```json
{
  "email": "virendra@test.com",
  "password": "password123"
}
```

Response:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

### Ask A Payment Question

```http
POST /chat/ask
Authorization: Bearer <jwt-token>
```

```json
{
  "question": "What is MT103 used for?"
}
```

### Explain Payment Message

```http
POST /payments/explain
Authorization: Bearer <jwt-token>
```

```json
{
  "message_type": "MT103",
  "content": "Explain MT103"
}
```

### AI Health

```http
GET /ai/health
```

Healthy response:

```json
{
  "status": "healthy",
  "provider": "gemini",
  "available": true
}
```

Unhealthy response:

```json
{
  "status": "unhealthy",
  "provider": "gemini",
  "available": false,
  "error": "AI service is currently unavailable. Please try again later."
}
```

## AI Provider Behavior

`GeminiService` is used when:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=<real key>
```

`LocalAIService` is used when:

```env
AI_PROVIDER=local
```

The local provider returns deterministic payment-domain answers and is intended for tests, demos, and offline development.

Gemini quota or provider failures are logged and returned from API endpoints as `503 Service Unavailable`.

## Logging

The app logs to:

```text
logs/app.log
```

Request and response logging includes:

- HTTP method
- request path
- client host
- response status code
- request duration
- stack traces for unexpected failures

## Error Handling

AI endpoints handle:

- invalid input as `400 Bad Request`
- provider/API failures as `503 Service Unavailable`
- successful provider responses as `200 OK`

Example provider failure:

```json
{
  "status": "error",
  "provider": "gemini",
  "message": "AI service is currently unavailable. Please try again later.",
  "error": "AI service is currently unavailable. Please try again later."
}
```

## GitHub Actions

The project is intended to run tests in CI with GitHub Actions.

Typical workflow:

```text
Push
  |
  v
GitHub Actions
  |
  +-- Install dependencies
  +-- Run unit tests
  +-- Verify build
```

## Roadmap

### Version 1.0

- FastAPI APIs
- JWT authentication
- SQLite database
- Unit tests

### Version 1.1

- Environment variables
- Logging
- Docker support
- GitHub Actions
- Improved documentation

### Version 2.0

- Gemini AI integration
- AI service abstraction
- Local AI fallback provider
- AI health endpoint
- AI API failure handling
- Configuration validation
- Gemini unit tests

### Version 3.0

- OpenAI and Ollama provider support
- PostgreSQL
- Better prompt engineering
- RAG foundation

### Version 4.0

- ChromaDB
- PDF processing
- Document intelligence
- SWIFT MT103 parser
- ISO 20022 parsing support

### Version 5.0

- Kubernetes deployment
- Cloud hosting
- Enterprise CI/CD

## Learning Goals

This project helps practice:

- FastAPI
- SQLAlchemy
- JWT authentication
- Unit testing
- Docker
- GitHub Actions
- Git workflows
- AI engineering
- Payment systems
- RAG systems
- Kubernetes

## Contributing

Recommended workflow:

1. Fork the repository
2. Create a feature branch
3. Write tests
4. Follow Conventional Commits
5. Open a Pull Request

Example:

```bash
git checkout -b feature/add-openai-support
```

Commit examples:

```bash
feat(auth): add JWT authentication
feat(ai): add Gemini provider
test(ai): add Gemini service tests
docs(readme): update Version 2 documentation
fix(ai): return 503 on provider failures
```

## License

This project is licensed under the MIT License.

## Author

**Virendra Singh**

Building an AI-powered payment assistant while learning FastAPI, AI engineering, payment systems, Docker, Kubernetes, and modern backend development.
