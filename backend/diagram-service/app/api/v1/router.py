"""API v1 router."""

from app.api.v1.endpoints import diagram
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(diagram.router, prefix="/diagrams", tags=["diagrams"])
