<p align="center">
  <img src="docs/images/banner.png" width="100%">
</p>
<h1 align="center">AI Payment Assistant</h1>

<p align="center">
  <strong>AI-powered assistant for understanding SWIFT MT messages, ISO 20022 messages, payment workflows, and payment-domain documentation.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-3.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688" alt="FastAPI">
  <img src="https://img.shields.io/badge/AI-Google%20Gemini-orange" alt="Gemini">
  <img src="https://img.shields.io/badge/RAG-Enabled-success" alt="RAG">
  <img src="https://img.shields.io/badge/Vector%20DB-ChromaDB-green" alt="ChromaDB">
  <img src="https://img.shields.io/badge/Database-SQLite-07405E" alt="SQLite">
  <img src="https://img.shields.io/badge/Migrations-Alembic-red" alt="Alembic">
  <img src="https://img.shields.io/badge/Tests-Pytest-yellow" alt="Pytest">
  <img src="https://img.shields.io/badge/License-MIT-lightgrey" alt="License">
</p>

---
## Overview

AI Payment Assistant is a FastAPI-based backend application designed to make complex international-payment concepts and payment documentation easier to understand using Generative AI and Retrieval-Augmented Generation (RAG).

The application can:

- Explain SWIFT MT and ISO 20022 payment messages
- Answer payment-domain questions using Google Gemini
- Register and authenticate users securely with JWT
- Upload and manage payment-related PDF, TXT, and DOCX documents
- Extract text from uploaded documents
- Split document content into searchable chunks
- Generate vector embeddings using Google Gemini
- Store and index document vectors in ChromaDB
- Perform semantic search to retrieve relevant document content
- Answer document-specific questions using a complete RAG pipeline
- Provide source chunks for traceability of AI-generated answers
- Secure document access using user-level ownership
- Delete documents along with physical files, metadata, chunks, and vectors
- Manage database schema changes using Alembic migrations
- Provide application and AI-service health checks
- Run automated tests through Pytest and GitHub Actions

This project combines **backend engineering, Generative AI, Retrieval-Augmented Generation, vector search, and international-payments domain knowledge** to demonstrate how AI can be integrated into a real-world payment-domain application.

---

## Features

### Authentication

- User registration
- Secure user login
- JWT access-token generation
- Protected user-profile endpoint
- Authentication for protected APIs
- User-level document ownership and access control

### Payment Explanation

- Explain payment messages using structured domain logic
- Generate AI-powered payment explanations using Google Gemini
- Support SWIFT MT and ISO 20022 payment-message concepts
- Provide simplified explanations of complex payment fields and workflows
- Maintain separate local and AI-powered explanation endpoints

### AI Chat

- Ask payment-domain and general AI questions
- Generate conversational responses using Google Gemini
- Support payment concepts, terminology, and workflow-related queries
- Provide a standalone AI chat experience independent of uploaded documents

### Document Management

- Upload payment-domain PDF, TXT, and DOCX documents securely
- Associate uploaded documents with the authenticated user
- Store original uploaded files on disk
- Persist document metadata and processing status in SQLite
- List documents belonging to the authenticated user
- Track original filename, content type, file size, and upload timestamp
- Enforce user-level document ownership and access control
- Delete documents together with physical files, metadata, chunks, and ChromaDB vectors

### Document Processing & RAG

- Extract text from uploaded documents
- Split extracted content into configurable overlapping chunks
- Generate numerical embeddings using Google Gemini
- Store and index document vectors in ChromaDB
- Perform semantic search across document chunks
- Retrieve Top-K relevant chunks using vector similarity
- Generate document-grounded answers using Retrieval-Augmented Generation (RAG)
- Return source chunks for answer traceability

### Engineering and Operations

- Environment-based configuration and secret management
- Structured application and request logging
- SQLAlchemy ORM with SQLite persistence
- Alembic-based database schema migrations
- Persistent ChromaDB vector storage
- Modular service architecture for AI, embeddings, RAG, and vector operations
- Pytest unit and API integration testing
- Mocked Gemini and ChromaDB dependencies for deterministic tests
- GitHub Actions continuous integration
- Swagger/OpenAPI documentation
- Application and AI-service health endpoints

---

## Technology Stack

| Area | Technology |
| --- | --- |
| Programming language | Python |
| API framework | FastAPI |
| AI / LLM provider | Google Gemini |
| Embedding provider | Google Gemini Embeddings |
| RAG architecture | Retrieval-Augmented Generation (RAG) |
| Vector database | ChromaDB |
| Database ORM | SQLAlchemy |
| Application database | SQLite |
| Database migrations | Alembic |
| Authentication | JWT |
| Data validation | Pydantic |
| Document processing | PDF / TXT / DOCX processing |
| Semantic search | Vector similarity search |
| Testing | Pytest / FastAPI TestClient |
| CI/CD | GitHub Actions |
| API documentation | Swagger UI / OpenAPI |
| Logging | Python structured logging |

---


## Architecture

```mermaid
flowchart LR
    U[User / API Client] --> F[FastAPI Application]

    F --> A[Authentication Module]
    F --> P[Payment Explanation Module]
    F --> C[AI Chat Module]
    F --> D[Document / RAG Module]
    F --> H[Health Module]

    A --> DB[(SQLite Database)]
    P --> G[Google Gemini API]
    C --> G

    D --> UP[Document Upload]
    UP --> FS[(Local File Storage)]
    UP --> DB

    D --> EX[Text Extraction]
    EX --> DB

    D --> CH[Text Chunking]
    CH --> DB

    D --> EM[Embedding Generation]
    EM --> GE[Gemini Embedding API]
    EM --> DB

    D --> VS[Vector Indexing]
    VS --> VDB[(ChromaDB)]

    D --> SS[Semantic Search]
    SS --> GE
    SS --> VDB

    D --> RAG[RAG Question Answering]
    RAG --> SS
    RAG --> G

    F --> L[Structured Logging]
    F --> T[Pytest Test Suite]
    T --> CI[GitHub Actions]
```



### Request Flow

1. A user registers or logs in and receives a JWT access token.
2. The user authorizes protected API requests using the token.
3. FastAPI validates incoming requests using Pydantic models.
4. The application verifies authentication and document ownership where required.
5. The appropriate service processes the request.
6. For document ingestion:
   - The document is uploaded and stored locally.
   - Document metadata is persisted in SQLite.
   - Text is extracted from the document.
   - Extracted text is split into overlapping chunks.
   - Google Gemini generates numerical embeddings for each chunk.
   - Embeddings, chunk content, and metadata are indexed in ChromaDB.
7. For semantic search:
   - The user's question is converted into an embedding.
   - ChromaDB performs vector similarity search.
   - The Top-K most relevant document chunks are retrieved.
8. For RAG question answering:
   - The retrieved chunks are assembled as document context.
   - The question and context are sent to Google Gemini.
   - Gemini generates an answer grounded in the retrieved document content.
   - Relevant source chunks are returned with the answer for traceability.
9. Payment-explanation and general AI-chat endpoints call Google Gemini independently of the document RAG pipeline.
10. The API returns a structured JSON response.
11. Important requests, processing events, errors, and execution times are recorded through structured application logging.
---

## API Documentation

After starting the application, open:

```text
http://127.0.0.1:8000/docs
```

Alternative OpenAPI documentation:

```text
http://127.0.0.1:8000/redoc
```

---

## Screenshots

### Swagger API Overview

![Swagger API Overview](docs/images/swagger-api.png)

### Document Processing APIs

![Document Processing APIs](docs/images/swagger-document-processing.png)

### Semantic Search & RAG APIs

![Semantic Search and RAG APIs](docs/images/swagger-rag.png)
### User Login

![User Login](docs/images/login-api.png)

### AI Payment Explanation

![AI Payment Explanation](docs/images/payment-explanation.png)

### Document Upload

![Document Upload](docs/images/document-upload.png)

### GitHub Actions

![GitHub Actions](docs/images/github-actions.png)

> Add the corresponding image files under `docs/images/`. Remove any passwords, API keys, JWT tokens, personal data, or real payment information before publishing screenshots.

---

## Project Structure

```text
ai-payment-assistant/
├── app/
│   ├── documents/
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── router.py
│   │   └── service.py
│   ├── services/
│   ├── auth.py
│   ├── config.py
│   ├── database.py
│   ├── logger.py
│   ├── main.py
│   ├── models.py
│   ├── payment_service.py
│   └── schemas.py
├── docs/
├── logs/
├── tests/
├── uploads/
├── .github/
├── .env.example
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/ai-payment-assistant.git
cd ai-payment-assistant
```

### 2. Create a virtual environment

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create the environment file

Copy the example file:

#### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

#### macOS or Linux

```bash
cp .env.example .env
```

Update `.env` with your local configuration:

```env
SECRET_KEY=replace_with_a_strong_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./ai_payment_assistant.db
GEMINI_API_KEY=replace_with_your_gemini_api_key
```

Never commit your real `.env` file.

### 5. Start the application

```bash
uvicorn app.main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

### 6. Open Swagger UI

```text
http://127.0.0.1:8000/docs
```

---

## Testing

Run all tests from the project virtual environment:

### Windows PowerShell

```powershell
.\.venv\Scripts\python.exe -m pytest
```

### macOS or Linux

```bash
python -m pytest
```

Run tests with detailed output:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Run tests with coverage when `pytest-cov` is installed:

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing
```

The test suite uses `AI_PROVIDER=local` from `tests/conftest.py`, so tests do not call the external Gemini API.

---

## Main API Endpoints

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| GET | `/health` | Application health check | No |
| GET | `/ai/health` | AI-service health check | No |
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/login` | Authenticate user with OAuth2 password form data | No |
| GET | `/auth/me` | Get current user profile | Yes |
| POST | `/payments/explain` | Explain payment message | Yes |
| POST | `/payments/explain-ai` | Explain payment using AI | No |
| POST | `/chat/ask` | Ask Payment Assistant | Yes |
| POST | `/chat/ask-ai` | Ask General AI Assistant | No |
| POST | `/documents/upload` | Upload PDF or TXT document, persist metadata, and save the file under `uploads/documents` | Yes |
| POST | `/documents/upload/v2` | Upload PDF, TXT, or DOCX document to the legacy local storage path | Yes |
| GET | `/documents` | List uploaded documents from the legacy local upload directory | Yes |

---

## Example Usage

### Register a user

```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example User",
    "email": "user@example.com",
    "password": "StrongPassword123"
  }'
```

### Log in

```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=StrongPassword123"
```

The login endpoint follows FastAPI's OAuth2 password flow. Use `username` for the registered email address.

### Explain a payment message

```bash
TOKEN="paste_access_token_here"

curl -X POST "http://127.0.0.1:8000/payments/explain" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message_type": "pacs.008",
    "content": "Add a safe sample payment message here"
  }'
```

Use `/payments/explain-ai` for the AI-powered public endpoint.

### Upload a document

The primary upload endpoint is `/documents/upload`. It accepts authenticated multipart uploads, allows only PDF and TXT files, enforces a 10 MB limit, stores the file under `uploads/documents`, and creates a document record in the database.

```bash
curl -X POST "http://127.0.0.1:8000/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample-document.pdf;type=application/pdf"
```

Expected response fields:

- `document_id`
- `original_filename`
- `content_type`
- `file_size`
- `processing_status`
- `uploaded_at`

The older `/documents/upload/v2` endpoint still exists for direct local file storage and also accepts `.docx` files.

---

## Security

- Passwords should be stored only as secure hashes.
- Protected endpoints require JWT authentication.
- Secrets are loaded from environment variables.
- `.env` must remain excluded through `.gitignore`.
- Screenshots and examples must not contain real customer or payment data.
- API responses should avoid exposing internal exception details.
- Uploaded documents should be validated for file type and size.
- `/documents/upload` accepts only PDF and TXT files and enforces a 10 MB size limit.

---

## Continuous Integration

GitHub Actions runs the automated test suite when code is pushed or a pull request is created.

Suggested workflow checks:

- Install Python
- Install project dependencies
- Run Pytest
- Fail the workflow when tests fail

Workflow file location:

```text
.github/workflows/tests.yml
```

---

## Current Version

### Version 3.0.0

Version 3 includes:

- JWT authentication
- Payment-message explanation
- AI-powered payment explanation
- AI chat endpoints
- Document upload with database-backed metadata
- Legacy local document upload and listing
- Structured logging
- Automated testing
- GitHub Actions CI
- Improved Swagger documentation

---

## Roadmap

Planned Version 3 improvements:

- Retrieval-Augmented Generation
- Semantic search across uploaded documents
- Payment-message validation
- Conversation history
- Role-based access control
- PostgreSQL support
- Docker deployment
- Cloud deployment
- Improved monitoring and analytics
- Web-based frontend

---

## Learning Outcomes

This project demonstrates practical experience in:

- FastAPI backend development
- REST API design
- JWT-based authentication
- SQLAlchemy database integration
- Generative AI integration
- Payment-domain application design
- Automated testing
- Continuous integration
- Logging and configuration management
- Technical documentation

---

## Author

**Virendra Singh**

- GitHub: `https://github.com/YOUR-USERNAME`
- LinkedIn: `https://www.linkedin.com/in/YOUR-LINKEDIN-PROFILE`

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Disclaimer

This project is intended for learning and demonstration purposes. It must not be used to process real customer data, confidential payment messages, or production financial transactions without appropriate security, compliance, validation, and operational controls.
