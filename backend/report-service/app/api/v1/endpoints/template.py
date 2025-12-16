"""Template endpoints."""
from fastapi import APIRouter

from tara_shared.utils import success_response

router = APIRouter()


# Predefined templates
TEMPLATES = [
    {
        "id": "iso21434",
        "name": "ISO/SAE 21434 标准模板",
        "description": "符合ISO/SAE 21434标准的完整TARA报告模板",
        "sections": [
            "executive_summary",
            "scope_definition",
            "asset_identification",
            "threat_scenarios",
            "impact_assessment",
            "attack_feasibility",
            "risk_assessment",
            "risk_treatment",
            "cybersecurity_goals",
            "appendices",
        ],
    },
    {
        "id": "unr155",
        "name": "UN R155 标准模板",
        "description": "符合UN R155/R156法规要求的CSMS报告模板",
        "sections": [
            "organization_info",
            "csms_overview",
            "risk_assessment",
            "mitigations",
            "verification",
            "incident_response",
        ],
    },
    {
        "id": "simple",
        "name": "简洁模板",
        "description": "简洁的威胁分析报告模板",
        "sections": [
            "summary",
            "assets",
            "threats",
            "risks",
            "recommendations",
        ],
    },
    {
        "id": "executive",
        "name": "管理层摘要模板",
        "description": "面向管理层的简要风险摘要报告",
        "sections": [
            "executive_summary",
            "risk_overview",
            "key_findings",
            "recommendations",
        ],
    },
]


@router.get("")
async def list_templates():
    """List available report templates."""
    return success_response(TEMPLATES)


@router.get("/{template_id}")
async def get_template(template_id: str):
    """Get template details."""
    template = next((t for t in TEMPLATES if t["id"] == template_id), None)
    if not template:
        return success_response(None, message="Template not found")
    return success_response(template)
