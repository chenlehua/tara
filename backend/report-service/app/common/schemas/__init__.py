"""Pydantic schemas for TARA system."""

from .asset import (AssetCreate, AssetListResponse, AssetResponse, AssetUpdate,
                    DamageScenarioCreate, DamageScenarioResponse)
from .base import APIResponse, BaseSchema, PaginatedResponse
from .document import (DocumentCreate, DocumentListResponse, DocumentResponse,
                       DocumentUpdate)
from .project import (ProjectCreate, ProjectListResponse, ProjectResponse,
                      ProjectUpdate)
from .report import (GenerationProgressResponse, OneClickGenerateRequest,
                     OneClickGenerateResponse, ReportCreate,
                     ReportGenerateRequest, ReportListResponse, ReportResponse,
                     ReportUpdate)
from .report_version import (
    ApproveVersionRequest,
    ReportVersionCreate,
    ReportVersionDetailResponse,
    ReportVersionListResponse,
    ReportVersionResponse,
    RollbackRequest,
    SetBaselineRequest,
    VersionChangeDetail,
    VersionChangeSummary,
    VersionCompareRequest,
    VersionCompareResponse,
)
from .threat_risk import (AttackPathCreate, AttackPathResponse,
                          ControlMeasureCreate, ControlMeasureResponse,
                          ThreatRiskCreate, ThreatRiskListResponse,
                          ThreatRiskResponse, ThreatRiskUpdate)

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
    # Report Version
    "ReportVersionCreate",
    "ReportVersionResponse",
    "ReportVersionDetailResponse",
    "ReportVersionListResponse",
    "VersionCompareRequest",
    "VersionCompareResponse",
    "VersionChangeSummary",
    "VersionChangeDetail",
    "SetBaselineRequest",
    "ApproveVersionRequest",
    "RollbackRequest",
]
