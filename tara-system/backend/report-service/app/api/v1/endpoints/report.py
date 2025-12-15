"""Report endpoints."""
from typing import Optional

from fastapi import APIRouter, Depends, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from tara_shared.database import get_db
from tara_shared.schemas import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportListResponse,
    ReportGenerateRequest,
)
from tara_shared.utils import success_response, paginated_response

from app.services.report_service import ReportService
from app.repositories.report_repo import ReportRepository

router = APIRouter()


def get_report_service(db: Session = Depends(get_db)) -> ReportService:
    """Get report service instance."""
    return ReportService(ReportRepository(db))


@router.post("")
async def create_report(
    data: ReportCreate,
    service: ReportService = Depends(get_report_service),
):
    """Create a new report record."""
    report = await service.create_report(data)
    return success_response(ReportResponse.model_validate(report))


@router.get("")
async def list_reports(
    project_id: int = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[int] = None,
    service: ReportService = Depends(get_report_service),
):
    """List reports for a project."""
    reports, total = await service.list_reports(
        project_id=project_id,
        page=page,
        page_size=page_size,
        status=status,
    )
    return paginated_response(
        items=[ReportResponse.model_validate(r) for r in reports],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{report_id}")
async def get_report(
    report_id: int,
    service: ReportService = Depends(get_report_service),
):
    """Get report by ID."""
    report = await service.get_report(report_id)
    return success_response(ReportResponse.model_validate(report))


@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    service: ReportService = Depends(get_report_service),
):
    """Delete a report."""
    await service.delete_report(report_id)
    return success_response({"message": "Report deleted"})


@router.post("/generate")
async def generate_report(
    request: ReportGenerateRequest,
    background_tasks: BackgroundTasks,
    service: ReportService = Depends(get_report_service),
):
    """Generate a new report (async)."""
    report = await service.start_report_generation(request)
    background_tasks.add_task(service.run_report_generation, report.id, request)
    return success_response({
        "report_id": report.id,
        "message": "Report generation started",
    })


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    format: str = Query("pdf", regex="^(pdf|docx|xlsx)$"),
    service: ReportService = Depends(get_report_service),
):
    """Download report file."""
    file_data, filename = await service.get_report_file(report_id, format)
    
    media_types = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
    
    return StreamingResponse(
        file_data,
        media_type=media_types.get(format, "application/octet-stream"),
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/{report_id}/preview")
async def preview_report(
    report_id: int,
    service: ReportService = Depends(get_report_service),
):
    """Get report preview data."""
    preview = await service.get_report_preview(report_id)
    return success_response(preview)
