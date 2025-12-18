"""
Project Model
=============

SQLAlchemy model for Project entity.
"""

from sqlalchemy import JSON, Column, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel


class Project(BaseModel):
    """Project model for TARA analysis projects."""

    __tablename__ = "projects"

    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    vehicle_type = Column(String(50), nullable=True)
    vehicle_model = Column(String(100), nullable=True)
    vehicle_year = Column(String(10), nullable=True)
    standard = Column(String(50), default="ISO/SAE 21434")
    scope = Column(Text, nullable=True)
    status = Column(
        Integer, default=0
    )  # 0: draft, 1: in_progress, 2: completed, 3: archived
    owner = Column(String(100), nullable=True)
    team = Column(JSON, default=list)  # List of team members
    config = Column(JSON, default=dict)  # Project configuration
    tags = Column(JSON, default=list)  # Tags for categorization

    # Relationships
    documents = relationship(
        "Document", back_populates="project", cascade="all, delete-orphan"
    )
    assets = relationship(
        "Asset", back_populates="project", cascade="all, delete-orphan"
    )
    threat_risks = relationship(
        "ThreatRisk", back_populates="project", cascade="all, delete-orphan"
    )
    reports = relationship(
        "Report", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}')>"
