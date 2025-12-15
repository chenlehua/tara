"""
TARA Project Management Service
===============================

FastAPI application for project management.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from tara_shared.config import settings
from tara_shared.database import init_db
from tara_shared.utils import setup_logging, get_logger
from tara_shared.utils.exceptions import TaraException

from .config import config
from .api.v1.router import api_router

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info(f"Starting {config.service_name} v{config.service_version}")
    init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {config.service_name}")


# Create FastAPI application
app = FastAPI(
    title="TARA Project Management Service",
    description="项目管理服务 - 提供TARA项目的创建、配置和管理功能",
    version=config.service_version,
    openapi_url=f"{config.api_prefix}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(TaraException)
async def tara_exception_handler(request, exc: TaraException):
    """Handle TARA exceptions."""
    return JSONResponse(
        status_code=exc.code,
        content=exc.to_dict(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "code": 500,
            "message": "Internal server error",
            "data": None,
        },
    )


# Include API router
app.include_router(api_router, prefix=config.api_prefix)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": config.service_name,
        "version": config.service_version,
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "service": config.service_name,
        "version": config.service_version,
        "docs": "/docs",
    }
