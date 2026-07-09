# API Documentation

This document lists the current API endpoints in AI Payment Assistant.

Interactive documentation is available at:

```text
http://localhost:8000/docs
```

## Health

### `GET /health`

Returns application health.

Response:

```json
{
  "status": "ok",
  "app": "AI Payment Assistant"
}
```

### `GET /ai/health`

Returns configured AI provider health.

Response:

```json
{
  "status": "healthy",
  "provider": "local",
  "available": true
}
```

## Authentication

### `POST /auth/register`

Registers a new user.

Request:

```json
{
  "name": "Virendra Singh",
  "email": "virendra@test.com",
  "password": "password123"
}
```

Response:

```json
{
  "message": "User registered successfully",
  "email": "virendra@test.com"
}
```

### `POST /auth/login`

Logs in a user and returns a bearer token.

Request:

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

### `GET /auth/me`

Requires:

```text
Authorization: Bearer <jwt-token>
```

Response:

```json
{
  "name": "Virendra Singh",
  "email": "virendra@test.com"
}
```

## Chat

### `POST /chat/ask`

Protected endpoint for payment-domain chat.

Request:

```json
{
  "question": "What is MT103 used for?"
}
```

Response:

```json
{
  "question": "What is MT103 used for?",
  "answer": "MT103 is used for international customer credit transfers over SWIFT."
}
```

### `POST /chat/ask-ai`

Direct AI chat endpoint.

Request:

```json
{
  "question": "Explain pacs.008"
}
```

## Payments

### `POST /payments/explain`

Protected endpoint for payment message explanation.

Request:

```json
{
  "message_type": "MT103",
  "content": "Explain MT103"
}
```

Response:

```json
{
  "message_type": "MT103",
  "explanation": "..."
}
```

### `POST /payments/explain-ai`

Direct AI payment explanation endpoint.

Request:

```json
{
  "message_type": "pacs.008",
  "content": "Explain this payment message"
}
```

## Documents

### `POST /documents/upload`

Protected endpoint for uploading documents.

Allowed extensions:

- `.pdf`
- `.txt`
- `.docx`

Form field:

```text
file
```

Response:

```json
{
  "filename": "example.pdf",
  "status": "uploaded"
}
```

### `GET /documents`

Protected endpoint for listing uploaded documents.

Response:

```json
[
  {
    "filename": "example.pdf",
    "type": "pdf"
  }
]
```

## Error Responses

### Auth Error

```json
{
  "detail": "Invalid token"
}
```

### AI Provider Error

```json
{
  "status": "error",
  "provider": "gemini",
  "message": "AI service is currently unavailable. Please try again later.",
  "error": "AI service is currently unavailable. Please try again later."
}
```

## Related Docs

- [Authentication](Authentication.md)
- [Payment Service](Payment-Service.md)
- [AI Integration](AI-Integration.md)
