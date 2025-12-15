"""Report service."""
import io
from datetime import datetime
from typing import Optional, Tuple, Any

from tara_shared.models import Report
from tara_shared.schemas import ReportCreate, ReportGenerateRequest
from tara_shared.constants import ReportStatus
from tara_shared.utils import get_logger
from tara_shared.utils.exceptions import NotFoundException

from app.repositories.report_repo import ReportRepository
from app.generators import PDFGenerator, WordGenerator

logger = get_logger(__name__)


class ReportService:
    """Report management service."""

    def __init__(self, repo: ReportRepository):
        self.repo = repo
        self.pdf_generator = PDFGenerator()
        self.word_generator = WordGenerator()

    async def create_report(self, data: ReportCreate) -> Report:
        """Create a new report record."""
        return self.repo.create(data.model_dump())

    async def get_report(self, report_id: int) -> Report:
        """Get report by ID."""
        report = self.repo.get_by_id(report_id)
        if not report:
            raise NotFoundException(f"Report {report_id} not found")
        return report

    async def list_reports(
        self,
        project_id: int,
        page: int = 1,
        page_size: int = 20,
        status: Optional[int] = None,
    ) -> Tuple[list[Report], int]:
        """List reports for a project."""
        return self.repo.list_reports(
            project_id=project_id,
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
            "name": request.name or f"TARA Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
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
        """Collect data for report generation."""
        # TODO: Call other services to collect data
        return {
            "project": {
                "id": project_id,
                "name": "示例项目",
                "vehicle_type": "BEV",
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
        
        # TODO: Download from MinIO
        buffer = io.BytesIO(b"Report content placeholder")
        filename = f"{report.name}.{format}"
        
        return buffer, filename

    async def get_report_preview(self, report_id: int) -> dict:
        """Get report preview data."""
        report = await self.get_report(report_id)
        
        return {
            "id": report.id,
            "name": report.name,
            "template": report.template,
            "status": report.status,
            "statistics": report.statistics or {},
            "sections": [],  # TODO: Load section previews
        }
