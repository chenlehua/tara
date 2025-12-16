"""Diagram Service main application."""

from contextlib import asynccontextmanager

from app.api.v1.router import api_router
from app.config import settings
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from tara_shared.utils import get_logger
from tara_shared.utils.exceptions import TaraException

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting Diagram Service...")
    yield
    logger.info("Shutting down Diagram Service...")


app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(TaraException)
async def tara_exception_handler(request: Request, exc: TaraException):
    """Handle TARA exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "code": exc.error_code,
            "message": exc.message,
            "data": None,
        },
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.SERVICE_NAME}


app.include_router(api_router, prefix=settings.API_PREFIX)
