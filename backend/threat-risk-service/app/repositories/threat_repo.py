"""
Threat Repository
=================

Data access layer for ThreatRisk entity.
"""

from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from tara_shared.models import ThreatRisk


class ThreatRepository:
    """Repository for ThreatRisk data access."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, threat: ThreatRisk) -> ThreatRisk:
        self.db.add(threat)
        self.db.commit()
        self.db.refresh(threat)
        return threat

    def get_by_id(self, threat_id: int) -> Optional[ThreatRisk]:
        return self.db.query(ThreatRisk).filter(ThreatRisk.id == threat_id).first()

    def list_threats(
        self,
        project_id: int,
        page: int = 1,
        page_size: int = 20,
        asset_id: int = None,
        threat_type: str = None,
        risk_level: str = None,
    ) -> Tuple[List[ThreatRisk], int]:
        query = self.db.query(ThreatRisk).filter(ThreatRisk.project_id == project_id)
        
        if asset_id:
            query = query.filter(ThreatRisk.asset_id == asset_id)
        
        if threat_type:
            query = query.filter(ThreatRisk.threat_type == threat_type)
        
        if risk_level:
            query = query.filter(ThreatRisk.risk_level == risk_level)
        
        total = query.count()
        offset = (page - 1) * page_size
        threats = query.order_by(ThreatRisk.created_at.desc()).offset(offset).limit(page_size).all()
        
        return threats, total

    def update(self, threat: ThreatRisk) -> ThreatRisk:
        self.db.commit()
        self.db.refresh(threat)
        return threat

    def delete(self, threat: ThreatRisk) -> None:
        self.db.delete(threat)
        self.db.commit()
