"""
Report Agent
============

Agent for report generation.
"""

from typing import Any, Dict

from .base_agent import BaseAgent


class ReportAgent(BaseAgent):
    """Agent for TARA report generation."""

    SYSTEM_PROMPT = """你是一个专业的汽车网络安全报告撰写专家。你的任务是：
1. 根据TARA分析结果撰写符合ISO/SAE 21434标准的报告
2. 使用专业但清晰的语言
3. 包含所有必要的章节：范围、资产识别、威胁分析、风险评估、处置建议
4. 提供可操作的安全建议"""

    def __init__(self):
        super().__init__("ReportAgent")

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute report generation."""
        project_id = kwargs.get("project_id")
        return await self.generate_report(project_id)

    async def generate_report(self, project_id: int) -> Dict[str, Any]:
        """Generate TARA report for a project."""
        self.logger.info(f"Generating report for project {project_id}")
        
        # In production, this would:
        # 1. Fetch all project data
        # 2. Generate each section
        # 3. Create charts and diagrams
        # 4. Export to PDF/Word
        
        return {
            "report_id": None,
            "status": "generated",
            "sections": [
                "executive_summary",
                "scope",
                "asset_identification",
                "threat_analysis",
                "risk_assessment",
                "risk_treatment",
                "appendix",
            ],
        }

    async def write_section(
        self,
        section_type: str,
        data: Dict[str, Any],
    ) -> str:
        """Write a specific report section."""
        prompts = {
            "executive_summary": "撰写执行摘要，总结TARA分析的主要发现和建议。",
            "scope": "撰写分析范围章节，说明分析对象和边界。",
            "asset_identification": "撰写资产识别章节，描述已识别的资产及其属性。",
            "threat_analysis": "撰写威胁分析章节，描述已识别的威胁和攻击场景。",
            "risk_assessment": "撰写风险评估章节，说明风险等级和评估依据。",
            "risk_treatment": "撰写风险处置章节，提出处置建议和措施。",
        }
        
        prompt = f"""{prompts.get(section_type, '撰写报告章节')}

数据：
{str(data)[:3000]}

请以专业格式撰写该章节内容。"""

        return await self.call_llm(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.5,
            max_tokens=2000,
        )
