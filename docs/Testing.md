# Testing

AI Payment Assistant uses Pytest for unit and API tests.

## Files

- `tests/conftest.py`
- `tests/test_auth.py`
- `tests/test_chat.py`
- `tests/test_gemini_service.py`
- `tests/test_health.py`
- `tests/test_login.py`
- `tests/test_payment.py`
- `tests/utils.py`

## Test Environment

`tests/conftest.py` sets:

```python
os.environ["AI_PROVIDER"] = "local"
```

This prevents tests from calling external AI APIs.

## Running Tests

Run all tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Run auth tests:

```powershell
.\.venv\Scripts\python.exe -m pytest .\tests\test_auth.py .\tests\test_login.py -q
```

Run AI tests:

```powershell
.\.venv\Scripts\python.exe -m pytest .\tests\test_gemini_service.py .\tests\test_health.py -q
```

Run chat and payment tests:

```powershell
.\.venv\Scripts\python.exe -m pytest .\tests\test_chat.py .\tests\test_payment.py -q
```

Run coverage:

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=app
```

## Test Coverage Areas

### Health

Verifies:

- `/health`
- `/ai/health`

### Authentication

Verifies:

- registration
- login
- protected route access
- current user lookup

### Chat

Verifies:

- authenticated chat API
- local deterministic payment answer behavior

### Payments

Verifies:

- payment explanation API
- authentication requirement

### Gemini Service

Verifies:

- client initialization
- missing API key behavior
- successful response handling
- empty question validation
- empty Gemini response fallback
- provider failure behavior
- health check behavior

## Why Local AI Is Used In Tests

Real AI APIs make tests unstable because of:

- network dependency
- API key dependency
- rate limits
- quota failures
- non-deterministic responses

The local provider avoids these problems.

## Common Issues

### `No module named pytest`

Use the project virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

### Gemini API Called During Tests

Check `tests/conftest.py` and ensure it sets:

```python
os.environ["AI_PROVIDER"] = "local"
```

## Related Docs

- [AI Integration](AI-Integration.md)
- [Authentication](Authentication.md)
- [Payment Service](Payment-Service.md)
