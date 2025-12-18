"""
TARA AI Agent Service
=====================

FastAPI application for AI agent orchestration and MCP servers.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.common.config import settings
from app.common.utils import get_logger, setup_logging
from app.common.utils.exceptions import TaraException

from .api.v1.router import api_router

setup_logging()
logger = get_logger(__name__)

SERVICE_NAME = "tara-agent-service"
SERVICE_VERSION = "0.1.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    yield
    logger.info(f"Shutting down {SERVICE_NAME}")


app = FastAPI(
    title="TARA AI Agent Service",
    description="智能体服务 - 提供AI对话、自动化TARA分析和MCP服务",
    version=SERVICE_VERSION,
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(TaraException)
async def tara_exception_handler(request, exc: TaraException):
    return JSONResponse(status_code=exc.code, content=exc.to_dict())


app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": SERVICE_NAME, "version": SERVICE_VERSION}
