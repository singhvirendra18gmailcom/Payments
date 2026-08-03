from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base
from sqlalchemy.orm import relationship

class Document(Base):
    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    original_filename = Column(
        String,
        nullable=False,
    )

    stored_filename = Column(
        String,
        unique=True,
        nullable=False,
    )

    file_path = Column(
        String,
        nullable=False,
    )

    content_type = Column(
        String,
        nullable=False,
    )

    file_extension = Column(
        String,
        nullable=False,
    )

    file_size = Column(
        Integer,
        nullable=False,
    )

    processing_status = Column(
        String,
        nullable=False,
        default="uploaded",
    )
    extracted_text = Column(
        Text,
        nullable=True,
    )
    page_count = Column(
        Integer,
        nullable=True,
    )

    error_message = Column(
        Text,
        nullable=True,
    )

    uploaded_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    processed_at = Column(
        DateTime,
        nullable=True,
    )

    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )

    owner = relationship("User")
