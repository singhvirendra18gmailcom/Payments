from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_db
from app.models import User
from app.schemas import DocumentUploadResponse
from app.auth import get_current_user
from .models import Document

from .service import upload_document
from app.documents.schemas import DocumentProcessingResponse
from app.documents.schemas import ExtractedTextResponse
from app.documents.service import process_document_text

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
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