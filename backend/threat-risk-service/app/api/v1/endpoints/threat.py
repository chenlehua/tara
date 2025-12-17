"""
Threat Endpoints
================

REST API endpoints for threat management and STRIDE analysis.
"""

from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from sqlalchemy.orm import Session
from tara_shared.database import get_db
from tara_shared.schemas.threat_risk import (STRIDEAnalysisRequest,
                                             ThreatRiskCreate,
                                             ThreatRiskDetailResponse,
                                             ThreatRiskResponse,
                                             ThreatRiskUpdate)
from tara_shared.utils import paginated_response, success_response
from tara_shared.utils.exceptions import NotFoundException

from ....services.threat_service import ThreatService

router = APIRouter()


def get_threat_service(db: Session = Depends(get_db)) -> ThreatService:
    return ThreatService(db)


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_threat(
    threat_data: ThreatRiskCreate,
    service: ThreatService = Depends(get_threat_service),
):
    """Create a new threat."""
    threat = service.create_threat(threat_data)
    return success_response(
        data=ThreatRiskResponse.model_validate(threat).model_dump(),
        message="威胁创建成功",
    )


@router.get("", response_model=dict)
async def list_threats(
    project_id: Optional[int] = Query(default=None, description="项目ID，为空则返回所有项目的威胁"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    asset_id: Optional[int] = Query(default=None, description="资产ID"),
    threat_type: Optional[str] = Query(default=None, description="威胁类型(STRIDE)"),
    risk_level: Optional[str] = Query(default=None, description="风险等级"),
    service: ThreatService = Depends(get_threat_service),
):
    """List threats for a project or all projects if project_id is not provided."""
    threats, total = service.list_threats(
        project_id=project_id,
        page=page,
        page_size=page_size,
        asset_id=asset_id,
        threat_type=threat_type,
        risk_level=risk_level,
    )

    items = [ThreatRiskResponse.model_validate(t).model_dump() for t in threats]
    return paginated_response(items=items, total=total, page=page, page_size=page_size)


@router.get("/{threat_id}", response_model=dict)
async def get_threat(
    threat_id: int,
    include_attack_paths: bool = Query(default=False),
    service: ThreatService = Depends(get_threat_service),
):
    """Get threat details."""
    threat = service.get_threat(threat_id)
    if not threat:
        raise NotFoundException("ThreatRisk", threat_id)

    if include_attack_paths:
        response = ThreatRiskDetailResponse.model_validate(threat)
    else:
        response = ThreatRiskResponse.model_validate(threat)

    return success_response(data=response.model_dump())


@router.put("/{threat_id}", response_model=dict)
async def update_threat(
    threat_id: int,
    threat_data: ThreatRiskUpdate,
    service: ThreatService = Depends(get_threat_service),
):
    """Update a threat."""
    threat = service.update_threat(threat_id, threat_data)
    if not threat:
        raise NotFoundException("ThreatRisk", threat_id)

    return success_response(
        data=ThreatRiskResponse.model_validate(threat).model_dump(),
        message="威胁更新成功",
    )


@router.delete("/{threat_id}", response_model=dict)
async def delete_threat(
    threat_id: int,
    service: ThreatService = Depends(get_threat_service),
):
    """Delete a threat."""
    success = service.delete_threat(threat_id)
    if not success:
        raise NotFoundException("ThreatRisk", threat_id)

    return success_response(message="威胁删除成功")


@router.post("/analyze", response_model=dict)
async def analyze_threats(
    request: STRIDEAnalysisRequest,
    background_tasks: BackgroundTasks,
    service: ThreatService = Depends(get_threat_service),
):
    """Run STRIDE threat analysis on assets."""
    task_id = service.start_stride_analysis(
        asset_ids=request.asset_ids,
        include_attack_paths=request.include_attack_paths,
    )

    background_tasks.add_task(
        service.run_stride_analysis,
        task_id=task_id,
        asset_ids=request.asset_ids,
        include_attack_paths=request.include_attack_paths,
    )

    return success_response(
        data={"task_id": task_id, "status": "processing"},
        message="STRIDE分析任务已启动",
    )


@router.get("/{threat_id}/attack-tree", response_model=dict)
async def get_attack_tree(
    threat_id: int,
    service: ThreatService = Depends(get_threat_service),
):
    """Get attack tree for a threat."""
    threat = service.get_threat(threat_id)
    if not threat:
        raise NotFoundException("ThreatRisk", threat_id)

    attack_tree = service.generate_attack_tree(threat_id)
    return success_response(data=attack_tree)


@router.post("/analyze-project", response_model=dict)
async def analyze_threats_for_project(
    project_id: int = Query(..., description="项目ID"),
    asset_ids: Optional[List[int]] = Query(default=None, description="资产ID列表"),
    service: ThreatService = Depends(get_threat_service),
):
    """
    Perform complete threat analysis for a project.
    
    This endpoint is called by report service during one-click generation.
    It fetches assets from asset service and performs STRIDE analysis.
    """
    result = await service.analyze_threats_for_project(
        project_id=project_id,
        asset_ids=asset_ids,
    )

    return success_response(
        data=result,
        message=f"威胁分析完成，共创建 {result['created_threats']} 个威胁",
    )


@router.post("/assess-risks", response_model=dict)
async def assess_risks_for_project(
    project_id: int = Query(..., description="项目ID"),
    service: ThreatService = Depends(get_threat_service),
):
    """
    Perform risk assessment for all threats in a project.
    
    Updates risk levels based on impact and likelihood analysis.
    """
    result = await service.assess_risks_for_project(project_id=project_id)

    return success_response(
        data=result,
        message=f"风险评估完成，共分析 {result['total_threats']} 个威胁",
    )


@router.get("/project/{project_id}/all", response_model=dict)
async def get_project_threats(
    project_id: int,
    service: ThreatService = Depends(get_threat_service),
):
    """
    Get all threats for a project in API-friendly format.
    
    Used by report service to get complete threat data for report generation.
    """
    threats = service.get_threats_for_project(project_id)
    return success_response(
        data={"project_id": project_id, "threats": threats, "total": len(threats)}
    )


@router.get("/project/{project_id}/measures", response_model=dict)
async def get_project_measures(
    project_id: int,
    service: ThreatService = Depends(get_threat_service),
):
    """
    Get all control measures for a project.
    
    Used by report service to get complete measures data for report generation.
    """
    measures = service.get_control_measures_for_project(project_id)
    return success_response(
        data={"project_id": project_id, "measures": measures, "total": len(measures)}
    )
