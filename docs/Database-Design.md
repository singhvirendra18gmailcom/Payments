# Database Design

AI Payment Assistant currently uses SQLite with SQLAlchemy.

## Files

- `app/database.py`
- `app/models.py`
- `app/auth.py`

## Database Configuration

The database URL is configured through:

```env
DATABASE_URL=sqlite:///./payment_assistant.db
```

`app/database.py` creates:

- SQLAlchemy engine
- session factory
- declarative base

## Engine

```python
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
```

`check_same_thread=False` is used for SQLite compatibility with FastAPI request handling.

## Session Management

`SessionLocal` is used to create database sessions.

`get_db()` in `app/auth.py` provides a request-scoped session:

```text
create session
  |
  v
yield to route
  |
  v
close session
```

## Tables

### `users`

Defined in `app/models.py`.

| Column | Type | Notes |
|--------|------|-------|
| `id` | Integer | Primary key, indexed |
| `name` | String | Required |
| `email` | String | Required, unique, indexed |
| `hashed_password` | String | Required |
| `created_at` | DateTime | Defaults to UTC timestamp |

## Table Creation

Tables are created on app import/startup in `app/main.py`:

```python
Base.metadata.create_all(bind=engine)
```

This is acceptable for the current learning/local setup. For production, migrations should be added.

## Current Limitations

- No Alembic migrations yet.
- SQLite is used instead of PostgreSQL.
- Uploaded documents are stored on disk, not in the database.
- There are no audit tables or domain-specific payment tables yet.

## Future Schema Ideas

Possible future tables:

- `documents`
- `chat_sessions`
- `chat_messages`
- `payment_explanations`
- `ai_requests`
- `payment_messages`
- `parsed_payment_fields`

## Tests

Database behavior is indirectly tested through:

- auth tests
- login tests
- protected endpoint tests

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest .\tests\test_auth.py .\tests\test_login.py -q
```

## Related Docs

- [Authentication](Authentication.md)
- [Architecture](Architecture.md)
- [Deployment](Deployment.md)
