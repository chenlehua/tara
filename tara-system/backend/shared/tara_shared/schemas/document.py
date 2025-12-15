"""
Document Schemas
================

Pydantic schemas for Document entity.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import BaseSchema, TimestampMixin, IDMixin, PaginatedResponse


class DocumentBase(BaseSchema):
    """Base schema for Document."""

    filename: str = Field(..., max_length=255, description="文件名")
    doc_type: Optional[str] = Field(default=None, max_length=50, description="文档类型")
    doc_category: Optional[str] = Field(default=None, max_length=50, description="文档分类")


class DocumentCreate(DocumentBase):
    """Schema for creating a Document (metadata only, file uploaded separately)."""

    project_id: int = Field(..., description="项目ID")
    file_path: str = Field(..., max_length=500, description="文件存储路径")
    file_size: Optional[int] = Field(default=None, description="文件大小")
    file_type: Optional[str] = Field(default=None, max_length=50, description="MIME类型")
    file_extension: Optional[str] = Field(default=None, max_length=20, description="扩展名")


class DocumentUpdate(BaseSchema):
    """Schema for updating a Document."""

    doc_type: Optional[str] = Field(default=None, max_length=50)
    doc_category: Optional[str] = Field(default=None, max_length=50)
    title: Optional[str] = Field(default=None, max_length=255)
    metadata: Optional[Dict[str, Any]] = None


class DocumentParseResult(BaseSchema):
    """Schema for document parse result."""

    title: Optional[str] = Field(default=None, description="文档标题")
    content: Optional[str] = Field(default=None, description="文本内容")
    structure: Dict[str, Any] = Field(default_factory=dict, description="文档结构")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    page_count: Optional[int] = Field(default=None, description="页数")


class DocumentResponse(DocumentBase, IDMixin, TimestampMixin):
    """Schema for Document response."""

    project_id: int = Field(..., description="项目ID")
    file_path: str = Field(..., description="文件路径")
    file_size: Optional[int] = Field(default=None, description="文件大小")
    file_type: Optional[str] = Field(default=None, description="MIME类型")
    file_extension: Optional[str] = Field(default=None, description="扩展名")
    parse_status: int = Field(default=0, description="解析状态")
    parse_progress: int = Field(default=0, description="解析进度")
    parse_error: Optional[str] = Field(default=None, description="解析错误")
    title: Optional[str] = Field(default=None, description="文档标题")
    page_count: Optional[int] = Field(default=None, description="页数")
    download_url: Optional[str] = Field(default=None, description="下载链接")


class DocumentDetailResponse(DocumentResponse):
    """Detailed document response with content."""

    content: Optional[str] = Field(default=None, description="文本内容")
    structure: Dict[str, Any] = Field(default_factory=dict, description="文档结构")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    ocr_result: Dict[str, Any] = Field(default_factory=dict, description="OCR结果")


class DocumentListResponse(PaginatedResponse[DocumentResponse]):
    """Paginated list of Documents."""
    pass


class DocumentUploadResponse(BaseSchema):
    """Response after file upload."""

    document_id: int = Field(..., description="文档ID")
    filename: str = Field(..., description="文件名")
    file_path: str = Field(..., description="存储路径")
    file_size: int = Field(..., description="文件大小")
    message: str = Field(default="上传成功", description="消息")


class ParseRequest(BaseSchema):
    """Request to parse a document."""

    enable_ocr: bool = Field(default=True, description="启用OCR")
    enable_structure: bool = Field(default=True, description="提取结构")
    enable_embedding: bool = Field(default=False, description="生成向量")
    language: str = Field(default="zh", description="语言")
