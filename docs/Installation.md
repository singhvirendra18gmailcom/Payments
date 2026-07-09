# Installation

This guide explains how to set up AI Payment Assistant locally for development, testing, and optional Docker usage.

## Prerequisites

Install:

- Python 3.13+
- Git
- Docker Desktop, optional
- PyCharm or VS Code

For Gemini mode, you also need a Gemini API key from Google AI Studio.

## Clone The Project

```bash
git clone https://github.com/YOUR_USERNAME/ai-payment-assistant.git
cd ai-payment-assistant
```

If you already have the project locally, open the project root:

```powershell
cd C:\Users\PC\PycharmProjects\ai-payment-assistant
```

## Create Virtual Environment

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\activate
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

## Install Dependencies

```powershell
pip install -r requirements.txt
```

To verify Pytest is available:

```powershell
.\.venv\Scripts\python.exe -m pytest --version
```

## Configure Environment Variables

Create a `.env` file from the example:

```powershell
Copy-Item .env.example .env
```

Linux or macOS:

```bash
cp .env.example .env
```

## Local AI Mode

Use local mode when you do not want to call Gemini.

Set this in `.env`:

```env
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./payment_assistant.db

AI_PROVIDER=local
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash
```

Local mode uses `LocalAIService`, which returns deterministic payment-domain answers and does not call external APIs.

## Gemini AI Mode

Use Gemini mode when you have a real Gemini API key.

Set this in `.env`:

```env
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./payment_assistant.db

AI_PROVIDER=gemini
GEMINI_API_KEY=your_real_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash
```

If Gemini quota is exhausted, AI endpoints return `503 Service Unavailable`.

## Run The Application

Start the API:

```powershell
uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://localhost:8000/docs
```

Health checks:

```text
http://localhost:8000/health
http://localhost:8000/ai/health
```

## Run Tests

Run all tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Run AI-focused tests:

```powershell
.\.venv\Scripts\python.exe -m pytest .\tests\test_gemini_service.py .\tests\test_health.py -q
```

Run chat and payment tests:

```powershell
.\.venv\Scripts\python.exe -m pytest .\tests\test_chat.py .\tests\test_payment.py -q
```

Tests use `AI_PROVIDER=local` from `tests/conftest.py`, so they do not call Gemini.

## Run With Docker

Build the image:

```powershell
docker compose build
```

Start the application:

```powershell
docker compose up
```

Stop the application:

```powershell
docker compose down
```

Open Swagger UI:

```text
http://localhost:8000/docs
```

## Verify The Setup

After startup, check:

```text
GET /health
```

Expected response:

```json
{
  "status": "ok",
  "app": "AI Payment Assistant"
}
```

Check AI health:

```text
GET /ai/health
```

Expected local-mode response:

```json
{
  "status": "healthy",
  "provider": "local",
  "available": true
}
```

## Common Issues

### `No module named pytest`

Use the project virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

### `No module named dotenv`

Install dependencies into the active environment:

```powershell
pip install -r requirements.txt
```

### Gemini `429 RESOURCE_EXHAUSTED`

The Gemini API quota is exhausted. Options:

- wait for quota reset
- use a quota-enabled API key
- switch to `AI_PROVIDER=local`
- change model if your account supports another Gemini model

### Startup Configuration Error

The app validates required configuration during startup. Check these values:

- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `DATABASE_URL`
- `AI_PROVIDER`
- `GEMINI_API_KEY`
- `GEMINI_MODEL`

## Related Docs

- [Home](Home.md)
- [Project Overview](Project-Overview.md)
- [Roadmap](Roadmap.md)
