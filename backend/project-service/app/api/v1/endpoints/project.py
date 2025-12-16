"""
Project Endpoints
=================

REST API endpoints for project management.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from tara_shared.database import get_db
from tara_shared.schemas import (ProjectCreate, ProjectListResponse,
                                 ProjectResponse, ProjectUpdate)
from tara_shared.schemas.project import ProjectCloneRequest, ProjectStats
from tara_shared.utils import paginated_response, success_response
from tara_shared.utils.exceptions import NotFoundException

from ....services.project_service import ProjectService

router = APIRouter()


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    """Dependency to get project service."""
    return ProjectService(db)


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="创建项目",
    description="创建一个新的TARA分析项目",
)
async def create_project(
    project_data: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
):
    """Create a new project."""
    project = service.create_project(project_data)
    return success_response(
        data=ProjectResponse.model_validate(project).model_dump(),
        message="项目创建成功",
    )


@router.get(
    "",
    response_model=dict,
    summary="获取项目列表",
    description="获取项目列表，支持分页和筛选，默认包含统计信息",
)
async def list_projects(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(default=None, description="搜索关键词"),
    status: Optional[int] = Query(default=None, ge=0, le=3, description="项目状态"),
    include_stats: bool = Query(default=True, description="是否包含统计信息"),
    service: ProjectService = Depends(get_project_service),
):
    """List all projects with pagination and optional statistics."""
    if include_stats:
        # Return projects with statistics included
        projects_with_stats, total = service.list_projects_with_stats(
            page=page,
            page_size=page_size,
            keyword=keyword,
            status=status,
        )
        return paginated_response(
            items=projects_with_stats,
            total=total,
            page=page,
            page_size=page_size,
        )
    else:
        # Return projects without statistics
        projects, total = service.list_projects(
            page=page,
            page_size=page_size,
            keyword=keyword,
            status=status,
        )
        items = [ProjectResponse.model_validate(p).model_dump() for p in projects]
        return paginated_response(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )


@router.get(
    "/{project_id}",
    response_model=dict,
    summary="获取项目详情",
    description="获取指定项目的详细信息",
)
async def get_project(
    project_id: int,
    include_stats: bool = Query(default=False, description="是否包含统计数据"),
    service: ProjectService = Depends(get_project_service),
):
    """Get project by ID."""
    project = service.get_project(project_id)
    if not project:
        raise NotFoundException("Project", project_id)

    response_data = ProjectResponse.model_validate(project).model_dump()

    if include_stats:
        stats = service.get_project_stats(project_id)
        response_data["stats"] = stats

    return success_response(data=response_data)


@router.put(
    "/{project_id}",
    response_model=dict,
    summary="更新项目",
    description="更新指定项目的信息",
)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
):
    """Update a project."""
    project = service.update_project(project_id, project_data)
    if not project:
        raise NotFoundException("Project", project_id)

    return success_response(
        data=ProjectResponse.model_validate(project).model_dump(),
        message="项目更新成功",
    )


@router.delete(
    "/{project_id}",
    response_model=dict,
    summary="删除项目",
    description="删除指定项目及其所有关联数据",
)
async def delete_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
):
    """Delete a project."""
    success = service.delete_project(project_id)
    if not success:
        raise NotFoundException("Project", project_id)

    return success_response(message="项目删除成功")


@router.post(
    "/{project_id}/clone",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="克隆项目",
    description="克隆一个现有项目",
)
async def clone_project(
    project_id: int,
    clone_request: ProjectCloneRequest,
    service: ProjectService = Depends(get_project_service),
):
    """Clone an existing project."""
    project = service.clone_project(
        project_id=project_id,
        new_name=clone_request.name,
        include_documents=clone_request.include_documents,
        include_assets=clone_request.include_assets,
        include_threats=clone_request.include_threats,
    )
    if not project:
        raise NotFoundException("Project", project_id)

    return success_response(
        data=ProjectResponse.model_validate(project).model_dump(),
        message="项目克隆成功",
    )


@router.get(
    "/{project_id}/stats",
    response_model=dict,
    summary="获取项目统计",
    description="获取项目的统计数据",
)
async def get_project_stats(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
):
    """Get project statistics."""
    project = service.get_project(project_id)
    if not project:
        raise NotFoundException("Project", project_id)

    stats = service.get_project_stats(project_id)
    return success_response(data=stats)


@router.patch(
    "/{project_id}/status",
    response_model=dict,
    summary="更新项目状态",
    description="更新项目状态",
)
async def update_project_status(
    project_id: int,
    status: int = Query(..., ge=0, le=3, description="项目状态"),
    service: ProjectService = Depends(get_project_service),
):
    """Update project status."""
    project = service.update_project_status(project_id, status)
    if not project:
        raise NotFoundException("Project", project_id)

    return success_response(
        data=ProjectResponse.model_validate(project).model_dump(),
        message="项目状态更新成功",
    )
