"""
TARA Document Parsing Service
=============================

FastAPI application for document parsing and OCR.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from tara_shared.config import settings
from tara_shared.database import init_db
from tara_shared.utils import setup_logging, get_logger
from tara_shared.utils.exceptions import TaraException

from .api.v1.router import api_router

setup_logging()
logger = get_logger(__name__)

SERVICE_NAME = "tara-document-service"
SERVICE_VERSION = "0.1.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    init_db()
    yield
    logger.info(f"Shutting down {SERVICE_NAME}")


app = FastAPI(
    title="TARA Document Parsing Service",
    description="文档解析服务 - 提供文档上传、OCR识别和结构化提取功能",
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
