"""
Risk Service
============

Business logic for risk assessment.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from tara_shared.models import ThreatRisk
from tara_shared.constants.tara import RISK_MATRIX, RISK_LEVEL_TO_CAL
from tara_shared.utils import get_logger

logger = get_logger(__name__)


class RiskService:
    """Service for risk assessment operations."""

    def __init__(self, db: Session):
        self.db = db

    def assess_risk(
        self,
        threat_risk_id: int,
        impact_level: int,
        likelihood: int,
        justification: str = None,
    ) -> Optional[Dict[str, Any]]:
        """Assess risk for a threat."""
        threat = self.db.query(ThreatRisk).filter(
            ThreatRisk.id == threat_risk_id
        ).first()
        
        if not threat:
            return None
        
        # Set impact and likelihood
        threat.impact_level = impact_level
        threat.likelihood = likelihood
        
        # Calculate risk using matrix
        threat.risk_value = impact_level * likelihood
        
        # Determine risk level from matrix
        if impact_level >= 0 and impact_level <= 4 and likelihood >= 0 and likelihood <= 4:
            threat.risk_level = RISK_MATRIX[impact_level][likelihood]
        
        # Determine CAL
        if threat.risk_level:
            threat.cal = RISK_LEVEL_TO_CAL.get(threat.risk_level, 1)
        
        self.db.commit()
        
        return {
            "threat_risk_id": threat_risk_id,
            "impact_level": threat.impact_level,
            "likelihood": threat.likelihood,
            "risk_value": threat.risk_value,
            "risk_level": threat.risk_level,
            "cal": threat.cal,
        }

    def get_risk_matrix(self, project_id: int) -> Dict[str, Any]:
        """Get risk matrix data for a project."""
        # Initialize 5x5 matrix
        matrix = [[0 for _ in range(5)] for _ in range(5)]
        
        # Query threats and count by impact/likelihood
        threats = self.db.query(ThreatRisk).filter(
            ThreatRisk.project_id == project_id,
            ThreatRisk.impact_level.isnot(None),
            ThreatRisk.likelihood.isnot(None),
        ).all()
        
        for threat in threats:
            impact = threat.impact_level or 0
            likelihood = threat.likelihood or 0
            if 0 <= impact <= 4 and 0 <= likelihood <= 4:
                matrix[impact][likelihood] += 1
        
        # Count by risk level
        level_counts = (
            self.db.query(ThreatRisk.risk_level, func.count(ThreatRisk.id))
            .filter(ThreatRisk.project_id == project_id)
            .group_by(ThreatRisk.risk_level)
            .all()
        )
        
        threats_by_level = {level: count for level, count in level_counts if level}
        
        return {
            "matrix": matrix,
            "threats_by_level": threats_by_level,
        }

    def get_risk_summary(self, project_id: int) -> Dict[str, Any]:
        """Get risk summary for a project."""
        total = self.db.query(func.count(ThreatRisk.id)).filter(
            ThreatRisk.project_id == project_id
        ).scalar()
        
        assessed = self.db.query(func.count(ThreatRisk.id)).filter(
            ThreatRisk.project_id == project_id,
            ThreatRisk.risk_level.isnot(None),
        ).scalar()
        
        treated = self.db.query(func.count(ThreatRisk.id)).filter(
            ThreatRisk.project_id == project_id,
            ThreatRisk.treatment.isnot(None),
        ).scalar()
        
        level_counts = (
            self.db.query(ThreatRisk.risk_level, func.count(ThreatRisk.id))
            .filter(ThreatRisk.project_id == project_id)
            .group_by(ThreatRisk.risk_level)
            .all()
        )
        
        by_level = {level: count for level, count in level_counts if level}
        
        return {
            "total_threats": total or 0,
            "assessed_threats": assessed or 0,
            "treated_threats": treated or 0,
            "by_level": by_level,
            "critical_count": by_level.get("critical", 0),
            "high_count": by_level.get("high", 0),
            "medium_count": by_level.get("medium", 0),
            "low_count": by_level.get("low", 0),
            "negligible_count": by_level.get("negligible", 0),
        }

    def set_treatment(
        self,
        threat_risk_id: int,
        treatment: str,
        treatment_desc: str = None,
    ) -> Optional[Dict[str, Any]]:
        """Set risk treatment decision."""
        threat = self.db.query(ThreatRisk).filter(
            ThreatRisk.id == threat_risk_id
        ).first()
        
        if not threat:
            return None
        
        threat.treatment = treatment
        threat.treatment_desc = treatment_desc
        self.db.commit()
        
        return {
            "threat_risk_id": threat_risk_id,
            "treatment": threat.treatment,
            "treatment_desc": threat.treatment_desc,
        }

    def calculate_all_risks(self, project_id: int) -> int:
        """Calculate risks for all threats in a project."""
        threats = self.db.query(ThreatRisk).filter(
            ThreatRisk.project_id == project_id,
            ThreatRisk.impact_level.isnot(None),
            ThreatRisk.likelihood.isnot(None),
        ).all()
        
        count = 0
        for threat in threats:
            threat.calculate_risk()
            if threat.risk_level:
                threat.cal = RISK_LEVEL_TO_CAL.get(threat.risk_level, 1)
            count += 1
        
        self.db.commit()
        return count
