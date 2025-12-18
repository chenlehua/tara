"""
Report Version API Endpoints
============================

API endpoints for report version management.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.common.database import get_db
from app.common.schemas import (
    APIResponse,
    ApproveVersionRequest,
    ReportVersionCreate,
    ReportVersionDetailResponse,
    ReportVersionListResponse,
    ReportVersionResponse,
    RollbackRequest,
    SetBaselineRequest,
    VersionCompareRequest,
    VersionCompareResponse,
)
from app.common.schemas.report_version import ReportVersionChangeResponse
from app.common.utils import get_logger
from app.common.utils.exceptions import NotFoundException
from app.services import ReportVersionService

logger = get_logger(__name__)
router = APIRouter()


@router.get(
    "/{report_id}/versions",
    response_model=APIResponse,
    summary="获取报告版本列表",
)
async def list_versions(
    report_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all versions for a report."""
    service = ReportVersionService(db)
    
    versions, total = service.list_versions(
        report_id=report_id,
        page=page,
        page_size=page_size,
    )
    
    current_version = service.get_current_version(report_id)
    baseline_version = service.get_baseline_version(report_id)
    
    return APIResponse(
        success=True,
        code=200,
        message="获取版本列表成功",
        data=ReportVersionListResponse(
            versions=[
                ReportVersionResponse(
                    id=v.id,
                    report_id=v.report_id,
                    version_number=v.version_number,
                    major_version=v.major_version,
                    minor_version=v.minor_version,
                    status=v.status,
                    is_baseline=v.is_baseline,
                    is_current=v.is_current,
                    change_summary=v.change_summary,
                    change_reason=v.change_reason,
                    created_by=v.created_by,
                    approved_by=v.approved_by,
                    approved_at=v.approved_at,
                    created_at=v.created_at,
                    statistics=v.statistics,
                )
                for v in versions
            ],
            total=total,
            current_version=current_version.version_number if current_version else None,
            baseline_version=baseline_version.version_number if baseline_version else None,
        ).model_dump()
    )


@router.post(
    "/{report_id}/versions",
    response_model=APIResponse,
    summary="创建新版本",
)
async def create_version(
    report_id: int,
    request: ReportVersionCreate,
    db: Session = Depends(get_db),
):
    """Create a new version for a report."""
    service = ReportVersionService(db)
    
    try:
        version = service.create_version(
            report_id=report_id,
            is_major=request.is_major,
            change_summary=request.change_summary,
            change_reason=request.change_reason,
            created_by=request.created_by,
        )
        
        return APIResponse(
            success=True,
            code=200,
            message=f"创建版本 {version.version_number} 成功",
            data=ReportVersionResponse(
                id=version.id,
                report_id=version.report_id,
                version_number=version.version_number,
                major_version=version.major_version,
                minor_version=version.minor_version,
                status=version.status,
                is_baseline=version.is_baseline,
                is_current=version.is_current,
                change_summary=version.change_summary,
                change_reason=version.change_reason,
                created_by=version.created_by,
                approved_by=version.approved_by,
                approved_at=version.approved_at,
                created_at=version.created_at,
                statistics=version.statistics,
            ).model_dump()
        )
    except NotFoundException as e:
        return APIResponse(
            success=False,
            code=404,
            message=str(e),
            data=None
        )


@router.get(
    "/{report_id}/versions/{version_number}",
    response_model=APIResponse,
    summary="获取版本详情",
)
async def get_version(
    report_id: int,
    version_number: str,
    db: Session = Depends(get_db),
):
    """Get a specific version's details."""
    service = ReportVersionService(db)
    
    version = service.get_version(report_id, version_number)
    if not version:
        return APIResponse(
            success=False,
            code=404,
            message=f"版本 {version_number} 不存在",
            data=None
        )
    
    # Get changes for this version
    changes = [
        ReportVersionChangeResponse(
            id=c.id,
            version_id=c.version_id,
            change_type=c.change_type,
            entity_type=c.entity_type,
            entity_id=c.entity_id,
            entity_name=c.entity_name,
            field_name=c.field_name,
            old_value=c.old_value,
            new_value=c.new_value,
            created_at=c.created_at,
        )
        for c in version.changes
    ]
    
    return APIResponse(
        success=True,
        code=200,
        message="获取版本详情成功",
        data=ReportVersionDetailResponse(
            id=version.id,
            report_id=version.report_id,
            version_number=version.version_number,
            major_version=version.major_version,
            minor_version=version.minor_version,
            status=version.status,
            is_baseline=version.is_baseline,
            is_current=version.is_current,
            change_summary=version.change_summary,
            change_reason=version.change_reason,
            created_by=version.created_by,
            approved_by=version.approved_by,
            approved_at=version.approved_at,
            created_at=version.created_at,
            statistics=version.statistics,
            content=version.content,
            sections=version.sections,
            snapshot_data=version.snapshot_data,
            file_paths=version.file_paths,
            changes=changes,
        ).model_dump()
    )


@router.post(
    "/{report_id}/versions/compare",
    response_model=APIResponse,
    summary="比较两个版本",
)
async def compare_versions(
    report_id: int,
    request: VersionCompareRequest,
    db: Session = Depends(get_db),
):
    """Compare two versions and return the differences."""
    service = ReportVersionService(db)
    
    try:
        result = service.compare_versions(
            report_id=report_id,
            version_a=request.version_a,
            version_b=request.version_b,
        )
        
        return APIResponse(
            success=True,
            code=200,
            message="版本比较成功",
            data=VersionCompareResponse(
                version_a=result["version_a"],
                version_b=result["version_b"],
                summary=result["summary"],
                changes=result["changes"],
            ).model_dump()
        )
    except NotFoundException as e:
        return APIResponse(
            success=False,
            code=404,
            message=str(e),
            data=None
        )


@router.post(
    "/{report_id}/versions/{version_number}/rollback",
    response_model=APIResponse,
    summary="回滚到指定版本",
)
async def rollback_to_version(
    report_id: int,
    version_number: str,
    request: RollbackRequest,
    db: Session = Depends(get_db),
):
    """Rollback to a specific version."""
    service = ReportVersionService(db)
    
    try:
        new_version = service.rollback_to_version(
            report_id=report_id,
            version_number=version_number,
            created_by=request.created_by,
            reason=request.reason,
        )
        
        return APIResponse(
            success=True,
            code=200,
            message=f"已回滚到版本 {version_number}，创建新版本 {new_version.version_number}",
            data=ReportVersionResponse(
                id=new_version.id,
                report_id=new_version.report_id,
                version_number=new_version.version_number,
                major_version=new_version.major_version,
                minor_version=new_version.minor_version,
                status=new_version.status,
                is_baseline=new_version.is_baseline,
                is_current=new_version.is_current,
                change_summary=new_version.change_summary,
                change_reason=new_version.change_reason,
                created_by=new_version.created_by,
                approved_by=new_version.approved_by,
                approved_at=new_version.approved_at,
                created_at=new_version.created_at,
                statistics=new_version.statistics,
            ).model_dump()
        )
    except NotFoundException as e:
        return APIResponse(
            success=False,
            code=404,
            message=str(e),
            data=None
        )


@router.post(
    "/{report_id}/versions/{version_number}/baseline",
    response_model=APIResponse,
    summary="设置为基线版本",
)
async def set_baseline(
    report_id: int,
    version_number: str,
    request: SetBaselineRequest,
    db: Session = Depends(get_db),
):
    """Set a version as the baseline."""
    service = ReportVersionService(db)
    
    try:
        version = service.set_baseline(report_id, version_number)
        
        return APIResponse(
            success=True,
            code=200,
            message=f"版本 {version_number} 已设置为基线版本",
            data=ReportVersionResponse(
                id=version.id,
                report_id=version.report_id,
                version_number=version.version_number,
                major_version=version.major_version,
                minor_version=version.minor_version,
                status=version.status,
                is_baseline=version.is_baseline,
                is_current=version.is_current,
                change_summary=version.change_summary,
                change_reason=version.change_reason,
                created_by=version.created_by,
                approved_by=version.approved_by,
                approved_at=version.approved_at,
                created_at=version.created_at,
                statistics=version.statistics,
            ).model_dump()
        )
    except NotFoundException as e:
        return APIResponse(
            success=False,
            code=404,
            message=str(e),
            data=None
        )


@router.post(
    "/{report_id}/versions/{version_number}/approve",
    response_model=APIResponse,
    summary="审批版本",
)
async def approve_version(
    report_id: int,
    version_number: str,
    request: ApproveVersionRequest,
    db: Session = Depends(get_db),
):
    """Approve a version."""
    service = ReportVersionService(db)
    
    try:
        version = service.approve_version(
            report_id=report_id,
            version_number=version_number,
            approved_by=request.approved_by,
        )
        
        return APIResponse(
            success=True,
            code=200,
            message=f"版本 {version_number} 已审批通过",
            data=ReportVersionResponse(
                id=version.id,
                report_id=version.report_id,
                version_number=version.version_number,
                major_version=version.major_version,
                minor_version=version.minor_version,
                status=version.status,
                is_baseline=version.is_baseline,
                is_current=version.is_current,
                change_summary=version.change_summary,
                change_reason=version.change_reason,
                created_by=version.created_by,
                approved_by=version.approved_by,
                approved_at=version.approved_at,
                created_at=version.created_at,
                statistics=version.statistics,
            ).model_dump()
        )
    except NotFoundException as e:
        return APIResponse(
            success=False,
            code=404,
            message=str(e),
            data=None
        )


@router.get(
    "/{report_id}/versions/current",
    response_model=APIResponse,
    summary="获取当前版本",
)
async def get_current_version(
    report_id: int,
    db: Session = Depends(get_db),
):
    """Get the current version of a report."""
    service = ReportVersionService(db)
    
    version = service.get_current_version(report_id)
    if not version:
        return APIResponse(
            success=False,
            code=404,
            message="暂无版本记录",
            data=None
        )
    
    return APIResponse(
        success=True,
        code=200,
        message="获取当前版本成功",
        data=ReportVersionResponse(
            id=version.id,
            report_id=version.report_id,
            version_number=version.version_number,
            major_version=version.major_version,
            minor_version=version.minor_version,
            status=version.status,
            is_baseline=version.is_baseline,
            is_current=version.is_current,
            change_summary=version.change_summary,
            change_reason=version.change_reason,
            created_by=version.created_by,
            approved_by=version.approved_by,
            approved_at=version.approved_at,
            created_at=version.created_at,
            statistics=version.statistics,
        ).model_dump()
    )
