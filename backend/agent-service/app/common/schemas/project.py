"""
Project Schemas
===============

Pydantic schemas for Project entity.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import BaseSchema, IDMixin, PaginatedResponse, TimestampMixin


class ProjectBase(BaseSchema):
    """Base schema for Project."""

    name: str = Field(..., min_length=1, max_length=200, description="项目名称")
    description: Optional[str] = Field(default=None, description="项目描述")
    vehicle_type: Optional[str] = Field(
        default=None, max_length=50, description="车辆类型"
    )
    vehicle_model: Optional[str] = Field(
        default=None, max_length=100, description="车型"
    )
    vehicle_year: Optional[str] = Field(default=None, max_length=10, description="年份")
    standard: str = Field(default="ISO/SAE 21434", description="参考标准")
    scope: Optional[str] = Field(default=None, description="分析范围")
    owner: Optional[str] = Field(default=None, max_length=100, description="负责人")
    team: List[str] = Field(default_factory=list, description="项目团队")
    tags: List[str] = Field(default_factory=list, description="标签")


class ProjectCreate(ProjectBase):
    """Schema for creating a Project."""

    config: Dict[str, Any] = Field(default_factory=dict, description="项目配置")


class ProjectUpdate(BaseSchema):
    """Schema for updating a Project."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    vehicle_type: Optional[str] = Field(default=None, max_length=50)
    vehicle_model: Optional[str] = Field(default=None, max_length=100)
    vehicle_year: Optional[str] = Field(default=None, max_length=10)
    standard: Optional[str] = None
    scope: Optional[str] = None
    status: Optional[int] = Field(default=None, ge=0, le=3)
    owner: Optional[str] = Field(default=None, max_length=100)
    team: Optional[List[str]] = None
    config: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class ProjectStats(BaseSchema):
    """Statistics for a Project."""

    document_count: int = Field(default=0, description="文档数量")
    asset_count: int = Field(default=0, description="资产数量")
    threat_count: int = Field(default=0, description="威胁数量")
    report_count: int = Field(default=0, description="报告数量")
    critical_risk_count: int = Field(default=0, description="严重风险数量")
    high_risk_count: int = Field(default=0, description="高风险数量")


class ProjectResponse(ProjectBase, IDMixin, TimestampMixin):
    """Schema for Project response."""

    status: int = Field(default=0, description="状态")
    config: Dict[str, Any] = Field(default_factory=dict)
    stats: Optional[ProjectStats] = Field(default=None, description="统计数据")


class ProjectListResponse(PaginatedResponse[ProjectResponse]):
    """Paginated list of Projects."""

    pass


class ProjectCloneRequest(BaseSchema):
    """Request to clone a project."""

    name: str = Field(..., description="新项目名称")
    include_documents: bool = Field(default=True, description="是否包含文档")
    include_assets: bool = Field(default=True, description="是否包含资产")
    include_threats: bool = Field(default=True, description="是否包含威胁分析")
