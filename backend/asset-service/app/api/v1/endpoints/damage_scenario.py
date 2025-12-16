"""
Damage Scenario Endpoints
=========================

REST API endpoints for damage scenario management.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from tara_shared.database import get_db
from tara_shared.schemas.asset import DamageScenarioCreate, DamageScenarioResponse
from tara_shared.utils import success_response
from tara_shared.utils.exceptions import NotFoundException

from ....services.damage_service import DamageScenarioService

router = APIRouter()


def get_damage_service(db: Session = Depends(get_db)) -> DamageScenarioService:
    return DamageScenarioService(db)


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_damage_scenario(
    scenario_data: DamageScenarioCreate,
    service: DamageScenarioService = Depends(get_damage_service),
):
    """Create a new damage scenario."""
    scenario = service.create_scenario(scenario_data)
    return success_response(
        data=DamageScenarioResponse.model_validate(scenario).model_dump(),
        message="损害场景创建成功",
    )


@router.get("", response_model=dict)
async def list_damage_scenarios(
    asset_id: int = Query(..., description="资产ID"),
    service: DamageScenarioService = Depends(get_damage_service),
):
    """List damage scenarios for an asset."""
    scenarios = service.list_scenarios(asset_id)
    items = [DamageScenarioResponse.model_validate(s).model_dump() for s in scenarios]
    return success_response(data=items)


@router.get("/{scenario_id}", response_model=dict)
async def get_damage_scenario(
    scenario_id: int,
    service: DamageScenarioService = Depends(get_damage_service),
):
    """Get damage scenario details."""
    scenario = service.get_scenario(scenario_id)
    if not scenario:
        raise NotFoundException("DamageScenario", scenario_id)
    
    return success_response(data=DamageScenarioResponse.model_validate(scenario).model_dump())


@router.delete("/{scenario_id}", response_model=dict)
async def delete_damage_scenario(
    scenario_id: int,
    service: DamageScenarioService = Depends(get_damage_service),
):
    """Delete a damage scenario."""
    success = service.delete_scenario(scenario_id)
    if not success:
        raise NotFoundException("DamageScenario", scenario_id)
    
    return success_response(message="损害场景删除成功")
