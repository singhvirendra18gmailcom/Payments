# Release Notes

## Version 2.0

Version 2 focuses on AI integration and operational improvements.

### Added

- `AIService` provider interface
- Gemini AI provider
- Local deterministic AI provider
- AI provider factory
- Payment-domain service layer
- AI health endpoint: `GET /ai/health`
- Direct AI chat endpoint: `POST /chat/ask-ai`
- Direct AI payment explanation endpoint: `POST /payments/explain-ai`
- Request and response logging middleware
- AI provider failure handling
- Startup configuration validation
- Gemini service unit tests
- AI health tests
- Docs for architecture, installation, and project overview

### Changed

- `/chat/ask` now routes through the service abstraction.
- `/payments/explain` now routes through the service abstraction.
- Gemini provider failures now propagate to route handlers and return `503`.
- Tests use local AI mode to avoid external API calls.
- README updated for Version 2.

### Fixed

- `GeminiService` now implements the full `AIService` contract.
- Gemini quota/API failures no longer return misleading `200` responses.
- Test failures caused by real Gemini calls are avoided through local provider mode.

### Known Issues

- FastAPI `on_event` startup hook is deprecated and should be replaced with lifespan handlers.
- SQLite is still used for local persistence.
- OpenAI and Ollama providers are not implemented yet.
- Document upload does not yet support RAG or document question answering.

## Version 1.1

### Added

- Environment variable support
- Application logging
- Unit tests
- Dockerfile
- Docker Compose
- Improved README

## Version 1.0

### Added

- FastAPI app
- User registration
- User login
- JWT authentication
- Current user endpoint
- Payment explanation endpoint
- Chat endpoint
- Document upload endpoint
- SQLite database

## Related Docs

- [Roadmap](Roadmap.md)
- [Project Overview](Project-Overview.md)
- [Architecture](Architecture.md)
