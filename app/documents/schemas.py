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

class DocumentChunkRequest(BaseModel):
    chunk_size: int = Field(
        default=1000,
        ge=200,
        le=5000,
    )

    chunk_overlap: int = Field(
        default=150,
        ge=0,
        le=1000,
    )


class DocumentChunkSummary(BaseModel):
    chunk_id: int
    chunk_order: int
    character_count: int
    word_count: int
    preview: str


class DocumentChunkResponse(BaseModel):
    document_id: int
    processing_status: str
    total_chunks: int
    chunk_size: int
    chunk_overlap: int
    chunks: list[DocumentChunkSummary]