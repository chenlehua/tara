"""Report endpoints."""

import json
import uuid
from datetime import datetime
from typing import List, Optional

from app.repositories.report_repo import ReportRepository
from app.services.oneclick_service import OneClickGenerateService
from app.services.report_service import ReportService
from fastapi import (APIRouter, BackgroundTasks, Depends, File, Form, Query,
                     UploadFile)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from tara_shared.database import get_db
from tara_shared.schemas import (GenerationProgressResponse,
                                 OneClickGenerateRequest,
                                 OneClickGenerateResponse, ReportCreate,
                                 ReportGenerateRequest, ReportListResponse,
                                 ReportResponse, ReportUpdate)
from tara_shared.utils import paginated_response, success_response

router = APIRouter()

# In-memory task storage (should be Redis in production)
_generation_tasks = {}


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
    return success_response(
        {
            "report_id": report.id,
            "message": "Report generation started",
        }
    )


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


def get_oneclick_service(db: Session = Depends(get_db)) -> OneClickGenerateService:
    """Get one-click generate service instance."""
    return OneClickGenerateService(db)


@router.post("/oneclick")
async def oneclick_generate(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(..., description="上传的文件列表"),
    template: str = Form(default="full", description="报告模板"),
    prompt: str = Form(default="", description="分析提示词"),
    project_name: Optional[str] = Form(default=None, description="项目名称"),
    service: OneClickGenerateService = Depends(get_oneclick_service),
):
    """
    一键生成TARA报告

    支持上传:
    - 资产清单文件: .xlsx, .xls, .csv, .json
    - 系统架构图: .png, .jpg, .jpeg, .svg
    - 配置文档: .pdf
    """
    # Generate task ID
    task_id = str(uuid.uuid4())

    # Create project name
    if not project_name:
        project_name = f"TARA分析项目_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Initialize task status
    _generation_tasks[task_id] = {
        "status": "processing",
        "progress": 0,
        "current_step": "初始化",
        "steps": [
            {"label": "解析文件", "completed": False, "active": True},
            {"label": "识别资产", "completed": False, "active": False},
            {"label": "威胁分析", "completed": False, "active": False},
            {"label": "风险评估", "completed": False, "active": False},
            {"label": "生成报告", "completed": False, "active": False},
        ],
        "result": None,
        "error": None,
    }

    # Start background task
    result = await service.start_generation(
        task_id=task_id,
        files=files,
        template=template,
        prompt=prompt,
        project_name=project_name,
        task_storage=_generation_tasks,
    )

    # Add background processing
    background_tasks.add_task(
        service.run_generation,
        task_id=task_id,
        project_id=result["project_id"],
        report_id=result["report_id"],
        file_paths=result["file_paths"],
        template=template,
        prompt=prompt,
        task_storage=_generation_tasks,
    )

    return success_response(
        {
            "task_id": task_id,
            "report_id": result["report_id"],
            "project_id": result["project_id"],
            "status": "processing",
            "message": "报告生成已启动",
        }
    )


@router.get("/oneclick/{task_id}/progress")
async def get_generation_progress(task_id: str):
    """获取报告生成进度"""
    if task_id not in _generation_tasks:
        return success_response(
            {
                "task_id": task_id,
                "status": "not_found",
                "progress": 0,
                "error": "任务不存在",
            }
        )

    return success_response(_generation_tasks[task_id])
