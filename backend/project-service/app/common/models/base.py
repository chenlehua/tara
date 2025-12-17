"""
Base Model
==========

Base SQLAlchemy model with common fields.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, BigInteger, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class TimestampMixin:
    """Mixin for timestamp fields."""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class BaseModel(Base, TimestampMixin):
    """Abstract base model with common fields."""

    __abstract__ = True

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
