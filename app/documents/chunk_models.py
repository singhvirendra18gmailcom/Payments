from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text , String
from sqlalchemy.orm import relationship

from app.database import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chunk_order = Column(
        Integer,
        nullable=False,
    )

    chunk_text = Column(
        Text,
        nullable=False,
    )

    character_count = Column(
        Integer,
        nullable=False,
    )

    word_count = Column(
        Integer,
        nullable=False,
    )
    # Temporary storage until ChromaDB is added in Issue 6.
    embedding_json = Column(
        Text,
        nullable=True,
    )

    embedding_model = Column(
        String,
        nullable=True,
    )

    embedding_dimension = Column(
        Integer,
        nullable=True,
    )

    embedding_status = Column(
        String,
        nullable=False,
        default="pending",
    )

    embedding_error = Column(
        Text,
        nullable=True,
    )

    embedded_at = Column(
        DateTime,
        nullable=True,
    )
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    document = relationship(
        "Document",
        back_populates="chunks",
    )