# Roadmap

This roadmap tracks planned improvements for AI Payment Assistant.

## Version 1.0 - Completed

- [x] FastAPI application setup
- [x] SQLite database
- [x] SQLAlchemy models
- [x] User registration
- [x] User login
- [x] JWT authentication
- [x] Current user endpoint
- [x] Payment explanation endpoint
- [x] Chat endpoint
- [x] Document upload endpoint

## Version 1.1 - Completed

- [x] Environment variable support
- [x] Application logging
- [x] Unit tests
- [x] Dockerfile
- [x] Docker Compose
- [x] Improved README

## Version 2.0 - Completed

- [x] AI service interface
- [x] Gemini provider integration
- [x] Local AI provider
- [x] AI provider factory
- [x] Payment service layer
- [x] AI chat functionality
- [x] AI payment explanation flow
- [x] AI health check endpoint
- [x] Request and response logging
- [x] AI API failure handling
- [x] Startup configuration validation
- [x] Gemini service unit tests
- [x] Version 2 documentation

## Version 2.1 - Planned

- [ ] Replace FastAPI `on_event` startup hook with lifespan handler
- [ ] Add request correlation IDs
- [ ] Add structured JSON logging
- [ ] Add stronger endpoint response models
- [ ] Add tests for AI failure API responses
- [ ] Add tests for configuration validation
- [ ] Update `.env.example` with `GEMINI_MODEL`

## Version 3.0 - Planned

- [ ] Add OpenAI provider
- [ ] Add Ollama provider
- [ ] Add PostgreSQL support
- [ ] Add Alembic migrations
- [ ] Add better prompt templates
- [ ] Add provider-level timeout configuration

## Version 4.0 - Planned

- [ ] Add document parsing
- [ ] Add PDF text extraction
- [ ] Add embeddings
- [ ] Add vector database integration
- [ ] Add RAG service
- [ ] Add document question answering

## Version 5.0 - Planned

- [ ] Add SWIFT MT parser
- [ ] Add ISO 20022 XML parser
- [ ] Add payment field validation
- [ ] Add payment investigation workflows
- [ ] Add payment intelligence features

## Version 6.0 - Planned

- [ ] Add Kubernetes deployment
- [ ] Add cloud deployment guide
- [ ] Add production secret management
- [ ] Add monitoring and alerting
- [ ] Add enterprise CI/CD workflow

## Related Docs

- [Release Notes](Release-Notes.md)
- [Project Overview](Project-Overview.md)
- [Architecture](Architecture.md)
