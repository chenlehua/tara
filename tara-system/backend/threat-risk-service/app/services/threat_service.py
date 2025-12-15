"""
Threat Service
==============

Business logic for threat management and STRIDE analysis.
"""

from typing import Any, Dict, List, Optional, Tuple
import uuid

from sqlalchemy.orm import Session

from tara_shared.models import ThreatRisk, Asset
from tara_shared.schemas.threat_risk import ThreatRiskCreate, ThreatRiskUpdate
from tara_shared.constants import STRIDE_TYPES
from tara_shared.utils import get_logger

from ..repositories.threat_repo import ThreatRepository

logger = get_logger(__name__)


class ThreatService:
    """Service for threat operations."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = ThreatRepository(db)

    def create_threat(self, data: ThreatRiskCreate) -> ThreatRisk:
        """Create a new threat."""
        threat = ThreatRisk(
            project_id=data.project_id,
            asset_id=data.asset_id,
            damage_scenario_id=data.damage_scenario_id,
            threat_name=data.threat_name,
            threat_type=data.threat_type,
            threat_desc=data.threat_desc,
            attack_vector=data.attack_vector,
            attack_surface=data.attack_surface,
            threat_source=data.threat_source,
            threat_agent=data.threat_agent,
            safety_impact=data.safety_impact,
            financial_impact=data.financial_impact,
            operational_impact=data.operational_impact,
            privacy_impact=data.privacy_impact,
            cwe_ids=data.cwe_ids,
            capec_ids=data.capec_ids,
            source="manual",
        )
        
        # Calculate impact level
        threat.impact_level = max(
            threat.safety_impact,
            threat.financial_impact,
            threat.operational_impact,
            threat.privacy_impact,
        )
        
        return self.repo.create(threat)

    def get_threat(self, threat_id: int) -> Optional[ThreatRisk]:
        """Get threat by ID."""
        return self.repo.get_by_id(threat_id)

    def list_threats(
        self,
        project_id: int,
        page: int = 1,
        page_size: int = 20,
        asset_id: int = None,
        threat_type: str = None,
        risk_level: str = None,
    ) -> Tuple[List[ThreatRisk], int]:
        """List threats with filtering."""
        return self.repo.list_threats(
            project_id=project_id,
            page=page,
            page_size=page_size,
            asset_id=asset_id,
            threat_type=threat_type,
            risk_level=risk_level,
        )

    def update_threat(
        self,
        threat_id: int,
        data: ThreatRiskUpdate,
    ) -> Optional[ThreatRisk]:
        """Update a threat."""
        threat = self.repo.get_by_id(threat_id)
        if not threat:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(threat, key, value)
        
        # Recalculate impact if any impact changed
        if any(k in update_data for k in ['safety_impact', 'financial_impact', 'operational_impact', 'privacy_impact']):
            threat.impact_level = max(
                threat.safety_impact or 0,
                threat.financial_impact or 0,
                threat.operational_impact or 0,
                threat.privacy_impact or 0,
            )
        
        # Recalculate risk if impact or likelihood changed
        if 'likelihood' in update_data or 'impact_level' in update_data:
            threat.calculate_risk()
        
        return self.repo.update(threat)

    def delete_threat(self, threat_id: int) -> bool:
        """Delete a threat."""
        threat = self.repo.get_by_id(threat_id)
        if not threat:
            return False
        
        self.repo.delete(threat)
        return True

    def start_stride_analysis(
        self,
        asset_ids: List[int],
        include_attack_paths: bool = True,
    ) -> str:
        """Start STRIDE analysis task."""
        return str(uuid.uuid4())

    async def run_stride_analysis(
        self,
        task_id: str,
        asset_ids: List[int],
        include_attack_paths: bool = True,
    ) -> None:
        """Run STRIDE analysis on assets."""
        logger.info(f"Running STRIDE analysis task {task_id}")
        
        for asset_id in asset_ids:
            asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
            if not asset:
                continue
            
            # Analyze each STRIDE category
            for stride_type, stride_info in STRIDE_TYPES.items():
                # This would call AI service in production
                # For now, create placeholder threats
                threat = ThreatRisk(
                    project_id=asset.project_id,
                    asset_id=asset_id,
                    threat_name=f"{stride_info['name_zh']}威胁 - {asset.name}",
                    threat_type=stride_type,
                    threat_desc=f"针对{asset.name}的{stride_info['description']}",
                    source="ai_analyzed",
                )
                self.db.add(threat)
        
        self.db.commit()
        logger.info(f"STRIDE analysis completed for task {task_id}")

    def generate_attack_tree(self, threat_id: int) -> Dict[str, Any]:
        """Generate attack tree for a threat."""
        threat = self.repo.get_by_id(threat_id)
        if not threat:
            return {}
        
        # Build attack tree structure
        root = {
            "id": "root",
            "label": threat.threat_name,
            "node_type": "goal",
            "children": [],
        }
        
        # Add attack paths as branches
        for path in threat.attack_paths:
            path_node = {
                "id": f"path_{path.id}",
                "label": path.name,
                "node_type": "or",
                "attack_potential": path.attack_potential,
                "children": [],
            }
            
            # Add steps as leaves
            for step in (path.steps or []):
                step_node = {
                    "id": f"step_{path.id}_{step.get('order', 0)}",
                    "label": step.get("action", "Unknown"),
                    "node_type": "leaf",
                    "children": [],
                }
                path_node["children"].append(step_node)
            
            root["children"].append(path_node)
        
        return {
            "threat_id": threat_id,
            "threat_name": threat.threat_name,
            "root": root,
        }
