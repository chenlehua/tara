"""
API v1 Router
=============

Main router for Knowledge Base Service API v1.
"""

from fastapi import APIRouter

from .endpoints.knowledge import router as knowledge_router

api_router = APIRouter()

api_router.include_router(knowledge_router, prefix="/knowledge", tags=["Knowledge Base"])
