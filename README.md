# AI Payment Assistant

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

An AI-powered backend application for understanding payment messages, learning modern backend engineering, and building practical AI solutions using FastAPI.

---

## Overview

AI Payment Assistant is a learning and portfolio project focused on:

- FastAPI development
- JWT authentication
- Payment domain knowledge (SWIFT/ISO20022)
- AI integration
- Unit testing
- Docker
- GitHub Actions CI/CD
- Professional Git workflows

The long-term goal is to build an intelligent assistant capable of explaining payment messages, answering payment-related questions, and processing financial documents using AI and RAG.

---

## Features

### Current Features (Version 1)

- User Registration
- User Login
- JWT Authentication
- Current User API (`/auth/me`)
- Payment Message Explanation API
- AI Chat API
- Document Upload API
- SQLite Database
- Environment Variable Support
- Unit Tests using Pytest
- GitHub Actions CI Pipeline
- Docker Support

---

## Technology Stack

| Category | Technology |
|-----------|-------------|
| Language | Python 3.13 |
| Backend | FastAPI |
| Database | SQLite |
| ORM | SQLAlchemy |
| Authentication | JWT |
| Validation | Pydantic |
| Testing | Pytest |
| CI/CD | GitHub Actions |
| Containerization | Docker |
| Environment Management | python-dotenv |

---

## Architecture

```text
Client
   │
   ▼
FastAPI REST APIs
   │
   ├── JWT Authentication
   │
   ├── Payment Services
   │
   ├── Chat Services
   │
   └── Document Services
   │
   ▼
SQLite Database
```

Future Architecture:

```text
Client
   │
   ▼
FastAPI
   │
   ├── OpenAI
   ├── RAG
   ├── ChromaDB
   └── PostgreSQL
```

---

## Project Structure

```text
ai-payment-assistant/

├── .github/
│   └── workflows/
│       └── ci.yml
│
├── app/
│   ├── auth.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── main.py
│
├── tests/
│   ├── test_auth.py
│   ├── test_chat.py
│   ├── test_login.py
│   └── test_payment.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── README.md
└── .gitignore
```

---

## Prerequisites

Install:

- Python 3.13+
- Git
- Docker Desktop (Optional)
- VS Code or PyCharm

---

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/ai-payment-assistant.git

cd ai-payment-assistant
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

Windows:

```bash
.venv\Scripts\activate
```

Linux/Mac:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file:

```env
SECRET_KEY=my_super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./payment_assistant.db
```

Example:

```bash
cp .env.example .env
```

---

## Running Locally

Start the application:

```bash
uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://localhost:8000/docs
```

---

## Running Tests

Run all tests:

```bash
pytest -v
```

Run coverage:

```bash
pytest --cov=app
```

---

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

---

## API Endpoints

| Method | Endpoint | Description |
|----------|------------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | User login |
| GET | `/auth/me` | Get current user |
| POST | `/payments/explain` | Explain payment messages |
| POST | `/chat/ask` | Ask payment-related questions |
| POST | `/documents/upload` | Upload payment documents |
| GET | `/health` | Health check |

---

## Example API Requests

### Register User

```http
POST /auth/register
```

Request:

```json
{
  "name": "Virendra Singh",
  "email": "virendra@test.com",
  "password": "password123"
}
```

---

### Login

```http
POST /auth/login
```

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

---

### Explain Payment Message

```http
POST /payments/explain
```

Headers:

```text
Authorization: Bearer <jwt-token>
```

Request:

```json
{
  "message_type": "MT103",
  "content": "Explain MT103"
}
```

---

## GitHub Actions

The project uses GitHub Actions for Continuous Integration.

Workflow:

```text
Push
   │
   ▼
GitHub Actions
   │
   ├── Install Dependencies
   ├── Run Unit Tests
   └── Verify Build
```

Workflow file:

```text
.github/workflows/ci.yml
```

---

## Git Workflow

Recommended development workflow:

```text
Issue
   │
   ▼
Feature Branch
   │
   ▼
Development
   │
   ▼
Commit
   │
   ▼
Pull Request
   │
   ▼
Review
   │
   ▼
Merge to Main
```

Branch naming:

```text
feature/add-docker-support
feature/add-unit-tests
bugfix/login-error
docs/improve-readme
```

Commit examples:

```bash
feat(auth): add JWT authentication

feat(payment): add MT103 explanation endpoint

test(auth): add login API tests

docs(readme): improve setup instructions

ci: add GitHub Actions workflow

fix(config): add default SECRET_KEY for CI
```

---

## Roadmap

### Version 1.0

- FastAPI APIs
- JWT Authentication
- SQLite Database
- Unit Tests

### Version 1.1

- Environment Variables
- Logging
- Docker Support
- GitHub Actions
- Improved Documentation

### Version 2.0

- OpenAI Integration
- PostgreSQL
- Better Prompt Engineering

### Version 3.0

- RAG
- ChromaDB
- PDF Processing

### Version 4.0

- SWIFT MT103 Parser
- ISO20022 Support
- Payment Intelligence Features

### Version 5.0

- Kubernetes Deployment
- Cloud Hosting
- Enterprise CI/CD

---

## Learning Goals

This project helps learn:

- FastAPI
- SQLAlchemy
- JWT Authentication
- Unit Testing
- Docker
- GitHub Actions
- Git Workflows
- AI Engineering
- Payment Domain Knowledge
- RAG Systems
- Kubernetes

---

## Contributing

Contributions are welcome.

Steps:

1. Fork the repository
2. Create a feature branch
3. Write tests
4. Follow Conventional Commits
5. Open a Pull Request

Example:

```bash
git checkout -b feature/add-openai-support
```

---

## License

This project is licensed under the MIT License.

---

## Author

**Virendra Singh**

Building an AI-powered payment assistant while learning:

- FastAPI
- AI Engineering
- Payment Systems
- Docker
- Kubernetes
- Modern Backend Development