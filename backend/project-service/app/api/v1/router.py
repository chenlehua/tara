"""
API Router
==========

Main API router for v1 endpoints.
"""

from fastapi import APIRouter

from .endpoints import project

api_router = APIRouter()

# Include project endpoints
api_router.include_router(
    project.router,
    prefix="/projects",
    tags=["Projects"],
)
