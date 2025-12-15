"""API Router for document service."""

from fastapi import APIRouter
from .endpoints import document

api_router = APIRouter()
api_router.include_router(document.router, prefix="/documents", tags=["Documents"])
