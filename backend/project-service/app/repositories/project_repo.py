"""
Project Repository
==================

Data access layer for Project entity.
"""

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from tara_shared.models import Asset, Document, Project, Report, ThreatRisk


class ProjectRepository:
    """Repository for Project data access."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, project: Project) -> Project:
        """Create a new project."""
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        return self.db.query(Project).filter(Project.id == project_id).first()

    def get_by_name(self, name: str) -> Optional[Project]:
        """Get project by name."""
        return self.db.query(Project).filter(Project.name == name).first()

    def list_projects(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        status: Optional[int] = None,
    ) -> Tuple[List[Project], int]:
        """
        List projects with pagination and filtering.

        Returns:
            Tuple of (projects list, total count)
        """
        query = self.db.query(Project)

        # Apply filters
        if keyword:
            query = query.filter(
                or_(
                    Project.name.ilike(f"%{keyword}%"),
                    Project.description.ilike(f"%{keyword}%"),
                    Project.vehicle_type.ilike(f"%{keyword}%"),
                )
            )

        if status is not None:
            query = query.filter(Project.status == status)

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        offset = (page - 1) * page_size
        projects = (
            query.order_by(Project.updated_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return projects, total

    def update(self, project: Project) -> Project:
        """Update a project."""
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project: Project) -> None:
        """Delete a project."""
        self.db.delete(project)
        self.db.commit()

    def get_stats(self, project_id: int) -> Dict[str, Any]:
        """Get project statistics."""
        # Document count
        doc_count = (
            self.db.query(func.count(Document.id))
            .filter(Document.project_id == project_id)
            .scalar()
        )

        # Asset count
        asset_count = (
            self.db.query(func.count(Asset.id))
            .filter(Asset.project_id == project_id)
            .scalar()
        )

        # Threat counts by risk level
        threat_query = (
            self.db.query(ThreatRisk.risk_level, func.count(ThreatRisk.id))
            .filter(ThreatRisk.project_id == project_id)
            .group_by(ThreatRisk.risk_level)
            .all()
        )

        threat_count = sum(count for _, count in threat_query)
        risk_counts = {level: count for level, count in threat_query if level}

        # Report count
        report_count = (
            self.db.query(func.count(Report.id))
            .filter(Report.project_id == project_id)
            .scalar()
        )

        return {
            "document_count": doc_count or 0,
            "asset_count": asset_count or 0,
            "threat_count": threat_count or 0,
            "report_count": report_count or 0,
            "critical_risk_count": risk_counts.get("critical", 0),
            "high_risk_count": risk_counts.get("high", 0),
            "medium_risk_count": risk_counts.get("medium", 0),
            "low_risk_count": risk_counts.get("low", 0),
            "negligible_risk_count": risk_counts.get("negligible", 0),
        }

    def exists(self, project_id: int) -> bool:
        """Check if project exists."""
        return (
            self.db.query(func.count(Project.id))
            .filter(Project.id == project_id)
            .scalar()
            > 0
        )
