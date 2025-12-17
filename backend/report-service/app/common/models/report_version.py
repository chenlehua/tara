"""
Report Version Models
=====================

SQLAlchemy models for report version management.
"""

from sqlalchemy import (
    JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
)
from sqlalchemy.orm import relationship

from .base import BaseModel


class ReportVersion(BaseModel):
    """Report version model for version control."""

    __tablename__ = "report_versions"

    report_id = Column(
        Integer,
        ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Version identification
    version_number = Column(String(20), nullable=False)  # "1.0", "1.1", "2.0"
    major_version = Column(Integer, nullable=False, default=1)
    minor_version = Column(Integer, nullable=False, default=0)

    # Version content (complete snapshot)
    content = Column(JSON, default=dict)  # Report content snapshot
    statistics = Column(JSON, default=dict)  # Statistics snapshot
    sections = Column(JSON, default=list)  # Sections list snapshot
    snapshot_data = Column(JSON, default=dict)  # Full data snapshot (assets, threats, measures)

    # Version metadata
    change_summary = Column(Text, nullable=True)  # Change summary
    change_reason = Column(String(500), nullable=True)  # Change reason
    created_by = Column(String(100), nullable=True)  # Creator
    approved_by = Column(String(100), nullable=True)  # Approver
    approved_at = Column(DateTime, nullable=True)  # Approval time

    # Version status
    status = Column(String(20), default="draft")  # draft, review, approved, deprecated
    is_baseline = Column(Boolean, default=False)  # Is baseline version
    is_current = Column(Boolean, default=False)  # Is current version

    # File information
    file_paths = Column(JSON, default=dict)  # {pdf: "", docx: "", xlsx: ""}

    # Relationships
    report = relationship("Report", back_populates="versions")
    changes = relationship(
        "ReportVersionChange",
        back_populates="version",
        cascade="all, delete-orphan",
        order_by="ReportVersionChange.created_at"
    )

    def __repr__(self) -> str:
        return f"<ReportVersion(id={self.id}, report_id={self.report_id}, version='{self.version_number}')>"


class ReportVersionChange(BaseModel):
    """Report version change record for tracking modifications."""

    __tablename__ = "report_version_changes"

    version_id = Column(
        Integer,
        ForeignKey("report_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Change type
    change_type = Column(String(20), nullable=False)  # add, modify, delete
    entity_type = Column(String(50), nullable=False)  # asset, threat, measure, project_info
    entity_id = Column(Integer, nullable=True)  # Entity ID
    entity_name = Column(String(200), nullable=True)  # Entity name for display

    # Change details
    field_name = Column(String(100), nullable=True)  # Changed field
    old_value = Column(Text, nullable=True)  # Old value (JSON format)
    new_value = Column(Text, nullable=True)  # New value (JSON format)

    # Relationship
    version = relationship("ReportVersion", back_populates="changes")

    def __repr__(self) -> str:
        return f"<ReportVersionChange(id={self.id}, type='{self.change_type}', entity='{self.entity_type}')>"
