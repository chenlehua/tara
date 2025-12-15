"""
Asset Endpoints
===============

REST API endpoints for asset management.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, BackgroundTasks, status
from sqlalchemy.orm import Session

from tara_shared.database import get_db
from tara_shared.schemas.asset import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    AssetDetailResponse,
    AssetDiscoveryRequest,
    AssetGraph,
)
from tara_shared.utils import success_response, paginated_response
from tara_shared.utils.exceptions import NotFoundException

from ....services.asset_service import AssetService

router = APIRouter()


def get_asset_service(db: Session = Depends(get_db)) -> AssetService:
    return AssetService(db)


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_data: AssetCreate,
    service: AssetService = Depends(get_asset_service),
):
    """Create a new asset."""
    asset = service.create_asset(asset_data)
    return success_response(
        data=AssetResponse.model_validate(asset).model_dump(),
        message="资产创建成功",
    )


@router.get("", response_model=dict)
async def list_assets(
    project_id: int = Query(..., description="项目ID"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    asset_type: Optional[str] = Query(default=None, description="资产类型"),
    category: Optional[str] = Query(default=None, description="资产分类"),
    keyword: Optional[str] = Query(default=None, description="搜索关键词"),
    service: AssetService = Depends(get_asset_service),
):
    """List assets for a project."""
    assets, total = service.list_assets(
        project_id=project_id,
        page=page,
        page_size=page_size,
        asset_type=asset_type,
        category=category,
        keyword=keyword,
    )
    
    items = [AssetResponse.model_validate(a).model_dump() for a in assets]
    return paginated_response(items=items, total=total, page=page, page_size=page_size)


@router.get("/graph", response_model=dict)
async def get_asset_graph(
    project_id: int = Query(..., description="项目ID"),
    service: AssetService = Depends(get_asset_service),
):
    """Get asset relationship graph for a project."""
    graph = service.get_asset_graph(project_id)
    return success_response(data=graph)


@router.get("/{asset_id}", response_model=dict)
async def get_asset(
    asset_id: int,
    include_children: bool = Query(default=False),
    include_scenarios: bool = Query(default=False),
    service: AssetService = Depends(get_asset_service),
):
    """Get asset details."""
    asset = service.get_asset(asset_id)
    if not asset:
        raise NotFoundException("Asset", asset_id)
    
    response = AssetDetailResponse.model_validate(asset)
    
    if include_children:
        response.children = [AssetResponse.model_validate(c) for c in asset.children]
    
    if include_scenarios:
        from tara_shared.schemas.asset import DamageScenarioResponse
        response.damage_scenarios = [
            DamageScenarioResponse.model_validate(s) for s in asset.damage_scenarios
        ]
    
    return success_response(data=response.model_dump())


@router.put("/{asset_id}", response_model=dict)
async def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    service: AssetService = Depends(get_asset_service),
):
    """Update an asset."""
    asset = service.update_asset(asset_id, asset_data)
    if not asset:
        raise NotFoundException("Asset", asset_id)
    
    return success_response(
        data=AssetResponse.model_validate(asset).model_dump(),
        message="资产更新成功",
    )


@router.delete("/{asset_id}", response_model=dict)
async def delete_asset(
    asset_id: int,
    service: AssetService = Depends(get_asset_service),
):
    """Delete an asset."""
    success = service.delete_asset(asset_id)
    if not success:
        raise NotFoundException("Asset", asset_id)
    
    return success_response(message="资产删除成功")


@router.post("/discover", response_model=dict)
async def discover_assets(
    request: AssetDiscoveryRequest,
    background_tasks: BackgroundTasks,
    service: AssetService = Depends(get_asset_service),
):
    """AI-powered asset discovery from documents."""
    task_id = service.start_asset_discovery(
        document_ids=request.document_ids,
        include_relations=request.include_relations,
    )
    
    background_tasks.add_task(
        service.run_asset_discovery,
        task_id=task_id,
        document_ids=request.document_ids,
        include_relations=request.include_relations,
    )
    
    return success_response(
        data={"task_id": task_id, "status": "processing"},
        message="资产识别任务已启动",
    )


@router.post("/{asset_id}/relations", response_model=dict)
async def add_asset_relation(
    asset_id: int,
    target_asset_id: int = Query(..., description="目标资产ID"),
    relation_type: str = Query(..., description="关系类型"),
    service: AssetService = Depends(get_asset_service),
):
    """Add a relationship between assets."""
    success = service.add_asset_relation(
        source_id=asset_id,
        target_id=target_asset_id,
        relation_type=relation_type,
    )
    
    if not success:
        raise NotFoundException("Asset", asset_id)
    
    return success_response(message="资产关系添加成功")
