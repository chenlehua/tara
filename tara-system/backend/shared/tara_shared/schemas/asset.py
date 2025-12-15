"""
Asset Schemas
=============

Pydantic schemas for Asset and DamageScenario entities.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import BaseSchema, TimestampMixin, IDMixin, PaginatedResponse


# ==================== Security Attributes ====================

class SecurityAttribute(BaseSchema):
    """Security attribute (C/I/A)."""

    level: str = Field(..., description="等级: none, low, medium, high, critical")
    description: Optional[str] = Field(default=None, description="描述")


class SecurityAttributes(BaseSchema):
    """CIA security attributes."""

    confidentiality: Optional[SecurityAttribute] = Field(default=None, description="机密性")
    integrity: Optional[SecurityAttribute] = Field(default=None, description="完整性")
    availability: Optional[SecurityAttribute] = Field(default=None, description="可用性")


# ==================== Interface ====================

class AssetInterface(BaseSchema):
    """Asset interface definition."""

    name: str = Field(..., description="接口名称")
    interface_type: str = Field(..., description="接口类型: bus, network, wireless, etc.")
    protocol: Optional[str] = Field(default=None, description="协议")
    direction: Optional[str] = Field(default=None, description="方向: in, out, bidirectional")
    description: Optional[str] = Field(default=None, description="描述")


# ==================== Damage Scenario ====================

class DamageScenarioBase(BaseSchema):
    """Base schema for DamageScenario."""

    name: str = Field(..., max_length=200, description="损害场景名称")
    description: Optional[str] = Field(default=None, description="描述")
    safety_impact: int = Field(default=0, ge=0, le=4, description="安全影响")
    financial_impact: int = Field(default=0, ge=0, le=4, description="财务影响")
    operational_impact: int = Field(default=0, ge=0, le=4, description="运营影响")
    privacy_impact: int = Field(default=0, ge=0, le=4, description="隐私影响")
    impact_justification: Optional[str] = Field(default=None, description="影响评估说明")
    stakeholders: List[str] = Field(default_factory=list, description="受影响的利益相关者")


class DamageScenarioCreate(DamageScenarioBase):
    """Schema for creating a DamageScenario."""

    asset_id: int = Field(..., description="资产ID")


class DamageScenarioResponse(DamageScenarioBase, IDMixin, TimestampMixin):
    """Schema for DamageScenario response."""

    asset_id: int = Field(..., description="资产ID")
    impact_level: Optional[int] = Field(default=None, description="综合影响等级")


# ==================== Asset ====================

class AssetBase(BaseSchema):
    """Base schema for Asset."""

    name: str = Field(..., min_length=1, max_length=200, description="资产名称")
    asset_type: str = Field(..., max_length=50, description="资产类型")
    category: Optional[str] = Field(default=None, max_length=50, description="资产分类")
    description: Optional[str] = Field(default=None, description="描述")
    version: Optional[str] = Field(default=None, max_length=50, description="版本")
    vendor: Optional[str] = Field(default=None, max_length=100, description="供应商")
    model_number: Optional[str] = Field(default=None, max_length=100, description="型号")
    location: Optional[str] = Field(default=None, max_length=200, description="物理位置")
    zone: Optional[str] = Field(default=None, max_length=50, description="安全区域")
    trust_boundary: Optional[str] = Field(default=None, max_length=50, description="信任边界")
    criticality: Optional[str] = Field(default=None, description="关键性等级")


class AssetCreate(AssetBase):
    """Schema for creating an Asset."""

    project_id: int = Field(..., description="项目ID")
    parent_id: Optional[int] = Field(default=None, description="父资产ID")
    security_attrs: Optional[SecurityAttributes] = Field(default=None, description="安全属性")
    interfaces: List[AssetInterface] = Field(default_factory=list, description="接口列表")
    data_types: List[str] = Field(default_factory=list, description="数据类型")
    is_external: int = Field(default=0, ge=0, le=1, description="是否外部资产")


class AssetUpdate(BaseSchema):
    """Schema for updating an Asset."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    asset_type: Optional[str] = Field(default=None, max_length=50)
    category: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = None
    version: Optional[str] = Field(default=None, max_length=50)
    vendor: Optional[str] = Field(default=None, max_length=100)
    model_number: Optional[str] = Field(default=None, max_length=100)
    location: Optional[str] = Field(default=None, max_length=200)
    zone: Optional[str] = Field(default=None, max_length=50)
    trust_boundary: Optional[str] = Field(default=None, max_length=50)
    criticality: Optional[str] = None
    security_attrs: Optional[SecurityAttributes] = None
    interfaces: Optional[List[AssetInterface]] = None
    data_types: Optional[List[str]] = None
    is_external: Optional[int] = Field(default=None, ge=0, le=1)
    status: Optional[int] = Field(default=None, ge=0, le=1)
    parent_id: Optional[int] = None


class AssetResponse(AssetBase, IDMixin, TimestampMixin):
    """Schema for Asset response."""

    project_id: int = Field(..., description="项目ID")
    parent_id: Optional[int] = Field(default=None, description="父资产ID")
    security_attrs: Optional[Dict[str, Any]] = Field(default=None, description="安全属性")
    interfaces: List[Dict[str, Any]] = Field(default_factory=list, description="接口列表")
    data_types: List[str] = Field(default_factory=list, description="数据类型")
    is_external: int = Field(default=0, description="是否外部资产")
    status: int = Field(default=1, description="状态")
    source: str = Field(default="manual", description="来源")
    damage_scenario_count: int = Field(default=0, description="损害场景数量")
    threat_count: int = Field(default=0, description="关联威胁数量")


class AssetDetailResponse(AssetResponse):
    """Detailed asset response with children and scenarios."""

    children: List["AssetResponse"] = Field(default_factory=list, description="子资产")
    damage_scenarios: List[DamageScenarioResponse] = Field(
        default_factory=list, description="损害场景"
    )


class AssetListResponse(PaginatedResponse[AssetResponse]):
    """Paginated list of Assets."""
    pass


# ==================== Asset Discovery ====================

class AssetDiscoveryRequest(BaseSchema):
    """Request for AI asset discovery."""

    document_ids: List[int] = Field(..., description="文档ID列表")
    include_relations: bool = Field(default=True, description="是否识别关系")


class AssetDiscoveryResult(BaseSchema):
    """Result of asset discovery."""

    discovered_assets: List[AssetCreate] = Field(default_factory=list, description="发现的资产")
    relations: List[Dict[str, Any]] = Field(default_factory=list, description="资产关系")
    confidence: float = Field(default=0.0, description="置信度")


# ==================== Asset Graph ====================

class AssetNode(BaseSchema):
    """Asset node for graph visualization."""

    id: int = Field(..., description="资产ID")
    name: str = Field(..., description="资产名称")
    asset_type: str = Field(..., description="资产类型")
    category: Optional[str] = Field(default=None, description="分类")


class AssetEdge(BaseSchema):
    """Asset edge for graph visualization."""

    source: int = Field(..., description="源资产ID")
    target: int = Field(..., description="目标资产ID")
    relation_type: str = Field(..., description="关系类型")
    properties: Dict[str, Any] = Field(default_factory=dict, description="关系属性")


class AssetGraph(BaseSchema):
    """Asset graph for visualization."""

    nodes: List[AssetNode] = Field(default_factory=list, description="节点列表")
    edges: List[AssetEdge] = Field(default_factory=list, description="边列表")
