# Authentication

AI Payment Assistant uses JWT bearer authentication for protected API endpoints.

## Files

- `app/auth.py`
- `app/models.py`
- `app/schemas.py`
- `app/main.py`

## User Model

Users are stored in the `users` table.

Fields:

- `id`
- `name`
- `email`
- `hashed_password`
- `created_at`

The `email` field is unique and indexed.

## Password Hashing

Passwords are hashed with Passlib using Argon2:

```python
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
```

Plain-text passwords are accepted only during registration and login. Stored passwords are hashed.

## JWT Token Flow

```text
POST /auth/login
  |
  v
verify email and password
  |
  v
create JWT token with sub=<email>
  |
  v
return access_token
```

The token payload includes:

- `sub`: user email
- `exp`: expiry timestamp

## Protected Endpoint Flow

```text
Request with Authorization header
  |
  v
OAuth2PasswordBearer
  |
  v
decode JWT
  |
  v
load user from database
  |
  v
route handler receives current_user
```

## Auth Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register a user |
| `POST` | `/auth/login` | Login and receive JWT |
| `GET` | `/auth/me` | Return current authenticated user |

## Register Request

```json
{
  "name": "Virendra Singh",
  "email": "virendra@test.com",
  "password": "password123"
}
```

## Login Response

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

## Authorization Header

```text
Authorization: Bearer <jwt-token>
```

## Configuration

Authentication depends on:

```env
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## Error Cases

| Case | Status |
|------|--------|
| Duplicate registration email | `400` |
| Invalid login email | `401` |
| Invalid login password | `401` |
| Missing bearer token | `401` |
| Invalid token | `401` |
| User not found | `401` |

## Tests

Relevant tests:

- `tests/test_auth.py`
- `tests/test_login.py`
- `tests/utils.py`

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest .\tests\test_auth.py .\tests\test_login.py -q
```

## Related Docs

- [Architecture](Architecture.md)
- [API Documentation](API-Documentation.md)
- [Database Design](Database-Design.md)
