"""API v1 router."""
from fastapi import APIRouter

from app.api.v1.endpoints import diagram

api_router = APIRouter()

api_router.include_router(diagram.router, prefix="/diagrams", tags=["diagrams"])
