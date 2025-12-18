"""
Base Schemas
============

Base Pydantic models and common schemas.
"""

from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
        },
    )


class TimestampMixin(BaseSchema):
    """Mixin for timestamp fields."""

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class IDMixin(BaseSchema):
    """Mixin for ID field."""

    id: int


# Generic type for paginated response
T = TypeVar("T")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Paginated response schema."""

    items: List[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(default=0, description="总数量")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=20, description="每页数量")
    pages: int = Field(default=0, description="总页数")

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int = 1,
        page_size: int = 20,
    ) -> "PaginatedResponse[T]":
        """Create paginated response."""
        pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )


class APIResponse(BaseSchema, Generic[T]):
    """Standard API response schema."""

    success: bool = Field(default=True, description="是否成功")
    code: int = Field(default=200, description="状态码")
    message: str = Field(default="success", description="消息")
    data: Optional[T] = Field(default=None, description="数据")

    @classmethod
    def success_response(
        cls,
        data: T = None,
        message: str = "success",
    ) -> "APIResponse[T]":
        """Create success response."""
        return cls(success=True, code=200, message=message, data=data)

    @classmethod
    def error_response(
        cls,
        message: str,
        code: int = 400,
    ) -> "APIResponse[None]":
        """Create error response."""
        return cls(success=False, code=code, message=message, data=None)


class QueryParams(BaseSchema):
    """Common query parameters."""

    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    keyword: Optional[str] = Field(default=None, description="搜索关键词")
    sort_by: Optional[str] = Field(default="created_at", description="排序字段")
    sort_order: Optional[str] = Field(default="desc", description="排序方向: asc/desc")

    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size
