"""
Threat Risk Schemas
===================

Pydantic schemas for ThreatRisk, AttackPath, and ControlMeasure entities.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import BaseSchema, TimestampMixin, IDMixin, PaginatedResponse


# ==================== Control Measure ====================

class ControlMeasureBase(BaseSchema):
    """Base schema for ControlMeasure."""

    name: str = Field(..., max_length=200, description="控制措施名称")
    control_type: Optional[str] = Field(default=None, description="类型")
    category: Optional[str] = Field(default=None, description="分类")
    description: Optional[str] = Field(default=None, description="描述")
    implementation: Optional[str] = Field(default=None, description="实施方式")
    effectiveness: Optional[str] = Field(default=None, description="有效性")
    cost_estimate: Optional[str] = Field(default=None, description="成本估算")
    iso21434_ref: Optional[str] = Field(default=None, description="ISO 21434参考")


class ControlMeasureCreate(ControlMeasureBase):
    """Schema for creating a ControlMeasure."""

    attack_path_id: int = Field(..., description="攻击路径ID")


class ControlMeasureResponse(ControlMeasureBase, IDMixin, TimestampMixin):
    """Schema for ControlMeasure response."""

    attack_path_id: int = Field(..., description="攻击路径ID")
    implementation_status: int = Field(default=0, description="实施状态")
    verification_status: int = Field(default=0, description="验证状态")


# ==================== Attack Path ====================

class AttackStep(BaseSchema):
    """Attack step in attack path."""

    order: int = Field(..., description="步骤顺序")
    action: str = Field(..., description="攻击动作")
    target: Optional[str] = Field(default=None, description="目标")
    technique: Optional[str] = Field(default=None, description="攻击技术")
    description: Optional[str] = Field(default=None, description="描述")


class AttackPathBase(BaseSchema):
    """Base schema for AttackPath."""

    name: str = Field(..., max_length=200, description="攻击路径名称")
    description: Optional[str] = Field(default=None, description="描述")
    steps: List[AttackStep] = Field(default_factory=list, description="攻击步骤")
    
    # Attack potential parameters
    expertise: int = Field(default=0, ge=0, le=8, description="专业知识")
    elapsed_time: int = Field(default=0, ge=0, le=19, description="时间")
    equipment: int = Field(default=0, ge=0, le=10, description="设备")
    knowledge: int = Field(default=0, ge=0, le=7, description="信息获取")
    window_of_opportunity: int = Field(default=0, ge=0, le=10, description="机会窗口")
    
    prerequisites: List[str] = Field(default_factory=list, description="前置条件")
    attack_techniques: List[str] = Field(default_factory=list, description="ATT&CK技术")


class AttackPathCreate(AttackPathBase):
    """Schema for creating an AttackPath."""

    threat_risk_id: int = Field(..., description="威胁风险ID")


class AttackPathResponse(AttackPathBase, IDMixin, TimestampMixin):
    """Schema for AttackPath response."""

    threat_risk_id: int = Field(..., description="威胁风险ID")
    attack_potential: Optional[int] = Field(default=None, description="攻击潜力值")
    feasibility_rating: Optional[str] = Field(default=None, description="可行性评级")
    control_measures: List[ControlMeasureResponse] = Field(
        default_factory=list, description="控制措施"
    )


# ==================== Threat Risk ====================

class ThreatRiskBase(BaseSchema):
    """Base schema for ThreatRisk."""

    threat_name: str = Field(..., max_length=200, description="威胁名称")
    threat_type: Optional[str] = Field(default=None, description="威胁类型(STRIDE)")
    threat_desc: Optional[str] = Field(default=None, description="威胁描述")
    attack_vector: Optional[str] = Field(default=None, description="攻击向量")
    attack_surface: Optional[str] = Field(default=None, description="攻击面")
    threat_source: Optional[str] = Field(default=None, description="威胁源")
    threat_agent: Optional[str] = Field(default=None, description="威胁主体")


class ThreatRiskCreate(ThreatRiskBase):
    """Schema for creating a ThreatRisk."""

    project_id: int = Field(..., description="项目ID")
    asset_id: int = Field(..., description="资产ID")
    damage_scenario_id: Optional[int] = Field(default=None, description="损害场景ID")
    
    # Impact
    safety_impact: int = Field(default=0, ge=0, le=4, description="安全影响")
    financial_impact: int = Field(default=0, ge=0, le=4, description="财务影响")
    operational_impact: int = Field(default=0, ge=0, le=4, description="运营影响")
    privacy_impact: int = Field(default=0, ge=0, le=4, description="隐私影响")
    
    # External references
    cwe_ids: List[str] = Field(default_factory=list, description="CWE ID列表")
    capec_ids: List[str] = Field(default_factory=list, description="CAPEC ID列表")


class ThreatRiskUpdate(BaseSchema):
    """Schema for updating a ThreatRisk."""

    threat_name: Optional[str] = Field(default=None, max_length=200)
    threat_type: Optional[str] = None
    threat_desc: Optional[str] = None
    attack_vector: Optional[str] = None
    attack_surface: Optional[str] = None
    threat_source: Optional[str] = None
    threat_agent: Optional[str] = None
    
    # Impact
    safety_impact: Optional[int] = Field(default=None, ge=0, le=4)
    financial_impact: Optional[int] = Field(default=None, ge=0, le=4)
    operational_impact: Optional[int] = Field(default=None, ge=0, le=4)
    privacy_impact: Optional[int] = Field(default=None, ge=0, le=4)
    impact_level: Optional[int] = Field(default=None, ge=0, le=4)
    
    # Likelihood and Risk
    likelihood: Optional[int] = Field(default=None, ge=0, le=4)
    
    # Treatment
    treatment: Optional[str] = None
    treatment_desc: Optional[str] = None
    
    # CAL
    cal: Optional[int] = Field(default=None, ge=1, le=4)


class ThreatRiskResponse(ThreatRiskBase, IDMixin, TimestampMixin):
    """Schema for ThreatRisk response."""

    project_id: int = Field(..., description="项目ID")
    asset_id: int = Field(..., description="资产ID")
    asset_name: Optional[str] = Field(default=None, description="资产名称")
    damage_scenario_id: Optional[int] = Field(default=None, description="损害场景ID")
    
    # Impact
    safety_impact: int = Field(default=0, description="安全影响")
    financial_impact: int = Field(default=0, description="财务影响")
    operational_impact: int = Field(default=0, description="运营影响")
    privacy_impact: int = Field(default=0, description="隐私影响")
    impact_level: Optional[int] = Field(default=None, description="综合影响等级")
    
    # Risk
    likelihood: Optional[int] = Field(default=None, description="可能性等级")
    risk_value: Optional[int] = Field(default=None, description="风险值")
    risk_level: Optional[str] = Field(default=None, description="风险等级")
    
    # Treatment
    treatment: Optional[str] = Field(default=None, description="处置决策")
    treatment_desc: Optional[str] = Field(default=None, description="处置说明")
    residual_risk: Optional[int] = Field(default=None, description="残余风险")
    cal: Optional[int] = Field(default=None, description="网络安全保障等级")
    
    # Source
    source: str = Field(default="manual", description="来源")
    
    # References
    cwe_ids: List[str] = Field(default_factory=list, description="CWE ID列表")
    capec_ids: List[str] = Field(default_factory=list, description="CAPEC ID列表")
    
    # Attack paths count
    attack_path_count: int = Field(default=0, description="攻击路径数量")


class ThreatRiskDetailResponse(ThreatRiskResponse):
    """Detailed threat risk response with attack paths."""

    attack_paths: List[AttackPathResponse] = Field(
        default_factory=list, description="攻击路径"
    )


class ThreatRiskListResponse(PaginatedResponse[ThreatRiskResponse]):
    """Paginated list of ThreatRisks."""
    pass


# ==================== Risk Assessment ====================

class RiskAssessmentRequest(BaseSchema):
    """Request for risk assessment."""

    threat_risk_id: int = Field(..., description="威胁风险ID")
    impact_level: int = Field(..., ge=0, le=4, description="影响等级")
    likelihood: int = Field(..., ge=0, le=4, description="可能性")
    justification: Optional[str] = Field(default=None, description="评估说明")


class RiskMatrixData(BaseSchema):
    """Data for risk matrix visualization."""

    matrix: List[List[int]] = Field(default_factory=list, description="风险矩阵数据")
    # matrix[impact][likelihood] = count of threats
    threats_by_level: Dict[str, int] = Field(
        default_factory=dict, description="按风险等级统计"
    )
    # {"critical": 3, "high": 7, "medium": 12, ...}


# ==================== STRIDE Analysis ====================

class STRIDEAnalysisRequest(BaseSchema):
    """Request for STRIDE threat analysis."""

    asset_ids: List[int] = Field(..., description="资产ID列表")
    include_attack_paths: bool = Field(default=True, description="是否生成攻击路径")


class STRIDEAnalysisResult(BaseSchema):
    """Result of STRIDE analysis."""

    asset_id: int = Field(..., description="资产ID")
    asset_name: str = Field(..., description="资产名称")
    threats: List[ThreatRiskCreate] = Field(default_factory=list, description="识别的威胁")
    confidence: float = Field(default=0.0, description="置信度")


# ==================== Attack Tree ====================

class AttackTreeNode(BaseSchema):
    """Node in attack tree."""

    id: str = Field(..., description="节点ID")
    label: str = Field(..., description="节点标签")
    node_type: str = Field(..., description="节点类型: goal, and, or, leaf")
    children: List["AttackTreeNode"] = Field(default_factory=list, description="子节点")
    attack_potential: Optional[int] = Field(default=None, description="攻击潜力")


class AttackTreeData(BaseSchema):
    """Attack tree data for visualization."""

    threat_id: int = Field(..., description="威胁ID")
    threat_name: str = Field(..., description="威胁名称")
    root: AttackTreeNode = Field(..., description="根节点")
