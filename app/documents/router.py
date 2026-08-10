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

from app.documents.schemas import (
    DocumentSearchMatch,
    DocumentSearchRequest,
    DocumentSearchResponse,
)
from app.documents.service import (
    distance_to_relevance,
    search_document_chunks,
)

from app.documents.schemas import (
    DocumentAskRequest,
    DocumentAskResponse,
    RAGSource,
)

from app.documents.service import (
    ask_document_question,
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Document"],
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
    """
    Upload a document to the application.

    What it does:
        Accepts a PDF or TXT file.
        Validates filename, extension, MIME type, size, and empty-file cases.
        Generates a safe UUID-based stored filename.
        Saves the file under the configured upload directory.
        Creates a document metadata record in the database.
        Links the document to the currently logged-in user.
        Returns the uploaded document metadata.

    Example:
        POST /documents/upload
        Content-Type: multipart/form-data

    Response:
        {
          "id": 2,
          "original_filename": "pacs008-guide.pdf",
          "content_type": "application/pdf",
          "file_size": 18342,
          "processing_status": "uploaded",
          "uploaded_at": "2026-08-06T10:30:00"
        }

    At this stage, the document is only stored. Text extraction has not run yet.
    """
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
    """
    Extract readable text from an uploaded document.

    What it does for PDFs:
        Opens the stored PDF file.
        Reads each page.
        Extracts readable text.
        Counts pages.
        Handles corrupted, encrypted, or scanned PDFs as extraction failures.

    What it does for TXT files:
        Reads the stored text file using supported encodings.
        Validates that the file contains readable text.

    What it saves in the database:
        extracted_text
        page_count
        processed_at
        processing_status
        error_message, when extraction fails

    Example:
        POST /documents/2/process

    Status flow:
        uploaded -> processing -> completed

    On failure:
        uploaded -> processing -> failed
    """
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
    """
    Return text that has already been extracted from a document.

    What it does:
        Finds the document by ID.
        Verifies that the document belongs to the logged-in user.
        Returns the stored extracted text and processing status.
        Does not extract, regenerate, or modify document text.

    Example:
        GET /documents/2/text

    Response:
        {
          "document_id": 2,
          "original_filename": "pacs008-guide.pdf",
          "processing_status": "completed",
          "extracted_text": "The pacs.008 message is used..."
        }

    This is a read-only endpoint.
    """
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
    """
    Split extracted document text into smaller chunks.

    Why chunks are needed:
        AI models and embedding models work better with smaller focused
        sections than with one very large document body.

    What it does:
        Reads extracted_text from the document record.
        Splits the text into ordered chunks.
        Adds overlap between consecutive chunks.
        Tries to avoid splitting words or sentences unnecessarily.
        Stores each chunk in the document_chunks table.
        Records chunk order, character count, and word count.
        Replaces old chunks if the endpoint is called again.

    Example:
        POST /documents/2/chunks
        Content-Type: application/json

        {
          "chunk_size": 1000,
          "chunk_overlap": 150
        }

    Response:
        {
          "document_id": 2,
          "processing_status": "chunked",
          "total_chunks": 35,
          "chunk_size": 1000,
          "chunk_overlap": 150,
          "chunks": []
        }
    """
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
    """
    Return chunks that were already created for a document.

    What it does:
        Finds the document by ID.
        Verifies that the document belongs to the logged-in user.
        Retrieves stored chunks from the database.
        Orders chunks by chunk_order.
        Returns chunk text and metadata.
        Does not create or regenerate chunks.

    Example:
        GET /documents/2/chunks

    Response:
        {
          "document_id": 2,
          "original_filename": "pacs008-guide.pdf",
          "processing_status": "chunked",
          "total_chunks": 35,
          "chunks": [
            {
              "chunk_id": 48,
              "chunk_order": 1,
              "character_count": 986,
              "word_count": 153,
              "chunk_text": "The pacs.008 message..."
            }
          ]
        }
    """
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
    """
    Generate embeddings for every stored document chunk.

    What it does:
        Reads all chunks for the document.
        Sends each chunk to the configured embedding model.
        Receives a numeric vector for each chunk.
        Temporarily stores the vector in embedding_json.
        Stores the embedding model name and vector dimension.
        Tracks success or failure for each chunk.
        Updates the document processing status when complete.

    Example:
        POST /documents/2/embeddings

    Request body:
        No request body is required.

    Response:
        {
          "document_id": 2,
          "processing_status": "embedded",
          "total_chunks": 35,
          "embedded_chunks": 35,
          "failed_chunks": 0,
          "embeddings": []
        }

    This endpoint creates or regenerates embeddings, so it changes data.
    """
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
    """
    Return the current embedding status for a document.

    What it does:
        Finds the document by ID.
        Verifies that the document belongs to the logged-in user.
        Reads embedding metadata from SQLite.
        Shows which chunks completed or failed.
        Returns model name and vector dimension for each chunk.
        Does not generate embeddings.
        Does not return full embedding vectors.

    Example:
        GET /documents/2/embeddings

    Response:
        {
          "document_id": 2,
          "processing_status": "embedded",
          "total_chunks": 35,
          "embedded_chunks": 35,
          "failed_chunks": 0,
          "embeddings": [
            {
              "chunk_id": 48,
              "chunk_order": 1,
              "embedding_status": "completed",
              "embedding_model": "gemini-embedding-2",
              "embedding_dimension": 768
            }
          ]
        }

    This is a read-only endpoint.
    """
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
    """
    Store generated document embeddings in ChromaDB.

    Difference between embeddings and vectors:
        The embedding is the numeric list generated by the embedding model.
        The vector-storage step indexes that embedding in ChromaDB so it can
        be used for semantic search.

    What it indexes with each vector:
        Chunk text.
        Document ID.
        Chunk ID.
        User ID.
        Original filename.
        Embedding model.
        Vector dimension.

    What it does:
        Verifies that all chunks have completed embeddings.
        Reads embedding_json from each chunk.
        Creates deterministic vector IDs.
        Stores or updates vectors in ChromaDB.
        Updates vector-storage status in SQLite.
        Marks the document as indexed.

    Example:
        POST /documents/2/vectors

    Response:
        {
          "document_id": 2,
          "processing_status": "indexed",
          "collection_name": "payment_document_chunks",
          "total_chunks": 35,
          "indexed_chunks": 35,
          "failed_chunks": 0,
          "chunks": []
        }

    This endpoint prepares the document for semantic search.
    """
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


@router.get(
    "/{document_id}/vectors",
    response_model=DocumentVectorStoreResponse,
    tags=["Document Query"],
    summary="Get document vector-storage status",
)
def get_document_vectors_endpoint(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentVectorStoreResponse:
    """
    Return vector-indexing status for a document.

    What it does:
        Finds the document by ID.
        Verifies that the document belongs to the logged-in user.
        Reads vector-storage status from SQLite.
        Shows how many chunks are indexed or failed.
        Returns vector IDs and the Chroma collection name.
        Does not store vectors again.
        Does not return full embedding vectors.

    Example:
        GET /documents/2/vectors

    Response:
        {
          "document_id": 2,
          "processing_status": "indexed",
          "collection_name": "payment_document_chunks",
          "total_chunks": 35,
          "indexed_chunks": 35,
          "failed_chunks": 0,
          "chunks": []
        }

    Use this endpoint to answer whether a document has been indexed
    successfully.
    """
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
        .filter(
            DocumentChunk.document_id == document.id
        )
        .order_by(DocumentChunk.chunk_order.asc())
        .all()
    )

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No document chunks found.",
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
        document_id=document.id,
        processing_status=document.processing_status,
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

@router.post(
    "/{document_id}/search",
    response_model=DocumentSearchResponse,
    tags=["Document Query"],
    summary="Search relevant document chunks",
    description=(
        "Generates an embedding for the question and "
        "returns the most relevant indexed chunks."
    ),
)
def search_document_endpoint(
    document_id: int,
    request: DocumentSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentSearchResponse:
    result = search_document_chunks(
        document_id=document_id,
        current_user_id=current_user.id,
        question=request.question,
        top_k=request.top_k,
        db=db,
    )

    matches = [
        DocumentSearchMatch(
            vector_id=match.vector_id,
            chunk_id=match.metadata.get("chunk_id"),
            chunk_order=match.metadata.get(
                "chunk_order"
            ),
            text=match.document_text,
            distance=round(match.distance, 6),
            relevance_score=distance_to_relevance(
                match.distance
            ),
        )
        for match in result.matches
    ]

    return DocumentSearchResponse(
        document_id=document_id,
        question=request.question,
        collection_name=result.collection_name,
        total_matches=len(matches),
        matches=matches,
    )

@router.post(
    "/{document_id}/ask",
    response_model=DocumentAskResponse,
    tags=["Document Query"],
    summary="Ask a question about a document",
    description=(
        "Retrieves relevant document chunks from "
        "ChromaDB and uses Gemini to generate a "
        "grounded answer."
    ),
)
def ask_document_endpoint(
    document_id: int,
    request: DocumentAskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
) -> DocumentAskResponse:

    answer, matches = ask_document_question(
        document_id=document_id,
        current_user_id=current_user.id,
        question=request.question,
        top_k=request.top_k,
        db=db,
    )

    sources = [
        RAGSource(
            source_number=index,
            chunk_id=match.metadata.get(
                "chunk_id"
            ),
            chunk_order=match.metadata.get(
                "chunk_order"
            ),
            vector_id=match.vector_id,
            distance=round(
                match.distance,
                6,
            ),
            preview=(
                match.document_text[:250]
            ),
        )
        for index, match in enumerate(
            matches,
            start=1,
        )
    ]

    return DocumentAskResponse(
        document_id=document_id,
        question=request.question,
        answer=answer,
        total_sources=len(sources),
        sources=sources,
    )
