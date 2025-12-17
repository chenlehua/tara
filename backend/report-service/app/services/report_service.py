"""Report service."""

import io
import json
from datetime import datetime
from typing import Any, Optional, Tuple

from app.generators import ExcelGenerator, PDFGenerator, WordGenerator
from app.repositories.report_repo import ReportRepository
from sqlalchemy.orm import Session
from app.common.constants import ReportStatus
from app.common.models import Asset, AttackPath, ControlMeasure, Project, Report, ThreatRisk
from app.common.schemas import ReportCreate, ReportGenerateRequest
from app.common.utils import get_logger
from app.common.utils.exceptions import NotFoundException

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
            
            # Create asset name lookup for threat display
            asset_name_map = {asset.id: asset.name for asset in assets}

            # Fetch threats with related data
            threats = (
                self.db.query(ThreatRisk).filter(ThreatRisk.project_id == project_id).all()
            )
            
            # Collect all threat IDs for fetching related data
            threat_ids = [t.id for t in threats]
            
            # Fetch attack paths for all threats
            attack_paths = []
            attack_path_ids = []
            if threat_ids:
                attack_paths = (
                    self.db.query(AttackPath)
                    .filter(AttackPath.threat_risk_id.in_(threat_ids))
                    .all()
                )
                attack_path_ids = [ap.id for ap in attack_paths]
            
            # Fetch control measures (linked via attack_path or directly to threat)
            control_measures = []
            if attack_path_ids or threat_ids:
                # Get measures linked via attack paths
                if attack_path_ids:
                    measures_via_path = (
                        self.db.query(ControlMeasure)
                        .filter(ControlMeasure.attack_path_id.in_(attack_path_ids))
                        .all()
                    )
                    control_measures.extend(measures_via_path)
                
                # Get measures linked directly to threats
                measures_via_threat = (
                    self.db.query(ControlMeasure)
                    .filter(ControlMeasure.threat_risk_id.in_(threat_ids))
                    .all()
                )
                # Avoid duplicates
                existing_measure_ids = {m.id for m in control_measures}
                for m in measures_via_threat:
                    if m.id not in existing_measure_ids:
                        control_measures.append(m)
            
            # Build attack path lookup by threat_risk_id
            attack_path_by_threat = {}
            for ap in attack_paths:
                if ap.threat_risk_id not in attack_path_by_threat:
                    attack_path_by_threat[ap.threat_risk_id] = []
                attack_path_by_threat[ap.threat_risk_id].append(ap)
            
            # Build control measure lookup by attack_path_id and threat_risk_id
            measures_by_attack_path = {}
            measures_by_threat = {}
            for m in control_measures:
                if m.attack_path_id:
                    if m.attack_path_id not in measures_by_attack_path:
                        measures_by_attack_path[m.attack_path_id] = []
                    measures_by_attack_path[m.attack_path_id].append(m)
                if m.threat_risk_id:
                    if m.threat_risk_id not in measures_by_threat:
                        measures_by_threat[m.threat_risk_id] = []
                    measures_by_threat[m.threat_risk_id].append(m)
            
            # Build threats with enriched data
            report_data["threats"] = [
                {
                    "id": threat.id,
                    "name": threat.threat_name,  # Alias for Excel generator compatibility
                    "threat_name": threat.threat_name,
                    "threat_type": threat.threat_type,
                    "threat_desc": threat.threat_desc,
                    "description": threat.threat_desc,  # Alias
                    "attack_vector": threat.attack_vector,
                    "attack_path": self._format_attack_path(
                        attack_path_by_threat.get(threat.id, [])
                    ),
                    "likelihood": threat.likelihood,
                    "safety_impact": threat.safety_impact or 0,
                    "financial_impact": threat.financial_impact or 0,
                    "operational_impact": threat.operational_impact or 0,
                    "privacy_impact": threat.privacy_impact or 0,
                    "impact_level": threat.impact_level or 0,
                    "risk_level": threat.risk_level or "CAL-2",
                    "asset_id": threat.asset_id,
                    "asset_name": asset_name_map.get(threat.asset_id, ""),
                    "wp29_ref": self._get_wp29_ref(threat.threat_type),
                    "iso_clause": self._get_iso_clause(threat.threat_type),
                }
                for threat in threats
            ]
            
            # Build control measures list with threat references
            report_data["control_measures"] = [
                {
                    "id": m.id,
                    "name": m.name,
                    "control_type": m.control_type,
                    "category": m.category,
                    "description": m.description,
                    "implementation": m.implementation,
                    "effectiveness": m.effectiveness,
                    "iso21434_ref": m.iso21434_ref,
                    "threat_id": m.threat_risk_id,
                    "threat_risk_id": m.threat_risk_id,
                    "attack_path_id": m.attack_path_id,
                }
                for m in control_measures
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
                "total_attack_paths": len(attack_paths),
                "total_controls": len(control_measures),
                "risk_distribution": risk_distribution,
            }

            logger.info(
                f"Collected report data: {len(assets)} assets, {len(threats)} threats, "
                f"{len(attack_paths)} attack paths, {len(control_measures)} control measures"
            )

        except Exception as e:
            logger.error(f"Failed to collect report data: {e}")
            import traceback
            logger.error(traceback.format_exc())

        return report_data
    
    def _format_attack_path(self, attack_paths: list) -> str:
        """Format attack paths into a display string."""
        if not attack_paths:
            return "-"
        # Use the first attack path's description or name
        ap = attack_paths[0]
        if hasattr(ap, 'description') and ap.description:
            return ap.description[:30]
        if hasattr(ap, 'name') and ap.name:
            return ap.name[:30]
        return "-"
    
    def _get_wp29_ref(self, threat_type: str) -> str:
        """Get WP.29 reference for threat type."""
        wp29_map = {
            "S": "4.3.1",  # Spoofing
            "T": "5.1.1",  # Tampering
            "R": "5.2.1",  # Repudiation
            "I": "4.3.3",  # Information Disclosure
            "D": "4.3.4",  # Denial of Service
            "E": "4.3.5",  # Elevation of Privilege
        }
        return wp29_map.get(threat_type, "4.3.1")
    
    def _get_iso_clause(self, threat_type: str) -> str:
        """Get ISO 21434 clause reference for threat type."""
        iso_map = {
            "S": "9.4",   # Spoofing
            "T": "9.5",   # Tampering
            "R": "9.9",   # Repudiation
            "I": "9.6",   # Information Disclosure
            "D": "9.7",   # Denial of Service
            "E": "9.8",   # Elevation of Privilege
        }
        return iso_map.get(threat_type, "9.4")

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
                from app.common.database.minio import storage_service

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
