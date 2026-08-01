from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.documents.models import Document

from .config import (
    ALLOWED_CONTENT_TYPES,
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE,
    READ_CHUNK_SIZE,
    UPLOAD_DIRECTORY,
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
