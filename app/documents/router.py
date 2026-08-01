from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.auth import get_db
from app.models import User
from app.schemas import DocumentUploadResponse
from app.auth import get_current_user

from .service import upload_document


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