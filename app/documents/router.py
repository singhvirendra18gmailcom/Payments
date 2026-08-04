from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_db
from app.models import User
from app.schemas import DocumentUploadResponse
from app.auth import get_current_user
from .chunk_models import DocumentChunk
from .models import Document

from .service import upload_document
from app.documents.schemas import DocumentProcessingResponse
from app.documents.schemas import ExtractedTextResponse
from app.documents.service import process_document_text
from app.documents.schemas import (
    DocumentChunkRequest,
    DocumentChunkResponse,
    DocumentChunkSummary,
)
from app.documents.service import create_document_chunks
from app.documents.schemas import (
    ChunkEmbeddingSummary,
    DocumentEmbeddingResponse,
)
from app.documents.service import generate_document_embeddings
from app.documents.schemas import (
    ChunkVectorStoreSummary,
    DocumentVectorStoreResponse,
)
from app.documents.service import store_document_vectors
from app.vector_store.config import (
    CHROMA_COLLECTION_NAME,
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Document Upload"],
    summary="Upload a document",
    description=(
        "Uploads a PDF or TXT document, stores it securely and "
        "creates a document metadata record."
    ),
)
async def upload_document_endpoint(
    file: Annotated[
        UploadFile,
        File(description="PDF or TXT document, maximum size 10 MB"),
    ],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentUploadResponse:
    document = await upload_document(
        file=file,
        current_user_id=current_user.id,
        db=db,
    )

    return DocumentUploadResponse.model_validate(document)


@router.post(
    "/{document_id}/process",
    response_model=DocumentProcessingResponse,
    tags=["Document Processing"],
    summary="Extract text from an uploaded document",
)
def process_document_endpoint(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentProcessingResponse:
    document = process_document_text(
        document_id=document_id,
        current_user_id=current_user.id,
        db=db,
    )

    return DocumentProcessingResponse(
        document_id=document.id,
        original_filename=document.original_filename,
        processing_status=document.processing_status,
        page_count=document.page_count,
        character_count=len(document.extracted_text or ""),
        processed_at=document.processed_at,
        error_message=document.error_message,
    )



@router.get(
    "/{document_id}/text",
    response_model=ExtractedTextResponse,
    tags=["Document Query"],
    summary="Get extracted document text",
)
def get_extracted_text(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExtractedTextResponse:
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.uploaded_by == current_user.id,
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return ExtractedTextResponse(
        document_id=document.id,
        original_filename=document.original_filename,
        processing_status=document.processing_status,
        extracted_text=document.extracted_text,
    )

@router.post(
    "/{document_id}/chunks",
    response_model=DocumentChunkResponse,
    tags=["Document Processing"],
    summary="Split extracted document text into chunks",
)
def chunk_document_endpoint(
    document_id: int,
    request: DocumentChunkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentChunkResponse:
    chunks = create_document_chunks(
        document_id=document_id,
        current_user_id=current_user.id,
        db=db,
        chunk_size=request.chunk_size,
        chunk_overlap=request.chunk_overlap,
    )

    return DocumentChunkResponse(
        document_id=document_id,
        processing_status="chunked",
        total_chunks=len(chunks),
        chunk_size=request.chunk_size,
        chunk_overlap=request.chunk_overlap,
        chunks=[
            DocumentChunkSummary(
                chunk_id=chunk.id,
                chunk_order=chunk.chunk_order,
                character_count=chunk.character_count,
                word_count=chunk.word_count,
                preview=chunk.chunk_text[:150],
            )
            for chunk in chunks
        ],
    )

@router.get(
    "/{document_id}/chunks",
    tags=["Document Query"],
    summary="Get document chunks",
    description="Returns all stored chunks for a document in chunk order.",
)
def get_document_chunks(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.uploaded_by == current_user.id,
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No chunks found for this document.",
        )

    return {
        "document_id": document.id,
        "original_filename": document.original_filename,
        "processing_status": document.processing_status,
        "total_chunks": len(chunks),
        "chunks": [
            {
                "chunk_id": chunk.id,
                "chunk_order": chunk.chunk_order,
                "character_count": chunk.character_count,
                "word_count": chunk.word_count,
                "chunk_text": chunk.chunk_text,
            }
            for chunk in chunks
        ],
    }

@router.post(
    "/{document_id}/embeddings",
    response_model=DocumentEmbeddingResponse,
    tags=["Document Processing"],
    summary="Generate document chunk embeddings",
    description=(
        "Generates a Gemini embedding for each stored document chunk."
    ),
)
def generate_embeddings_endpoint(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentEmbeddingResponse:
    chunks = generate_document_embeddings(
        document_id=document_id,
        current_user_id=current_user.id,
        db=db,
    )

    embedded_chunks = sum(
        1
        for chunk in chunks
        if chunk.embedding_status == "completed"
    )

    failed_chunks = sum(
        1
        for chunk in chunks
        if chunk.embedding_status == "failed"
    )

    return DocumentEmbeddingResponse(
        document_id=document_id,
        processing_status="embedded",
        total_chunks=len(chunks),
        embedded_chunks=embedded_chunks,
        failed_chunks=failed_chunks,
        embeddings=[
            ChunkEmbeddingSummary(
                chunk_id=chunk.id,
                chunk_order=chunk.chunk_order,
                embedding_status=chunk.embedding_status,
                embedding_model=chunk.embedding_model,
                embedding_dimension=chunk.embedding_dimension,
            )
            for chunk in chunks
        ],
    )

@router.get(
    "/{document_id}/embeddings",
    response_model=DocumentEmbeddingResponse,
    tags=["Document Query"],
    summary="Get document embedding status",
)
def get_document_embeddings(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentEmbeddingResponse:
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.uploaded_by == current_user.id,
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No document chunks found.",
        )

    embedded_chunks = sum(
        1
        for chunk in chunks
        if chunk.embedding_status == "completed"
    )

    failed_chunks = sum(
        1
        for chunk in chunks
        if chunk.embedding_status == "failed"
    )

    return DocumentEmbeddingResponse(
        document_id=document.id,
        processing_status=document.processing_status,
        total_chunks=len(chunks),
        embedded_chunks=embedded_chunks,
        failed_chunks=failed_chunks,
        embeddings=[
            ChunkEmbeddingSummary(
                chunk_id=chunk.id,
                chunk_order=chunk.chunk_order,
                embedding_status=chunk.embedding_status,
                embedding_model=chunk.embedding_model,
                embedding_dimension=chunk.embedding_dimension,
            )
            for chunk in chunks
        ],
    )

@router.post(
    "/{document_id}/vectors",
    response_model=DocumentVectorStoreResponse,
    tags=["Document Processing"],
    summary="Store document vectors",
    description=(
        "Stores completed document chunk embeddings "
        "in ChromaDB."
    ),
)
def store_document_vectors_endpoint(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentVectorStoreResponse:
    chunks = store_document_vectors(
        document_id=document_id,
        current_user_id=current_user.id,
        db=db,
    )

    indexed_chunks = sum(
        1
        for chunk in chunks
        if chunk.vector_store_status == "indexed"
    )

    failed_chunks = sum(
        1
        for chunk in chunks
        if chunk.vector_store_status == "failed"
    )

    return DocumentVectorStoreResponse(
        document_id=document_id,
        processing_status="indexed",
        collection_name=CHROMA_COLLECTION_NAME,
        total_chunks=len(chunks),
        indexed_chunks=indexed_chunks,
        failed_chunks=failed_chunks,
        chunks=[
            ChunkVectorStoreSummary(
                chunk_id=chunk.id,
                chunk_order=chunk.chunk_order,
                vector_id=chunk.vector_id,
                vector_store=chunk.vector_store,
                vector_store_status=(
                    chunk.vector_store_status
                ),
                indexed_at=chunk.indexed_at,
            )
            for chunk in chunks
        ],
    )