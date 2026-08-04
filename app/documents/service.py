from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.documents.models import Document
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.documents.chunk_models import DocumentChunk
from app.documents.models import Document
from app.documents.text_chunker import split_text_into_chunks
import json
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.embedding_service import (
    EmbeddingGenerationError,
    GeminiEmbeddingService,
)
from app.documents.chunk_models import DocumentChunk
from app.documents.models import Document
import json
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.documents.chunk_models import DocumentChunk
from app.documents.models import Document
from app.vector_store.chroma_store import (
    ChromaVectorStore,
    VectorStoreError,
)
from app.vector_store.models import VectorRecord

from .config import (
    ALLOWED_CONTENT_TYPES,
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE,
    READ_CHUNK_SIZE,
    UPLOAD_DIRECTORY,
)
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.documents.models import Document
from app.documents.text_extractor import (
    DocumentExtractionError,
    extract_document_text,
)


def validate_basic_file_details(file: UploadFile) -> str:
    """
    Validate filename, extension and content type.

    Returns:
        Normalized file extension, such as '.pdf'.
    """

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file must have a filename.",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                "Unsupported file extension. "
                "Only PDF and TXT files are allowed."
            ),
        )

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                "Unsupported content type. "
                "Only application/pdf and text/plain are allowed."
            ),
        )

    return extension


async def save_uploaded_file(
    file: UploadFile,
    destination: Path,
) -> int:
    """
    Save an uploaded file in chunks.

    The function also validates:
    - Empty files
    - Maximum file size

    Returns:
        Total number of bytes saved.
    """

    total_size = 0

    try:
        with destination.open("wb") as output_file:
            while chunk := await file.read(READ_CHUNK_SIZE):
                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                        detail="The uploaded file exceeds the 10 MB limit.",
                    )

                output_file.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is empty.",
            )

        return total_size

    except Exception:
        if destination.exists():
            destination.unlink()

        raise

    finally:
        await file.close()


async def upload_document(
    *,
    file: UploadFile,
    current_user_id: int,
    db: Session,
) -> Document:
    """
    Validate, store and register an uploaded document.
    """

    extension = validate_basic_file_details(file)

    UPLOAD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    stored_filename = f"{uuid4()}{extension}"
    destination = UPLOAD_DIRECTORY / stored_filename

    file_size = await save_uploaded_file(
        file=file,
        destination=destination,
    )

    document = Document(
        original_filename=Path(file.filename).name,
        stored_filename=stored_filename,
        file_path=str(destination),
        content_type=file.content_type,
        file_extension=extension,
        file_size=file_size,
        processing_status="uploaded",
        uploaded_by=current_user_id,
    )

    try:
        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    except Exception:
        db.rollback()

        # Avoid leaving an orphaned physical file if DB insertion fails.
        if destination.exists():
            destination.unlink()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The document could not be saved.",
        )

def process_document_text(
    *,
    document_id: int,
    current_user_id: int,
    db: Session,
) -> Document:
    """
    Extract text from an uploaded document and update its database record.
    """

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.uploaded_by == current_user_id,
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    if document.processing_status == "processing":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document processing is already in progress.",
        )

    document.processing_status = "processing"
    document.error_message = None

    try:
        db.commit()

        extraction_result = extract_document_text(
            file_path=document.file_path,
            file_extension=document.file_extension,
        )

        document.extracted_text = extraction_result.text
        document.page_count = extraction_result.page_count
        document.processing_status = "completed"
        document.processed_at = datetime.now(timezone.utc)
        document.error_message = None

        db.commit()
        db.refresh(document)

        return document

    except DocumentExtractionError as exc:
        db.rollback()

        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if document is not None:
            document.processing_status = "failed"
            document.error_message = str(exc)
            document.processed_at = datetime.now(timezone.utc)

            db.commit()

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        )

    except Exception:
        db.rollback()

        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if document is not None:
            document.processing_status = "failed"
            document.error_message = (
                "An unexpected document-processing error occurred."
            )
            document.processed_at = datetime.now(timezone.utc)

            db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The document could not be processed.",
        )

def create_document_chunks(
    *,
    document_id: int,
    current_user_id: int,
    db: Session,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[DocumentChunk]:
    """
    Split extracted text and save chunks in the database.
    """

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.uploaded_by == current_user_id,
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    if document.processing_status != "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Document text extraction must be completed "
                "before chunking."
            ),
        )

    if not document.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The document does not contain extracted text.",
        )

    try:
        generated_chunks = split_text_into_chunks(
            text=document.extracted_text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        # Prevent duplicate chunks when the endpoint is called again.
        (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document.id)
            .delete(synchronize_session=False)
        )

        database_chunks: list[DocumentChunk] = []

        for chunk in generated_chunks:
            database_chunk = DocumentChunk(
                document_id=document.id,
                chunk_order=chunk.order,
                chunk_text=chunk.text,
                character_count=chunk.character_count,
                word_count=chunk.word_count,
            )

            db.add(database_chunk)
            database_chunks.append(database_chunk)

        document.processing_status = "chunked"

        db.commit()

        for chunk in database_chunks:
            db.refresh(chunk)

        return database_chunks

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document chunking failed.",
        ) from exc

def generate_document_embeddings(
    *,
    document_id: int,
    current_user_id: int,
    db: Session,
) -> list[DocumentChunk]:
    """
    Generate and persist embeddings for every chunk of a document.
    """

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.uploaded_by == current_user_id,
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_order.asc())
        .all()
    )

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Document chunks have not been created. "
                "Run the chunking endpoint first."
            ),
        )

    embedding_service = GeminiEmbeddingService()
    completed_chunks: list[DocumentChunk] = []

    try:
        for chunk in chunks:
            chunk.embedding_status = "processing"
            chunk.embedding_error = None
            db.commit()

            try:
                vector = (
                    embedding_service.generate_document_embedding(
                        text=chunk.chunk_text,
                        title=document.original_filename,
                    )
                )

                chunk.embedding_json = json.dumps(vector)
                chunk.embedding_model = embedding_service.model
                chunk.embedding_dimension = len(vector)
                chunk.embedding_status = "completed"
                chunk.embedding_error = None
                chunk.embedded_at = datetime.now(timezone.utc)

                db.commit()
                db.refresh(chunk)

                completed_chunks.append(chunk)

            except EmbeddingGenerationError as exc:
                chunk.embedding_status = "failed"
                chunk.embedding_error = str(exc)
                db.commit()

                raise

        document.processing_status = "embedded"
        db.commit()
        db.refresh(document)

        return completed_chunks

    except EmbeddingGenerationError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document embedding process failed.",
        ) from exc

def store_document_vectors(
    *,
    document_id: int,
    current_user_id: int,
    db: Session,
) -> list[DocumentChunk]:
    """
    Store all completed chunk embeddings in ChromaDB.
    """

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.uploaded_by == current_user_id,
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    chunks = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == document_id
        )
        .order_by(DocumentChunk.chunk_order.asc())
        .all()
    )

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Document chunks have not been created."
            ),
        )

    incomplete_chunks = [
        chunk
        for chunk in chunks
        if (
            chunk.embedding_status != "completed"
            or not chunk.embedding_json
        )
    ]

    if incomplete_chunks:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"{len(incomplete_chunks)} chunks do not have "
                "completed embeddings. Generate embeddings first."
            ),
        )

    vector_records: list[VectorRecord] = []

    try:
        for chunk in chunks:
            vector_id = (
                f"document-{document.id}-chunk-{chunk.id}"
            )

            try:
                embedding = json.loads(
                    chunk.embedding_json
                )
            except json.JSONDecodeError as exc:
                raise HTTPException(
                    status_code=(
                        status.HTTP_422_UNPROCESSABLE_CONTENT
                    ),
                    detail=(
                        f"Chunk {chunk.id} contains an invalid "
                        "embedding."
                    ),
                ) from exc

            if not isinstance(embedding, list):
                raise HTTPException(
                    status_code=(
                        status.HTTP_422_UNPROCESSABLE_CONTENT
                    ),
                    detail=(
                        f"Chunk {chunk.id} embedding is not a list."
                    ),
                )

            if (
                chunk.embedding_dimension is not None
                and len(embedding)
                != chunk.embedding_dimension
            ):
                raise HTTPException(
                    status_code=(
                        status.HTTP_422_UNPROCESSABLE_CONTENT
                    ),
                    detail=(
                        f"Chunk {chunk.id} embedding dimension "
                        "does not match its metadata."
                    ),
                )

            chunk.vector_id = vector_id
            chunk.vector_store_status = "indexing"
            chunk.vector_store_error = None

            vector_records.append(
                VectorRecord(
                    vector_id=vector_id,
                    embedding=[
                        float(value)
                        for value in embedding
                    ],
                    document_text=chunk.chunk_text,
                    metadata={
                        "document_id": document.id,
                        "chunk_id": chunk.id,
                        "chunk_order": chunk.chunk_order,
                        "user_id": current_user_id,
                        "original_filename": (
                            document.original_filename
                        ),
                        "embedding_model": (
                            chunk.embedding_model or "unknown"
                        ),
                        "embedding_dimension": len(embedding),
                    },
                )
            )

        db.commit()

        vector_store = ChromaVectorStore()

        result = vector_store.upsert_records(
            vector_records
        )

        stored_ids = set(result.vector_ids)
        indexed_at = datetime.now(timezone.utc)

        for chunk in chunks:
            if chunk.vector_id in stored_ids:
                chunk.vector_store = "chroma"
                chunk.vector_store_status = "indexed"
                chunk.vector_store_error = None
                chunk.indexed_at = indexed_at

        document.processing_status = "indexed"

        db.commit()

        for chunk in chunks:
            db.refresh(chunk)

        return chunks

    except HTTPException:
        db.rollback()
        raise

    except VectorStoreError as exc:
        db.rollback()

        failed_chunks = (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.document_id
                == document_id
            )
            .all()
        )

        for chunk in failed_chunks:
            if chunk.vector_store_status == "indexing":
                chunk.vector_store_status = "failed"
                chunk.vector_store_error = str(exc)

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Document vector storage failed.",
        ) from exc