"""
STRIDE Analysis Engine
======================

Engine for STRIDE threat identification.
"""

from typing import Any, Dict, List

from app.common.constants import STRIDE_TYPES
from app.common.utils import get_logger

logger = get_logger(__name__)


class STRIDEEngine:
    """Engine for STRIDE threat analysis."""

    ASSET_TYPE_THREATS = {
        "ECU": ["S", "T", "I", "D", "E"],
        "Gateway": ["S", "T", "I", "D", "E"],
        "T-Box": ["S", "T", "R", "I", "D", "E"],
        "IVI": ["S", "T", "I", "D", "E"],
        "Sensor": ["S", "T", "D"],
        "Actuator": ["S", "T", "D"],
        "Network": ["S", "T", "I", "D"],
        "Data": ["T", "R", "I"],
    }

    def analyze_asset(
        self,
        asset_name: str,
        asset_type: str,
        interfaces: List[Dict[str, Any]] = None,
        data_types: List[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Analyze an asset for STRIDE threats.

        Returns list of identified threats.
        """
        threats = []

        # Get applicable threat types for this asset type
        applicable_types = self.ASSET_TYPE_THREATS.get(
            asset_type, ["S", "T", "R", "I", "D", "E"]
        )

        for threat_type in applicable_types:
            stride_info = STRIDE_TYPES[threat_type]

            threat = {
                "threat_name": f"{stride_info['name_zh']} - {asset_name}",
                "threat_type": threat_type,
                "threat_desc": self._generate_threat_description(
                    asset_name, asset_type, threat_type, stride_info
                ),
                "violated_property": stride_info["violated_property"],
            }

            # Add interface-specific threats
            if interfaces:
                for interface in interfaces:
                    interface_threat = self._analyze_interface_threat(
                        asset_name, interface, threat_type, stride_info
                    )
                    if interface_threat:
                        threats.append(interface_threat)

            threats.append(threat)

        return threats

    def _generate_threat_description(
        self,
        asset_name: str,
        asset_type: str,
        threat_type: str,
        stride_info: Dict[str, str],
    ) -> str:
        """Generate threat description."""
        templates = {
            "S": f"攻击者可能伪造{asset_name}的身份，冒充合法组件进行通信",
            "T": f"攻击者可能篡改{asset_name}处理或存储的数据",
            "R": f"用户或系统可能否认通过{asset_name}执行的操作",
            "I": f"敏感信息可能从{asset_name}泄露给未授权方",
            "D": f"攻击者可能使{asset_name}的服务不可用",
            "E": f"攻击者可能在{asset_name}上获取未授权的权限",
        }

        return templates.get(
            threat_type, f"针对{asset_name}的{stride_info['name_zh']}威胁"
        )

    def _analyze_interface_threat(
        self,
        asset_name: str,
        interface: Dict[str, Any],
        threat_type: str,
        stride_info: Dict[str, str],
    ) -> Dict[str, Any]:
        """Analyze interface-specific threat."""
        interface_name = interface.get("name", "Unknown")
        interface_type = interface.get("interface_type", "Unknown")

        # Only generate specific threats for network interfaces
        if interface_type in ["network", "wireless", "bus"]:
            return {
                "threat_name": f"{stride_info['name_zh']} - {asset_name} ({interface_name})",
                "threat_type": threat_type,
                "threat_desc": f"通过{interface_name}接口对{asset_name}进行{stride_info['description']}",
                "attack_surface": interface_name,
            }

        return None
