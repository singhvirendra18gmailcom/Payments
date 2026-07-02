# AI Payment Assistant - Version 1 (MVP)

## Overview

AI Payment Assistant is a learning project that combines modern backend development with payment domain knowledge.

The application helps payment professionals and developers understand payment messages, ask payment-related questions, and manage reference documents through REST APIs.

Version 1 focuses on building a solid backend foundation using FastAPI, authentication, SQLite, and file uploads.

---

## Objectives

The primary goals of Version 1 are:

* Learn Python backend development
* Build REST APIs using FastAPI
* Implement JWT authentication
* Work with SQLAlchemy ORM
* Handle file uploads
* Apply clean architecture principles
* Create a foundation for future AI and RAG capabilities

---

## Features

### Health Check

Verify that the application is running.

```http
GET /health
```

Response:

```json
{
    "status": "ok",
    "app": "AI Payment Assistant"
}
```

---

### User Registration

Create a new user account.

```http
POST /auth/register
```

Request:

```json
{
    "name": "Viren",
    "email": "viren@example.com",
    "password": "Password@123"
}
```

Response:

```json
{
    "message": "User registered successfully",
    "email": "viren@example.com"
}
```

---

### User Login

Authenticate a user and generate a JWT access token.

```http
POST /auth/login
```

Request:

```json
{
    "email": "viren@example.com",
    "password": "Password@123"
}
```

Response:

```json
{
    "access_token": "<jwt-token>",
    "token_type": "bearer"
}
```

---

### Current User

Retrieve information about the authenticated user.

```http
GET /auth/me
```

Headers:

```text
Authorization: Bearer <jwt-token>
```

Response:

```json
{
    "name": "Viren",
    "email": "viren@example.com"
}
```

---

### Payment Explanation

Explain SWIFT and ISO 20022 payment messages.

```http
POST /payments/explain
```

Request:

```json
{
    "message_type": "MT103",
    "content": "What is MT103?"
}
```

Response:

```json
{
    "message_type": "MT103",
    "explanation": "MT103 is a SWIFT message used for customer credit transfer between banks."
}
```

Supported message types:

* MT103
* PACS.008
* PAIN.001
* CAMT.053

---

### Payment Questions

Ask basic payment-related questions.

```http
POST /chat/ask
```

Request:

```json
{
    "question": "What is pacs.008?"
}
```

Response:

```json
{
    "question": "What is pacs.008?",
    "answer": "pacs.008 is used in ISO 20022 for FI to FI customer credit transfer."
}
```

---

### Document Upload

Upload payment reference documents.

```http
POST /documents/upload
```

Supported file types:

* PDF
* TXT
* DOCX

Response:

```json
{
    "filename": "iso20022.pdf",
    "status": "uploaded"
}
```

---

### List Documents

Retrieve all uploaded documents.

```http
GET /documents
```

Response:

```json
[
    {
        "filename": "iso20022.pdf",
        "type": "pdf"
    }
]
```

---

## Technology Stack

| Component            | Technology       |
| -------------------- | ---------------- |
| Backend Framework    | FastAPI          |
| Programming Language | Python 3.13+     |
| Database             | SQLite           |
| ORM                  | SQLAlchemy       |
| Authentication       | JWT              |
| Password Hashing     | Passlib (bcrypt) |
| API Documentation    | Swagger UI       |
| File Upload          | python-multipart |

---

## Project Structure

```text
ai-payment-assistant/

├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── payment_service.py
│   └── uploads/
│
├── requirements.txt
└── README.md
```

---

## Architecture

```text
Client
   │
   ▼
FastAPI Controllers
   │
   ▼
Business Services
   │
   ▼
SQLAlchemy ORM
   │
   ▼
SQLite Database
```

---

## Database Schema

### Users Table

```text
users

id               INTEGER PRIMARY KEY
name             VARCHAR
email            VARCHAR UNIQUE
hashed_password  VARCHAR
created_at       DATETIME
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/your-username/ai-payment-assistant.git

cd ai-payment-assistant
```

---

### Create Virtual Environment

Windows:

```powershell
python -m venv venv

.\venv\Scripts\Activate.ps1
```

Linux/Mac:

```bash
python3 -m venv venv

source venv/bin/activate
```

---

### Install Dependencies

```bash
pip install fastapi
pip install uvicorn
pip install sqlalchemy
pip install passlib[bcrypt]
pip install python-jose[cryptography]
pip install python-multipart
pip install pydantic[email]
```

Or:

```bash
pip install -r requirements.txt
```

---

## Running the Application

Start the development server:

```bash
python -m uvicorn app.main:app --reload
```

Application URL:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

---

## API Testing Flow

Recommended testing sequence:

### Step 1

Check health endpoint:

```http
GET /health
```

---

### Step 2

Register a new user:

```http
POST /auth/register
```

---

### Step 3

Login:

```http
POST /auth/login
```

Copy the JWT token.

---

### Step 4

Authorize in Swagger UI:

```text
Bearer <your-token>
```

---

### Step 5

Test protected APIs:

```http
GET /auth/me

POST /payments/explain

POST /chat/ask

POST /documents/upload

GET /documents
```

---

## Version 1 Limitations

Current limitations include:

* SQLite database only
* Local file storage
* No OpenAI integration
* No PostgreSQL support
* No vector database
* No RAG implementation
* No frontend application
* Basic hardcoded payment knowledge

---

## Roadmap

### Version 1 (Current)

* FastAPI backend
* JWT authentication
* SQLite database
* Payment explanations
* Basic Q&A
* File upload

---

### Version 2

* PostgreSQL
* OpenAI integration
* Payment glossary
* Interview question generation
* ISO 20022 knowledge base

---

### Version 3

* RAG implementation
* ChromaDB
* PDF understanding
* Embeddings
* Source references

---

### Version 4

* SWIFT MT to ISO 20022 conversion
* Sanctions checker
* Error resolution assistant
* Payment test case generation

---

### Version 5

* Docker
* Kubernetes
* CI/CD
* Monitoring
* Cloud deployment
* Production readiness

---

## Learning Outcomes

By completing Version 1, you will gain practical experience in:

* Python programming
* FastAPI development
* REST API design
* SQLAlchemy ORM
* JWT authentication
* Dependency injection
* File uploads
* API documentation
* Backend project organization

---

## Future Vision

The long-term vision is to evolve this project into an enterprise-grade AI platform for payments that supports:

* ISO 20022 expertise
* SWIFT message analysis
* Regulatory guidance
* Document intelligence
* AI-powered payment operations
* Developer productivity tools

---

Built as a hands-on learning project combining modern AI engineering practices with real-world payment domain expertise.
