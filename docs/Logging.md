# Logging

AI Payment Assistant uses Python logging for application logs, request/response logs, and error traces.

## Files

- `app/logger.py`
- `app/main.py`
- `logs/app.log`

## Logger Setup

The logger is named:

```text
payment-assistant
```

Logs are written to:

```text
logs/app.log
```

and also streamed to the console.

## Format

```text
timestamp | level | logger | message
```

Example:

```text
2026-07-09 09:57:05,408 | INFO | payment-assistant | Request started: POST /payments/explain from 127.0.0.1
```

## Request Logging

Request logging is implemented as FastAPI middleware in `app/main.py`.

It logs:

- HTTP method
- request path
- client host
- response status code
- request duration in milliseconds

## Error Logging

Unexpected request failures are logged with stack traces.

Gemini API failures are logged in `GeminiService`.

Example logged failure:

```text
Gemini API error
429 RESOURCE_EXHAUSTED
```

## Common Log Events

| Event | Example |
|-------|---------|
| app health | `Health endpoint called` |
| user registration | `user registration endpoint called` |
| login attempt | `Login attempt: user@example.com` |
| protected user endpoint | `user me endpoint called` |
| payment explanation | `payment explain endpoint called` |
| AI health | `AI health endpoint called` |

## Operational Use

Use logs to diagnose:

- authentication failures
- provider failures
- Gemini quota exhaustion
- unexpected exceptions
- request latency
- invalid routes returning `404`

## Current Limitations

- No log rotation.
- No structured JSON logging.
- No request ID or correlation ID.
- No centralized log collector.

## Future Improvements

- Add request IDs.
- Add JSON logs.
- Add log rotation.
- Add environment-specific log levels.
- Add Sentry or another error tracker.

## Related Docs

- [Architecture](Architecture.md)
- [AI Integration](AI-Integration.md)
- [Deployment](Deployment.md)
