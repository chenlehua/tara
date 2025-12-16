"""Report repository."""

from typing import Optional, Tuple

from sqlalchemy.orm import Session
from tara_shared.models import Report


class ReportRepository:
    """Report data access layer."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Report:
        """Create a new report."""
        report = Report(**data)
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_by_id(self, report_id: int) -> Optional[Report]:
        """Get report by ID."""
        return self.db.query(Report).filter(Report.id == report_id).first()

    def list_reports(
        self,
        project_id: int,
        page: int = 1,
        page_size: int = 20,
        status: Optional[int] = None,
    ) -> Tuple[list[Report], int]:
        """List reports with pagination."""
        query = self.db.query(Report).filter(Report.project_id == project_id)

        if status is not None:
            query = query.filter(Report.status == status)

        total = query.count()

        reports = (
            query.order_by(Report.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return reports, total

    def update(self, report: Report, data: dict) -> Report:
        """Update a report."""
        for key, value in data.items():
            if hasattr(report, key):
                setattr(report, key, value)
        self.db.commit()
        self.db.refresh(report)
        return report

    def delete(self, report: Report) -> None:
        """Delete a report."""
        self.db.delete(report)
        self.db.commit()
