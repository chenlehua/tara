"""
Threat Service
==============

Business logic for threat management and STRIDE analysis.
"""

import uuid
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session
from tara_shared.constants import STRIDE_TYPES
from tara_shared.models import Asset, ThreatRisk
from tara_shared.schemas.threat_risk import ThreatRiskCreate, ThreatRiskUpdate
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
        if any(
            k in update_data
            for k in [
                "safety_impact",
                "financial_impact",
                "operational_impact",
                "privacy_impact",
            ]
        ):
            threat.impact_level = max(
                threat.safety_impact or 0,
                threat.financial_impact or 0,
                threat.operational_impact or 0,
                threat.privacy_impact or 0,
            )

        # Recalculate risk if impact or likelihood changed
        if "likelihood" in update_data or "impact_level" in update_data:
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

            # Try to use AI service for enhanced threat analysis
            ai_threats = None
            try:
                import httpx
                from tara_shared.config import settings

                async with httpx.AsyncClient() as client:
                    # Get asset context
                    asset_context = f"""
资产名称: {asset.name}
资产类型: {asset.asset_type}
资产类别: {asset.category or 'Unknown'}
接口: {asset.interfaces or []}
安全属性: {asset.security_attrs or {}}
"""
                    response = await client.post(
                        f"{settings.qwen3_url}/chat/completions",
                        json={
                            "model": "qwen3",
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "你是汽车网络安全专家，请对以下资产进行STRIDE威胁分析。对每种适用的威胁类型(S欺骗/T篡改/R否认/I信息泄露/D拒绝服务/E权限提升)，给出威胁名称、描述、攻击向量和建议影响等级(1-4)。返回JSON数组格式。",
                                },
                                {"role": "user", "content": asset_context},
                            ],
                            "temperature": 0.3,
                            "max_tokens": 2000,
                        },
                        timeout=60.0,
                    )
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result["choices"][0]["message"]["content"]
                        ai_threats = self._parse_ai_threats(ai_response)
            except Exception as e:
                logger.warning(f"AI service unavailable for STRIDE analysis: {e}")

            if ai_threats:
                # Create threats from AI analysis
                for threat_data in ai_threats:
                    threat = ThreatRisk(
                        project_id=asset.project_id,
                        asset_id=asset_id,
                        threat_name=threat_data.get("name", "Unknown Threat"),
                        threat_type=threat_data.get("type", "T"),
                        threat_desc=threat_data.get("description", ""),
                        attack_vector=threat_data.get("attack_vector", ""),
                        impact_level=threat_data.get("impact_level", 2),
                        source="ai_analyzed",
                    )
                    self.db.add(threat)
            else:
                # Fallback: Create basic STRIDE threats
                for stride_type, stride_info in STRIDE_TYPES.items():
                    # Calculate relevance based on asset type
                    if not self._is_threat_relevant(asset, stride_type):
                        continue

                    threat = ThreatRisk(
                        project_id=asset.project_id,
                        asset_id=asset_id,
                        threat_name=f"{stride_info['name_zh']}威胁 - {asset.name}",
                        threat_type=stride_type,
                        threat_desc=f"针对{asset.name}的{stride_info['description']}",
                        attack_vector=self._get_default_attack_vector(asset, stride_type),
                        impact_level=self._estimate_impact_level(asset, stride_type),
                        source="auto_generated",
                    )
                    self.db.add(threat)

        self.db.commit()
        logger.info(f"STRIDE analysis completed for task {task_id}")

    def _parse_ai_threats(self, ai_response: str) -> List[Dict[str, Any]]:
        """Parse AI response for threat analysis."""
        import json
        import re

        try:
            json_match = re.search(r"\[.*\]", ai_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        return []

    def _is_threat_relevant(self, asset: Asset, stride_type: str) -> bool:
        """Check if a STRIDE threat type is relevant for the asset."""
        asset_type = (asset.asset_type or "").lower()
        interfaces = asset.interfaces or []

        # External interfaces make most threats relevant
        external_interfaces = ["wifi", "bluetooth", "4g", "5g", "cellular"]
        has_external = any(
            any(ext in str(iface).lower() for ext in external_interfaces)
            for iface in interfaces
        )

        if has_external:
            return True

        # Gateway assets are vulnerable to all threats
        if "gateway" in asset_type:
            return True

        # Basic threats for all assets
        if stride_type in ["T", "D"]:  # Tampering, DoS
            return True

        return stride_type in ["S", "I"]  # Spoofing, Info Disclosure for most

    def _get_default_attack_vector(self, asset: Asset, stride_type: str) -> str:
        """Get default attack vector description."""
        interfaces = asset.interfaces or []
        iface_str = ", ".join(str(i.get("type", i) if isinstance(i, dict) else i) for i in interfaces[:2]) or "通信接口"

        vectors = {
            "S": f"通过{iface_str}伪造身份或消息来源",
            "T": f"利用{iface_str}注入恶意数据或修改传输内容",
            "R": "缺少充分的日志和审计机制，无法追溯操作",
            "I": f"窃听{iface_str}通信或访问未加密的数据存储",
            "D": f"向{iface_str}发送大量请求或恶意数据导致服务中断",
            "E": "利用软件漏洞或配置缺陷获取更高权限",
        }
        return vectors.get(stride_type, "未知攻击向量")

    def _estimate_impact_level(self, asset: Asset, stride_type: str) -> int:
        """Estimate impact level based on asset properties."""
        security_attrs = asset.security_attrs or {}
        criticality = asset.criticality or "medium"

        # Base impact from criticality
        base_impact = {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(
            criticality.lower(), 2
        )

        # Adjust based on STRIDE type and security attributes
        if stride_type in ["T", "D"]:  # Tampering, DoS affect integrity/availability
            integrity = security_attrs.get("integrity", "medium")
            if integrity in ["critical", "high"]:
                base_impact = max(base_impact, 3)

        if stride_type in ["S", "I"]:  # Spoofing, Info Disclosure affect confidentiality
            confidentiality = security_attrs.get("confidentiality", "medium")
            if confidentiality in ["critical", "high"]:
                base_impact = max(base_impact, 3)

        return min(base_impact, 4)

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
            for step in path.steps or []:
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
