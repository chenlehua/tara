"""
Report Schemas
==============

Pydantic schemas for Report entity.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import BaseSchema, TimestampMixin, IDMixin, PaginatedResponse


class ReportSection(BaseSchema):
    """Report section definition."""

    id: str = Field(..., description="章节ID")
    title: str = Field(..., description="章节标题")
    order: int = Field(..., description="顺序")
    content: Optional[str] = Field(default=None, description="内容")
    subsections: List["ReportSection"] = Field(default_factory=list, description="子章节")


class ReportStatistics(BaseSchema):
    """Report statistics."""

    total_assets: int = Field(default=0, description="资产总数")
    total_threats: int = Field(default=0, description="威胁总数")
    total_attack_paths: int = Field(default=0, description="攻击路径总数")
    critical_risks: int = Field(default=0, description="严重风险数")
    high_risks: int = Field(default=0, description="高风险数")
    medium_risks: int = Field(default=0, description="中风险数")
    low_risks: int = Field(default=0, description="低风险数")
    negligible_risks: int = Field(default=0, description="可忽略风险数")
    total_controls: int = Field(default=0, description="控制措施总数")


class ReportBase(BaseSchema):
    """Base schema for Report."""

    name: str = Field(..., max_length=200, description="报告名称")
    report_type: str = Field(default="tara", description="报告类型")
    description: Optional[str] = Field(default=None, description="描述")
    template: Optional[str] = Field(default=None, description="模板")


class ReportCreate(ReportBase):
    """Schema for creating a Report."""

    project_id: int = Field(..., description="项目ID")
    sections: List[str] = Field(
        default_factory=list,
        description="包含的章节: scope, assets, threats, risks, controls, etc."
    )
    file_format: str = Field(default="pdf", description="输出格式: pdf, docx, html")
    author: Optional[str] = Field(default=None, description="作者")


class ReportUpdate(BaseSchema):
    """Schema for updating a Report."""

    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = None
    author: Optional[str] = None
    reviewer: Optional[str] = None
    version: Optional[str] = None


class ReportResponse(ReportBase, IDMixin, TimestampMixin):
    """Schema for Report response."""

    project_id: int = Field(..., description="项目ID")
    status: int = Field(default=0, description="状态")
    progress: int = Field(default=0, description="进度")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    file_path: Optional[str] = Field(default=None, description="文件路径")
    file_format: Optional[str] = Field(default=None, description="文件格式")
    file_size: Optional[int] = Field(default=None, description="文件大小")
    version: str = Field(default="1.0", description="版本")
    author: Optional[str] = Field(default=None, description="作者")
    reviewer: Optional[str] = Field(default=None, description="审核人")
    review_status: int = Field(default=0, description="审核状态")
    download_url: Optional[str] = Field(default=None, description="下载链接")
    statistics: Optional[ReportStatistics] = Field(default=None, description="统计数据")


class ReportDetailResponse(ReportResponse):
    """Detailed report response with content."""

    content: Dict[str, Any] = Field(default_factory=dict, description="报告内容")
    sections: List[ReportSection] = Field(default_factory=list, description="章节列表")


class ReportListResponse(PaginatedResponse[ReportResponse]):
    """Paginated list of Reports."""
    pass


class ReportTemplateInfo(BaseSchema):
    """Report template information."""

    id: str = Field(..., description="模板ID")
    name: str = Field(..., description="模板名称")
    description: Optional[str] = Field(default=None, description="描述")
    standard: str = Field(..., description="适用标准")
    sections: List[str] = Field(default_factory=list, description="包含章节")
    preview_url: Optional[str] = Field(default=None, description="预览链接")


class ReportGenerateRequest(BaseSchema):
    """Request to generate a report."""

    project_id: int = Field(..., description="项目ID")
    template_id: str = Field(default="iso21434_tara", description="模板ID")
    name: str = Field(..., description="报告名称")
    file_format: str = Field(default="pdf", description="输出格式")
    
    # Options
    include_charts: bool = Field(default=True, description="包含图表")
    include_appendix: bool = Field(default=True, description="包含附录")
    language: str = Field(default="zh", description="语言")
    
    # Sections to include
    sections: List[str] = Field(
        default=["scope", "assets", "damage_scenarios", "threats", 
                 "attack_paths", "risk_assessment", "risk_treatment"],
        description="包含的章节"
    )
