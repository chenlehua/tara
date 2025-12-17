"""
Threat Risk Agent
=================

Agent for threat analysis and risk assessment.
"""

from typing import Any, Dict, List

from app.common.constants import STRIDE_TYPES

from .base_agent import BaseAgent


class ThreatRiskAgent(BaseAgent):
    """Agent for threat analysis and risk assessment."""

    SYSTEM_PROMPT = """你是一个汽车网络安全威胁分析专家，精通ISO/SAE 21434标准。你的任务是：
1. 对汽车资产进行STRIDE威胁分析
2. 识别可能的攻击向量和攻击路径
3. 评估攻击可行性（专业知识、时间、设备、信息获取）
4. 进行风险评估（影响×可能性）

STRIDE类型：
- S (Spoofing): 欺骗/身份伪造
- T (Tampering): 篡改
- R (Repudiation): 否认
- I (Information Disclosure): 信息泄露
- D (Denial of Service): 拒绝服务
- E (Elevation of Privilege): 权限提升"""

    def __init__(self):
        super().__init__("ThreatRiskAgent")

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute threat analysis."""
        project_id = kwargs.get("project_id")
        assets = kwargs.get("assets", [])
        return await self.analyze_threats(project_id, assets)

    async def analyze_threats(
        self,
        project_id: int,
        assets: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Analyze threats for assets using STRIDE."""
        self.logger.info(f"Analyzing threats for {len(assets)} assets")

        if not assets:
            return {"threats": [], "attack_paths": []}

        assets_desc = "\n".join(
            [
                f"- {a.get('name', 'Unknown')}: {a.get('type', 'Unknown')} - {a.get('description', '')}"
                for a in assets[:20]  # Limit to 20 assets
            ]
        )

        prompt = f"""对以下汽车电子资产进行STRIDE威胁分析：

资产列表：
{assets_desc}

请为每个资产识别可能的威胁，并评估攻击可行性和风险。以JSON格式输出：
{{
    "threats": [
        {{
            "asset_name": "资产名称",
            "threat_name": "威胁名称",
            "stride_type": "S/T/R/I/D/E",
            "description": "威胁描述",
            "attack_vector": "攻击向量",
            "impact": {{
                "safety": 0-4,
                "financial": 0-4,
                "operational": 0-4,
                "privacy": 0-4
            }},
            "feasibility": "high/medium/low/very_low",
            "risk_level": "critical/high/medium/low/negligible"
        }}
    ],
    "attack_paths": [
        {{
            "name": "攻击路径名称",
            "steps": ["步骤1", "步骤2"],
            "target_asset": "目标资产"
        }}
    ]
}}"""

        response = await self.call_llm(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.5,
            max_tokens=4000,
        )

        try:
            import json

            return json.loads(response)
        except Exception:
            self.logger.error("Failed to parse threat analysis result")
            return {"threats": [], "attack_paths": [], "raw_response": response}

    async def assess_attack_feasibility(
        self,
        attack_description: str,
    ) -> Dict[str, Any]:
        """Assess attack feasibility parameters."""
        prompt = f"""评估以下攻击的可行性参数（基于ISO 21434）：

攻击描述：{attack_description}

请评估以下参数（数值越低表示攻击越难实施）：
- 专业知识 (0-8)：0=多名专家，8=无需专业知识
- 时间 (0-19)：0=≥6个月，19=<1小时
- 设备 (0-10)：0=多个定制设备，10=无需设备
- 信息获取 (0-7)：0=关键信息，7=公开信息

输出JSON格式：
{{
    "expertise": 数值,
    "elapsed_time": 数值,
    "equipment": 数值,
    "knowledge": 数值,
    "attack_potential": 总分,
    "feasibility_rating": "high/medium/low/very_low",
    "justification": "评估说明"
}}"""

        response = await self.call_llm(prompt=prompt, temperature=0.3)

        try:
            import json

            return json.loads(response)
        except Exception:
            return {"feasibility_rating": "unknown"}
