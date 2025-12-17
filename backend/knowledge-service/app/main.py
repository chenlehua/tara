"""
Knowledge Base Service Main Entry
==================================

FastAPI application for knowledge base management.
Provides document upload, parsing, chunking, and hybrid search (vector + full-text).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tara_shared.config import settings
from tara_shared.utils import get_logger

from .api.v1.router import api_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("Knowledge Base Service starting...")
    
    # Initialize indices/collections
    from .services.knowledge_service import KnowledgeService
    service = KnowledgeService()
    service.init_storage()
    
    yield
    
    # Shutdown
    logger.info("Knowledge Base Service shutting down...")


app = FastAPI(
    title="TARA Knowledge Base Service",
    description="Knowledge base management with vector and full-text search",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "knowledge-service"}
