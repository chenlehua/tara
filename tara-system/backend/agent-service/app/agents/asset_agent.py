"""
Asset Agent
===========

Agent for asset discovery and relationship building.
"""

from typing import Any, Dict, List

from .base_agent import BaseAgent


class AssetAgent(BaseAgent):
    """Agent for asset discovery."""

    SYSTEM_PROMPT = """你是一个汽车网络安全资产分析专家。你的任务是：
1. 从文档中识别汽车电子电气架构中的资产
2. 对资产进行分类（ECU、传感器、网关、网络等）
3. 识别资产之间的连接关系
4. 评估资产的安全属性（CIA）

资产类型包括：ECU、Sensor、Actuator、Gateway、T-Box、IVI、ADAS、BCM、VCU、BMS等。
关系类型包括：CONNECTS_TO（连接）、COMMUNICATES_WITH（通信）、CONTAINS（包含）等。"""

    def __init__(self):
        super().__init__("AssetAgent")

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute asset discovery."""
        project_id = kwargs.get("project_id")
        document_content = kwargs.get("document_content", "")
        return await self.discover_assets(project_id, document_content)

    async def discover_assets(
        self,
        project_id: int,
        document_content: str,
    ) -> Dict[str, Any]:
        """Discover assets from document content."""
        self.logger.info(f"Discovering assets for project {project_id}")
        
        if not document_content:
            return {"assets": [], "relations": []}
        
        prompt = f"""分析以下汽车技术文档，识别其中的电子电气资产。

文档内容：
{document_content[:8000]}

请以JSON格式输出识别到的资产和关系：
{{
    "assets": [
        {{
            "name": "资产名称",
            "type": "ECU/Sensor/Gateway/等",
            "category": "Hardware/Software/Data/Network",
            "description": "资产描述",
            "interfaces": ["CAN", "Ethernet"],
            "security_importance": "high/medium/low"
        }}
    ],
    "relations": [
        {{
            "source": "资产1名称",
            "target": "资产2名称",
            "type": "CONNECTS_TO/COMMUNICATES_WITH/CONTAINS",
            "protocol": "CAN/Ethernet/等"
        }}
    ]
}}"""

        response = await self.call_llm(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=4000,
        )
        
        try:
            import json
            result = json.loads(response)
            return result
        except Exception:
            self.logger.error("Failed to parse asset discovery result")
            return {"assets": [], "relations": [], "raw_response": response}

    async def classify_asset(self, asset_description: str) -> Dict[str, Any]:
        """Classify an asset based on its description."""
        prompt = f"""根据以下描述，对汽车电子资产进行分类：

{asset_description}

输出JSON格式：
{{
    "type": "资产类型",
    "category": "分类",
    "security_attributes": {{
        "confidentiality": "high/medium/low",
        "integrity": "high/medium/low",
        "availability": "high/medium/low"
    }}
}}"""

        response = await self.call_llm(prompt=prompt, temperature=0.3)
        
        try:
            import json
            return json.loads(response)
        except Exception:
            return {"type": "Unknown", "category": "Unknown"}
