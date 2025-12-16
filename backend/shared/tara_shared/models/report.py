"""
Report Model
============

SQLAlchemy model for Report entity.
"""

from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseModel


class Report(BaseModel):
    """Report model for TARA analysis reports."""
    
    __tablename__ = "reports"
    
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(200), nullable=False, index=True)
    report_type = Column(String(50), default="tara")  # tara, threat, risk, measure
    description = Column(Text, nullable=True)
    template = Column(String(50), nullable=True)  # iso21434_tara, simple, custom
    
    # Generation status
    status = Column(Integer, default=0)  # 0: pending, 1: generating, 2: completed, 3: failed
    progress = Column(Integer, default=0)  # 0-100
    error_message = Column(Text, nullable=True)
    
    # File info
    file_path = Column(String(500), nullable=True)
    file_format = Column(String(20), nullable=True)  # pdf, docx, html, xlsx
    file_size = Column(Integer, nullable=True)
    
    # Content and sections
    content = Column(JSON, default=dict)  # Generated content data
    sections = Column(JSON, default=list)  # List of sections
    
    # Metadata
    version = Column(String(20), default="1.0")
    author = Column(String(100), nullable=True)
    reviewer = Column(String(100), nullable=True)
    review_status = Column(Integer, default=0)  # 0: draft, 1: in_review, 2: approved
    
    # Statistics
    statistics = Column(JSON, default=dict)
    
    # Relationship
    project = relationship("Project", back_populates="reports")
    
    def __repr__(self) -> str:
        return f"<Report(id={self.id}, name='{self.name}', status={self.status})>"
