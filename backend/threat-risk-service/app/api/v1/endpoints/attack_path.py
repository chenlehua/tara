"""
Attack Path Endpoints
=====================

REST API endpoints for attack path management.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.common.database import get_db
from app.common.schemas.threat_risk import (AttackPathCreate,
                                             AttackPathResponse,
                                             ControlMeasureCreate,
                                             ControlMeasureResponse)
from app.common.utils import success_response
from app.common.utils.exceptions import NotFoundException

from ....services.attack_path_service import AttackPathService

router = APIRouter()


def get_attack_path_service(db: Session = Depends(get_db)) -> AttackPathService:
    return AttackPathService(db)


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_attack_path(
    path_data: AttackPathCreate,
    service: AttackPathService = Depends(get_attack_path_service),
):
    """Create a new attack path."""
    path = service.create_attack_path(path_data)
    return success_response(
        data=AttackPathResponse.model_validate(path).model_dump(),
        message="攻击路径创建成功",
    )


@router.get("/{path_id}", response_model=dict)
async def get_attack_path(
    path_id: int,
    service: AttackPathService = Depends(get_attack_path_service),
):
    """Get attack path details."""
    path = service.get_attack_path(path_id)
    if not path:
        raise NotFoundException("AttackPath", path_id)

    return success_response(data=AttackPathResponse.model_validate(path).model_dump())


@router.delete("/{path_id}", response_model=dict)
async def delete_attack_path(
    path_id: int,
    service: AttackPathService = Depends(get_attack_path_service),
):
    """Delete an attack path."""
    success = service.delete_attack_path(path_id)
    if not success:
        raise NotFoundException("AttackPath", path_id)

    return success_response(message="攻击路径删除成功")


@router.post("/{path_id}/calculate-feasibility", response_model=dict)
async def calculate_feasibility(
    path_id: int,
    service: AttackPathService = Depends(get_attack_path_service),
):
    """Calculate attack feasibility for a path."""
    result = service.calculate_attack_feasibility(path_id)
    if not result:
        raise NotFoundException("AttackPath", path_id)

    return success_response(data=result, message="攻击可行性计算完成")


@router.post(
    "/{path_id}/controls", response_model=dict, status_code=status.HTTP_201_CREATED
)
async def add_control_measure(
    path_id: int,
    control_data: ControlMeasureCreate,
    service: AttackPathService = Depends(get_attack_path_service),
):
    """Add a control measure to an attack path."""
    control = service.add_control_measure(path_id, control_data)
    return success_response(
        data=ControlMeasureResponse.model_validate(control).model_dump(),
        message="控制措施添加成功",
    )


@router.get("/{path_id}/controls", response_model=dict)
async def list_control_measures(
    path_id: int,
    service: AttackPathService = Depends(get_attack_path_service),
):
    """List control measures for an attack path."""
    controls = service.list_control_measures(path_id)
    items = [ControlMeasureResponse.model_validate(c).model_dump() for c in controls]
    return success_response(data=items)
