"""Pydantic schemas for TARA system."""

from .base import BaseSchema, PaginatedResponse, APIResponse
from .project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from .document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse,
)
from .asset import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    AssetListResponse,
    DamageScenarioCreate,
    DamageScenarioResponse,
)
from .threat_risk import (
    ThreatRiskCreate,
    ThreatRiskUpdate,
    ThreatRiskResponse,
    ThreatRiskListResponse,
    AttackPathCreate,
    AttackPathResponse,
    ControlMeasureCreate,
    ControlMeasureResponse,
)
from .report import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportListResponse,
    ReportGenerateRequest,
    OneClickGenerateRequest,
    OneClickGenerateResponse,
    GenerationProgressResponse,
)

__all__ = [
    # Base
    "BaseSchema",
    "PaginatedResponse",
    "APIResponse",
    # Project
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectListResponse",
    # Document
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentResponse",
    "DocumentListResponse",
    # Asset
    "AssetCreate",
    "AssetUpdate",
    "AssetResponse",
    "AssetListResponse",
    "DamageScenarioCreate",
    "DamageScenarioResponse",
    # ThreatRisk
    "ThreatRiskCreate",
    "ThreatRiskUpdate",
    "ThreatRiskResponse",
    "ThreatRiskListResponse",
    "AttackPathCreate",
    "AttackPathResponse",
    "ControlMeasureCreate",
    "ControlMeasureResponse",
    # Report
    "ReportCreate",
    "ReportUpdate",
    "ReportResponse",
    "ReportListResponse",
    "ReportGenerateRequest",
    "OneClickGenerateRequest",
    "OneClickGenerateResponse",
    "GenerationProgressResponse",
]
