"""
Risk Endpoints
==============

REST API endpoints for risk assessment.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.common.database import get_db
from app.common.schemas.threat_risk import (RiskAssessmentRequest,
                                             RiskMatrixData)
from app.common.utils import success_response
from app.common.utils.exceptions import NotFoundException

from ....services.risk_service import RiskService

router = APIRouter()


def get_risk_service(db: Session = Depends(get_db)) -> RiskService:
    return RiskService(db)


@router.post("/assess", response_model=dict)
async def assess_risk(
    request: RiskAssessmentRequest,
    service: RiskService = Depends(get_risk_service),
):
    """Assess risk for a threat."""
    result = service.assess_risk(
        threat_risk_id=request.threat_risk_id,
        impact_level=request.impact_level,
        likelihood=request.likelihood,
        justification=request.justification,
    )

    if not result:
        raise NotFoundException("ThreatRisk", request.threat_risk_id)

    return success_response(data=result, message="风险评估完成")


@router.get("/matrix", response_model=dict)
async def get_risk_matrix(
    project_id: int = Query(..., description="项目ID"),
    service: RiskService = Depends(get_risk_service),
):
    """Get risk matrix data for a project."""
    matrix_data = service.get_risk_matrix(project_id)
    return success_response(data=matrix_data)


@router.get("/summary", response_model=dict)
async def get_risk_summary(
    project_id: int = Query(..., description="项目ID"),
    service: RiskService = Depends(get_risk_service),
):
    """Get risk summary for a project."""
    summary = service.get_risk_summary(project_id)
    return success_response(data=summary)


@router.post("/{threat_id}/treatment", response_model=dict)
async def set_risk_treatment(
    threat_id: int,
    treatment: str = Query(..., description="处置决策: avoid, reduce, share, retain"),
    treatment_desc: Optional[str] = Query(default=None, description="处置说明"),
    service: RiskService = Depends(get_risk_service),
):
    """Set risk treatment decision."""
    result = service.set_treatment(
        threat_risk_id=threat_id,
        treatment=treatment,
        treatment_desc=treatment_desc,
    )

    if not result:
        raise NotFoundException("ThreatRisk", threat_id)

    return success_response(data=result, message="风险处置决策已设置")


@router.post("/calculate-all", response_model=dict)
async def calculate_all_risks(
    project_id: int = Query(..., description="项目ID"),
    service: RiskService = Depends(get_risk_service),
):
    """Calculate risks for all threats in a project."""
    count = service.calculate_all_risks(project_id)
    return success_response(
        data={"calculated_count": count},
        message=f"已计算 {count} 个威胁的风险值",
    )
