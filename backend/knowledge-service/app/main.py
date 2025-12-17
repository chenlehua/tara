"""
Knowledge Base Service Main Entry
==================================

FastAPI application for knowledge base management.
Provides document upload, parsing, chunking, and hybrid search (vector + full-text).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.common.config import settings
from app.common.utils import get_logger
from app.common.utils.exceptions import TaraException

from .api.v1.router import api_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("Knowledge Base Service starting...")
    
    # Initialize indices/collections
    try:
        from .services.knowledge_service import KnowledgeService
        service = KnowledgeService()
        service.init_storage()
    except Exception as e:
        logger.warning(f"Failed to initialize storage (non-fatal): {e}")
    
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


@app.exception_handler(TaraException)
async def tara_exception_handler(request: Request, exc: TaraException):
    """Handle TARA-specific exceptions."""
    return JSONResponse(
        status_code=exc.code,
        content={
            "success": False,
            "code": exc.code,
            "message": exc.message,
            "data": None,
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "code": 500,
            "message": str(exc) if str(exc) else "服务器内部错误",
            "data": None,
        }
    )


# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "knowledge-service"}
