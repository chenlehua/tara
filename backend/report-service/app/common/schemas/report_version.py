"""
Report Version Schemas
======================

Pydantic schemas for report version management.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import BaseSchema, IDMixin, TimestampMixin


class ReportVersionChangeBase(BaseSchema):
    """Base schema for version change record."""

    change_type: str = Field(..., description="变更类型: add, modify, delete")
    entity_type: str = Field(..., description="实体类型: asset, threat, measure")
    entity_id: Optional[int] = Field(default=None, description="实体ID")
    entity_name: Optional[str] = Field(default=None, description="实体名称")
    field_name: Optional[str] = Field(default=None, description="变更字段")
    old_value: Optional[str] = Field(default=None, description="旧值")
    new_value: Optional[str] = Field(default=None, description="新值")


class ReportVersionChangeResponse(ReportVersionChangeBase, IDMixin):
    """Response schema for version change record."""

    version_id: int = Field(..., description="版本ID")
    created_at: datetime = Field(..., description="创建时间")


class ReportVersionBase(BaseSchema):
    """Base schema for report version."""

    version_number: str = Field(..., description="版本号")
    change_summary: Optional[str] = Field(default=None, description="变更摘要")
    change_reason: Optional[str] = Field(default=None, description="变更原因")


class ReportVersionCreate(BaseSchema):
    """Schema for creating a new version."""

    is_major: bool = Field(default=False, description="是否为主版本升级")
    change_summary: Optional[str] = Field(default=None, description="变更摘要")
    change_reason: Optional[str] = Field(default=None, description="变更原因")
    created_by: Optional[str] = Field(default=None, description="创建人")


class ReportVersionResponse(ReportVersionBase, IDMixin):
    """Response schema for report version."""

    report_id: int = Field(..., description="报告ID")
    major_version: int = Field(..., description="主版本号")
    minor_version: int = Field(..., description="次版本号")
    status: str = Field(default="draft", description="状态")
    is_baseline: bool = Field(default=False, description="是否为基线版本")
    is_current: bool = Field(default=False, description="是否为当前版本")
    created_by: Optional[str] = Field(default=None, description="创建人")
    approved_by: Optional[str] = Field(default=None, description="审批人")
    approved_at: Optional[datetime] = Field(default=None, description="审批时间")
    created_at: datetime = Field(..., description="创建时间")
    
    # Statistics summary
    statistics: Optional[Dict[str, Any]] = Field(default=None, description="统计数据")


class ReportVersionDetailResponse(ReportVersionResponse):
    """Detailed response including content and changes."""

    content: Optional[Dict[str, Any]] = Field(default=None, description="报告内容")
    sections: Optional[List[Dict[str, Any]]] = Field(default=None, description="章节列表")
    snapshot_data: Optional[Dict[str, Any]] = Field(default=None, description="快照数据")
    file_paths: Optional[Dict[str, str]] = Field(default=None, description="文件路径")
    changes: List[ReportVersionChangeResponse] = Field(default_factory=list, description="变更记录")


class ReportVersionListResponse(BaseSchema):
    """Response for version list."""

    versions: List[ReportVersionResponse] = Field(..., description="版本列表")
    total: int = Field(..., description="总数")
    current_version: Optional[str] = Field(default=None, description="当前版本号")
    baseline_version: Optional[str] = Field(default=None, description="基线版本号")


class VersionCompareRequest(BaseSchema):
    """Request for comparing two versions."""

    version_a: str = Field(..., description="版本A")
    version_b: str = Field(..., description="版本B")


class VersionChangeSummary(BaseSchema):
    """Summary of changes between versions."""

    added: int = Field(default=0, description="新增数量")
    modified: int = Field(default=0, description="修改数量")
    deleted: int = Field(default=0, description="删除数量")


class VersionChangeDetail(BaseSchema):
    """Detail of a single change."""

    change_type: str = Field(..., description="变更类型")
    entity_type: str = Field(..., description="实体类型")
    entity_name: Optional[str] = Field(default=None, description="实体名称")
    field_name: Optional[str] = Field(default=None, description="字段名称")
    old_value: Optional[Any] = Field(default=None, description="旧值")
    new_value: Optional[Any] = Field(default=None, description="新值")
    description: Optional[str] = Field(default=None, description="变更描述")


class VersionCompareResponse(BaseSchema):
    """Response for version comparison."""

    version_a: str = Field(..., description="版本A")
    version_b: str = Field(..., description="版本B")
    summary: VersionChangeSummary = Field(..., description="变更摘要")
    changes: List[VersionChangeDetail] = Field(default_factory=list, description="变更详情")


class SetBaselineRequest(BaseSchema):
    """Request for setting baseline version."""

    comment: Optional[str] = Field(default=None, description="备注")


class ApproveVersionRequest(BaseSchema):
    """Request for approving a version."""

    approved_by: str = Field(..., description="审批人")
    comment: Optional[str] = Field(default=None, description="审批意见")


class RollbackRequest(BaseSchema):
    """Request for rolling back to a version."""

    created_by: Optional[str] = Field(default=None, description="操作人")
    reason: Optional[str] = Field(default=None, description="回滚原因")
