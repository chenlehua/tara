"""
Measure Endpoints
=================

REST API endpoints for control measure management.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.common.database import get_db
from app.common.models import ControlMeasure
from app.common.schemas.threat_risk import ControlMeasureResponse
from app.common.utils import paginated_response, success_response
from app.common.utils.exceptions import NotFoundException

router = APIRouter()


@router.get("", response_model=dict)
async def list_measures(
    project_id: Optional[int] = Query(default=None, description="项目ID，为空则返回所有项目的措施"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List control measures for a project or all projects if project_id is not provided."""
    query = db.query(ControlMeasure)
    
    if project_id is not None:
        # Join through attack_path to filter by project
        from app.common.models import AttackPath, ThreatRisk
        query = query.join(AttackPath, ControlMeasure.attack_path_id == AttackPath.id)
        query = query.join(ThreatRisk, AttackPath.threat_risk_id == ThreatRisk.id)
        query = query.filter(ThreatRisk.project_id == project_id)
    
    total = query.count()
    offset = (page - 1) * page_size
    measures = (
        query.order_by(ControlMeasure.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    
    items = [ControlMeasureResponse.model_validate(m).model_dump() for m in measures]
    return paginated_response(items=items, total=total, page=page, page_size=page_size)


@router.get("/{measure_id}", response_model=dict)
async def get_measure(
    measure_id: int,
    db: Session = Depends(get_db),
):
    """Get control measure details."""
    measure = db.query(ControlMeasure).filter(ControlMeasure.id == measure_id).first()
    if not measure:
        raise NotFoundException("ControlMeasure", measure_id)
    
    return success_response(data=ControlMeasureResponse.model_validate(measure).model_dump())


@router.delete("/{measure_id}", response_model=dict)
async def delete_measure(
    measure_id: int,
    db: Session = Depends(get_db),
):
    """Delete a control measure."""
    measure = db.query(ControlMeasure).filter(ControlMeasure.id == measure_id).first()
    if not measure:
        raise NotFoundException("ControlMeasure", measure_id)
    
    db.delete(measure)
    db.commit()
    
    return success_response(message="控制措施删除成功")
