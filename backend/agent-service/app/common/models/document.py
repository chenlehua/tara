"""
Document Model
==============

SQLAlchemy model for Document entity.
"""

from sqlalchemy import JSON, BigInteger, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel


class Document(BaseModel):
    """Document model for uploaded files."""

    __tablename__ = "documents"

    project_id = Column(
        BigInteger,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    file_type = Column(String(50), nullable=True)  # MIME type
    file_extension = Column(String(20), nullable=True)
    doc_type = Column(String(50), nullable=True)  # Document category type
    doc_category = Column(String(50), nullable=True)

    # Parsing status
    parse_status = Column(
        Integer, default=0
    )  # 0: pending, 1: parsing, 2: completed, 3: failed
    parse_progress = Column(Integer, default=0)  # 0-100
    parse_error = Column(Text, nullable=True)

    # Extracted content
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    structure = Column(JSON, default=dict)
    doc_metadata = Column(
        JSON, default=dict
    )  # renamed from 'metadata' (reserved by SQLAlchemy)
    ocr_result = Column(JSON, default=dict)
    page_count = Column(Integer, nullable=True)

    # Relationship
    project = relationship("Project", back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename='{self.filename}')>"
