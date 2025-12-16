"""Report service."""

import io
import json
from datetime import datetime
from typing import Any, Optional, Tuple

from app.generators import ExcelGenerator, PDFGenerator, WordGenerator
from app.repositories.report_repo import ReportRepository
from sqlalchemy.orm import Session
from tara_shared.constants import ReportStatus
from tara_shared.models import Asset, Project, Report, ThreatRisk
from tara_shared.schemas import ReportCreate, ReportGenerateRequest
from tara_shared.utils import get_logger
from tara_shared.utils.exceptions import NotFoundException

logger = get_logger(__name__)


class ReportService:
    """Report management service."""

    def __init__(self, repo: ReportRepository, db: Optional[Session] = None):
        self.repo = repo
        self.db = db
        self.pdf_generator = PDFGenerator()
        self.word_generator = WordGenerator()
        self.excel_generator = ExcelGenerator()

    async def create_report(self, data: ReportCreate) -> Report:
        """Create a new report record."""
        return self.repo.create(data.model_dump())

    async def get_report(self, report_id: int) -> Report:
        """Get report by ID."""
        report = self.repo.get_by_id(report_id)
        if not report:
            raise NotFoundException("Report", report_id)
        return report

    async def list_reports(
        self,
        project_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
        status: Optional[int] = None,
    ) -> Tuple[list[Report], int]:
        """List reports for a project or all reports if project_id is None."""
        return self.repo.list_reports(
            project_id=project_id,
            page=page,
            page_size=page_size,
            status=status,
        )

    async def list_all_reports(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[int] = None,
    ) -> Tuple[list[Report], int]:
        """List all reports without project filter."""
        return self.repo.list_all_reports(
            page=page,
            page_size=page_size,
            status=status,
        )

    async def delete_report(self, report_id: int) -> None:
        """Delete a report."""
        report = await self.get_report(report_id)
        self.repo.delete(report)

    async def start_report_generation(self, request: ReportGenerateRequest) -> Report:
        """Start report generation process."""
        # Create report record
        report_data = {
            "project_id": request.project_id,
            "name": request.name
            or f"TARA Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "template": request.template or "iso21434",
            "status": ReportStatus.GENERATING.value,
        }
        return self.repo.create(report_data)

    async def run_report_generation(
        self,
        report_id: int,
        request: ReportGenerateRequest,
    ) -> None:
        """Run report generation (background task)."""
        try:
            logger.info(f"Generating report {report_id}...")

            # Collect data (TODO: call other services)
            report_data = await self._collect_report_data(request.project_id)

            # Generate files
            file_paths = {}

            for fmt in request.formats:
                if fmt == "pdf":
                    path = await self._generate_pdf(report_id, report_data, request)
                    file_paths["pdf"] = path
                elif fmt == "docx":
                    path = await self._generate_word(report_id, report_data, request)
                    file_paths["docx"] = path

            # Update report status
            self.repo.update(
                self.repo.get_by_id(report_id),
                {
                    "status": ReportStatus.COMPLETED.value,
                    "file_path": file_paths.get("pdf", ""),
                    "statistics": report_data.get("statistics", {}),
                },
            )

            logger.info(f"Report {report_id} generated successfully")

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            self.repo.update(
                self.repo.get_by_id(report_id),
                {"status": ReportStatus.FAILED.value},
            )

    async def _collect_report_data(self, project_id: int) -> dict:
        """Collect data for report generation from database."""
        # Default data structure
        report_data = {
            "project": {
                "id": project_id,
                "name": "未知项目",
                "vehicle_type": "",
            },
            "assets": [],
            "threats": [],
            "attack_paths": [],
            "control_measures": [],
            "statistics": {
                "total_assets": 0,
                "total_threats": 0,
                "total_attack_paths": 0,
                "total_controls": 0,
                "risk_distribution": {},
            },
        }

        if not self.db:
            logger.warning("No database session available, returning empty data")
            return report_data

        try:
            # Fetch project
            project = self.db.query(Project).filter(Project.id == project_id).first()
            if project:
                report_data["project"] = {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "vehicle_type": project.vehicle_type,
                    "vehicle_model": project.vehicle_model,
                    "standard": project.standard,
                    "scope": project.scope,
                }

            # Fetch assets
            assets = self.db.query(Asset).filter(Asset.project_id == project_id).all()
            report_data["assets"] = [
                {
                    "id": asset.id,
                    "name": asset.name,
                    "asset_type": asset.asset_type,
                    "category": asset.category,
                    "description": asset.description,
                    "security_attrs": asset.security_attrs,
                    "interfaces": asset.interfaces,
                    "criticality": asset.criticality,
                }
                for asset in assets
            ]

            # Fetch threats
            threats = (
                self.db.query(ThreatRisk).filter(ThreatRisk.project_id == project_id).all()
            )
            report_data["threats"] = [
                {
                    "id": threat.id,
                    "threat_name": threat.threat_name,
                    "threat_type": threat.threat_type,
                    "threat_desc": threat.threat_desc,
                    "attack_vector": threat.attack_vector,
                    "likelihood": threat.likelihood,
                    "impact_level": threat.impact_level,
                    "risk_level": threat.risk_level,
                    "asset_id": threat.asset_id,
                }
                for threat in threats
            ]

            # Calculate risk distribution
            risk_distribution = {"CAL-4": 0, "CAL-3": 0, "CAL-2": 0, "CAL-1": 0}
            for threat in threats:
                risk_level = threat.risk_level or "CAL-2"
                if risk_level in risk_distribution:
                    risk_distribution[risk_level] += 1

            # Update statistics
            report_data["statistics"] = {
                "total_assets": len(assets),
                "total_threats": len(threats),
                "total_attack_paths": sum(
                    len(t.attack_paths) if hasattr(t, "attack_paths") and t.attack_paths else 0
                    for t in threats
                ),
                "total_controls": 0,  # TODO: count control measures
                "risk_distribution": risk_distribution,
            }

            logger.info(
                f"Collected report data: {len(assets)} assets, {len(threats)} threats"
            )

        except Exception as e:
            logger.error(f"Failed to collect report data: {e}")

        return report_data

    async def _generate_pdf(
        self,
        report_id: int,
        data: dict,
        request: ReportGenerateRequest,
    ) -> str:
        """Generate PDF report."""
        # TODO: Implement actual PDF generation
        return f"reports/{report_id}/report.pdf"

    async def _generate_word(
        self,
        report_id: int,
        data: dict,
        request: ReportGenerateRequest,
    ) -> str:
        """Generate Word report."""
        # TODO: Implement actual Word generation
        return f"reports/{report_id}/report.docx"

    async def get_report_file(
        self,
        report_id: int,
        format: str,
    ) -> Tuple[io.BytesIO, str]:
        """Get report file for download."""
        report = await self.get_report(report_id)

        # Try to get file from MinIO if path exists
        if report.file_path:
            try:
                from tara_shared.database.minio import storage_service

                if storage_service.is_available():
                    file_data = storage_service.get_object(
                        bucket_name="reports",
                        object_name=report.file_path,
                    )
                    if file_data:
                        buffer = io.BytesIO(file_data)
                        filename = f"{report.name}.{format}"
                        return buffer, filename
            except Exception as e:
                logger.warning(f"Failed to get file from MinIO: {e}")

        # If no file in storage, generate on the fly from stored content
        if report.content:
            try:
                if format == "pdf":
                    buffer = await self._generate_pdf_from_content(report)
                elif format == "docx":
                    buffer = await self._generate_word_from_content(report)
                elif format == "xlsx":
                    buffer = await self._generate_excel_from_content(report)
                else:
                    buffer = io.BytesIO(
                        json.dumps(report.content, ensure_ascii=False, indent=2).encode(
                            "utf-8"
                        )
                    )
                filename = f"{report.name}.{format}"
                return buffer, filename
            except Exception as e:
                logger.error(f"Failed to generate report file: {e}")

        # Fallback: return JSON with report info
        content = {
            "id": report.id,
            "name": report.name,
            "status": report.status,
            "statistics": report.statistics or {},
            "content": report.content or {},
            "message": "报告文件正在生成中，请稍后重试",
        }
        buffer = io.BytesIO(json.dumps(content, ensure_ascii=False, indent=2).encode("utf-8"))
        filename = f"{report.name}.json"

        return buffer, filename

    async def _generate_pdf_from_content(self, report: Report) -> io.BytesIO:
        """Generate PDF from stored report content."""
        try:
            content = report.content or {}
            data = {
                "content": content,
                "project": content.get("project", {"name": report.name}),
                "assets": content.get("assets", []),
                "threats": content.get("threats", []),
                "statistics": report.statistics or {},
            }
            # Generate PDF using the generator's generate method
            buffer = await self.pdf_generator.generate(
                data=data,
                template=report.template or "iso21434",
            )
            return buffer
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return io.BytesIO(b"PDF generation failed")

    async def _generate_word_from_content(self, report: Report) -> io.BytesIO:
        """Generate Word document from stored report content."""
        try:
            content = report.content or {}
            data = {
                "content": content,
                "project": content.get("project", {"name": report.name}),
                "assets": content.get("assets", []),
                "threats": content.get("threats", []),
                "statistics": report.statistics or {},
            }
            # Generate Word using the generator's generate method
            buffer = await self.word_generator.generate(
                data=data,
                template=report.template or "iso21434",
            )
            return buffer
        except Exception as e:
            logger.error(f"Word generation failed: {e}")
            return io.BytesIO(b"Word generation failed")

    async def _generate_excel_from_content(self, report: Report) -> io.BytesIO:
        """Generate Excel document from stored report content."""
        try:
            content = report.content or {}
            data = {
                "content": content,
                "project": content.get("project", {"name": report.name}),
                "assets": content.get("assets", []),
                "threats": content.get("threats", []),
                "statistics": report.statistics or {},
            }
            # Generate Excel using the generator's generate method
            buffer = await self.excel_generator.generate(
                data=data,
                template=report.template or "iso21434",
            )
            return buffer
        except Exception as e:
            logger.error(f"Excel generation failed: {e}")
            return io.BytesIO(b"Excel generation failed")

    async def get_report_preview(self, report_id: int) -> dict:
        """Get report preview data."""
        report = await self.get_report(report_id)

        # Extract content from stored report data
        content = report.content or {}
        sections = report.sections or []

        # If no sections stored, generate from content
        if not sections and content:
            sections = [
                {"id": "assets", "title": "资产清单", "count": len(content.get("assets", []))},
                {"id": "threats", "title": "威胁分析", "count": len(content.get("threats", []))},
                {"id": "risks", "title": "风险评估", "count": len(content.get("threats", []))},
            ]

        return {
            "id": report.id,
            "name": report.name,
            "template": report.template,
            "status": report.status,
            "statistics": report.statistics or {},
            "sections": sections,
            "content": content,
        }
