"""API v1 router."""

from app.api.v1.endpoints import report, template
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(report.router, prefix="/reports", tags=["reports"])
api_router.include_router(template.router, prefix="/templates", tags=["templates"])
