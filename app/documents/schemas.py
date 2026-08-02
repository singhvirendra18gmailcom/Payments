from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentProcessingResponse(BaseModel):
    document_id: int = Field(validation_alias="id")
    original_filename: str
    processing_status: str
    page_count: int | None
    character_count: int
    processed_at: datetime | None
    error_message: str | None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class ExtractedTextResponse(BaseModel):
    document_id: int
    original_filename: str
    processing_status: str
    extracted_text: str | None