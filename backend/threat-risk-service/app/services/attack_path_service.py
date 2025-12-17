"""
Attack Path Service
===================

Business logic for attack path management.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from app.common.constants.tara import ATTACK_POTENTIAL_TO_FEASIBILITY
from app.common.models import AttackPath, ControlMeasure
from app.common.schemas.threat_risk import (AttackPathCreate,
                                             ControlMeasureCreate)
from app.common.utils import get_logger

logger = get_logger(__name__)


class AttackPathService:
    """Service for attack path operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_attack_path(self, data: AttackPathCreate) -> AttackPath:
        """Create a new attack path."""
        path = AttackPath(
            threat_risk_id=data.threat_risk_id,
            name=data.name,
            description=data.description,
            steps=[s.model_dump() for s in data.steps],
            expertise=data.expertise,
            elapsed_time=data.elapsed_time,
            equipment=data.equipment,
            knowledge=data.knowledge,
            window_of_opportunity=data.window_of_opportunity,
            prerequisites=data.prerequisites,
            attack_techniques=data.attack_techniques,
        )

        # Calculate attack potential
        path.calculate_attack_potential()

        self.db.add(path)
        self.db.commit()
        self.db.refresh(path)

        return path

    def get_attack_path(self, path_id: int) -> Optional[AttackPath]:
        """Get attack path by ID."""
        return self.db.query(AttackPath).filter(AttackPath.id == path_id).first()

    def delete_attack_path(self, path_id: int) -> bool:
        """Delete an attack path."""
        path = self.get_attack_path(path_id)
        if not path:
            return False

        self.db.delete(path)
        self.db.commit()
        return True

    def calculate_attack_feasibility(self, path_id: int) -> Optional[Dict[str, Any]]:
        """Calculate attack feasibility for a path."""
        path = self.get_attack_path(path_id)
        if not path:
            return None

        # Calculate attack potential
        path.calculate_attack_potential()
        self.db.commit()

        return {
            "path_id": path_id,
            "attack_potential": path.attack_potential,
            "feasibility_rating": path.feasibility_rating,
            "breakdown": {
                "expertise": path.expertise,
                "elapsed_time": path.elapsed_time,
                "equipment": path.equipment,
                "knowledge": path.knowledge,
                "window_of_opportunity": path.window_of_opportunity,
            },
        }

    def add_control_measure(
        self,
        path_id: int,
        data: ControlMeasureCreate,
    ) -> ControlMeasure:
        """Add a control measure to an attack path."""
        control = ControlMeasure(
            attack_path_id=path_id,
            name=data.name,
            control_type=data.control_type,
            category=data.category,
            description=data.description,
            implementation=data.implementation,
            effectiveness=data.effectiveness,
            cost_estimate=data.cost_estimate,
            iso21434_ref=data.iso21434_ref,
        )

        self.db.add(control)
        self.db.commit()
        self.db.refresh(control)

        return control

    def list_control_measures(self, path_id: int) -> List[ControlMeasure]:
        """List control measures for an attack path."""
        return (
            self.db.query(ControlMeasure)
            .filter(ControlMeasure.attack_path_id == path_id)
            .all()
        )
