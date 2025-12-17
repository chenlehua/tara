"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import report, template, version

api_router = APIRouter()

api_router.include_router(report.router, prefix="/reports", tags=["reports"])
api_router.include_router(template.router, prefix="/templates", tags=["templates"])
api_router.include_router(version.router, prefix="/reports", tags=["report-versions"])
