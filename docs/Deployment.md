# Deployment

This document describes the current deployment options for AI Payment Assistant.

## Current Deployment Style

The project supports:

- local development with Uvicorn
- Docker image build
- Docker Compose startup

Production deployment is planned for future versions.

## Local Run

Start the app directly:

```powershell
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000/docs
```

## Dockerfile

The Docker image uses:

```text
python:3.13-slim
```

Startup command:

```text
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Docker Compose

Build:

```powershell
docker compose build
```

Run:

```powershell
docker compose up
```

Stop:

```powershell
docker compose down
```

The app is exposed on:

```text
http://localhost:8000
```

## Environment Variables

Docker Compose reads:

```text
.env
```

Required settings:

```env
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./payment_assistant.db
AI_PROVIDER=local
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash
```

For Gemini:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your_real_gemini_api_key
```

## Health Checks

Use these endpoints after deployment:

```text
GET /health
GET /ai/health
```

## Logs

Logs are written inside the container to:

```text
logs/app.log
```

Docker Compose also streams application logs to the console.

## Current Limitations

- No production WSGI/ASGI process manager configuration.
- No Kubernetes manifests yet.
- No PostgreSQL deployment configuration yet.
- No secret manager integration.
- No CI/CD deployment workflow yet.
- Docker Compose mounts the project directory into `/app`, which is convenient for development but not ideal for production.

## Production Checklist

Before production deployment:

- use a strong `SECRET_KEY`
- use PostgreSQL instead of SQLite
- add database migrations
- configure secrets outside source control
- use a production-grade container image strategy
- add log rotation or centralized logging
- add HTTPS through a reverse proxy or platform
- add monitoring and alerting
- configure Gemini quota and billing

## Related Docs

- [Installation](Installation.md)
- [Logging](Logging.md)
- [Database Design](Database-Design.md)
