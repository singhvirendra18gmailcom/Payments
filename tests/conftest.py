import os

os.environ["AI_PROVIDER"] = "local"

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.auth import get_db
from app.database import Base
from app.models import User
from app.documents.models import Document
from app.documents.chunk_models import DocumentChunk
from app.auth import get_current_user
import json
import pytest

from app.documents.models import Document
from app.documents.chunk_models import DocumentChunk

# tests/conftest.py


TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(autouse=True)
def prepare_database():
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):

    test_user = User(
        id=1,
        name="Test User",
        email="test@example.com",
        hashed_password="not-used",
    )

    def override_get_db():
        try:
            yield db
        finally:
            pass

    def override_current_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[
        get_current_user
    ] = override_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def processed_document(client):

    content = (
        "PACS.008 is used for customer credit transfers. "
        "The message contains debtor, creditor and "
        "settlement information. "
        * 100
    ).encode()

    upload = client.post(
        "/documents/upload",
        files={
            "file": (
                "pacs008.txt",
                content,
                "text/plain",
            )
        },
    )

    assert upload.status_code == 201

    document_id = upload.json()["id"]

    process = client.post(
        f"/documents/{document_id}/process"
    )

    assert process.status_code == 200

    chunks = client.post(
        f"/documents/{document_id}/chunks",
        json={
            "chunk_size": 500,
            "chunk_overlap": 50,
        },
    )

    assert chunks.status_code == 200

    return document_id


@pytest.fixture
def embedded_document(db):

    document = Document(
        original_filename="pacs008.txt",
        stored_filename="pacs008-test.txt",
        file_path="test-path",
        content_type="text/plain",
        file_extension=".txt",
        file_size=100,
        processing_status="embedded",
        uploaded_by=1,
    )

    db.add(document)
    db.flush()

    chunk = DocumentChunk(
        document_id=document.id,
        chunk_order=1,
        chunk_text=(
            "PACS.008 is used for customer credit transfers."
        ),
        character_count=48,
        word_count=7,
        embedding_json=json.dumps(
            [0.01] * 768
        ),
        embedding_model="test-model",
        embedding_dimension=768,
        embedding_status="completed",
        vector_store_status="pending",
    )

    db.add(chunk)
    db.commit()

    return document.id


@pytest.fixture
def indexed_document(db):

    document = Document(
        original_filename="pacs008.txt",
        stored_filename="pacs008-test.txt",
        file_path="test-path",
        content_type="text/plain",
        file_extension=".txt",
        file_size=100,
        processing_status="indexed",
        uploaded_by=1,
    )

    db.add(document)
    db.flush()

    chunk = DocumentChunk(
        document_id=document.id,
        chunk_order=1,
        chunk_text=(
            "PACS.008 is used for customer credit transfers."
        ),
        character_count=48,
        word_count=7,
        embedding_json=json.dumps(
            [0.01] * 768
        ),
        embedding_model="test-model",
        embedding_dimension=768,
        embedding_status="completed",
        vector_id=f"document-{document.id}-chunk-1",
        vector_store="chroma",
        vector_store_status="indexed",
    )

    db.add(chunk)
    db.commit()

    return document.id