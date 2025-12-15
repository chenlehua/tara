"""
Damage Scenario Service
=======================

Business logic for damage scenario management.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from tara_shared.models import DamageScenario
from tara_shared.schemas.asset import DamageScenarioCreate
from tara_shared.utils import get_logger

logger = get_logger(__name__)


class DamageScenarioService:
    """Service for damage scenario operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_scenario(self, data: DamageScenarioCreate) -> DamageScenario:
        """Create a new damage scenario."""
        scenario = DamageScenario(
            asset_id=data.asset_id,
            name=data.name,
            description=data.description,
            safety_impact=data.safety_impact,
            financial_impact=data.financial_impact,
            operational_impact=data.operational_impact,
            privacy_impact=data.privacy_impact,
            impact_justification=data.impact_justification,
            stakeholders=data.stakeholders,
        )
        
        # Calculate max impact
        scenario.impact_level = max(
            scenario.safety_impact,
            scenario.financial_impact,
            scenario.operational_impact,
            scenario.privacy_impact,
        )
        
        self.db.add(scenario)
        self.db.commit()
        self.db.refresh(scenario)
        
        return scenario

    def get_scenario(self, scenario_id: int) -> Optional[DamageScenario]:
        """Get damage scenario by ID."""
        return self.db.query(DamageScenario).filter(
            DamageScenario.id == scenario_id
        ).first()

    def list_scenarios(self, asset_id: int) -> List[DamageScenario]:
        """List all damage scenarios for an asset."""
        return self.db.query(DamageScenario).filter(
            DamageScenario.asset_id == asset_id
        ).all()

    def delete_scenario(self, scenario_id: int) -> bool:
        """Delete a damage scenario."""
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return False
        
        self.db.delete(scenario)
        self.db.commit()
        return True
