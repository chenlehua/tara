"""API Router for threat-risk service."""

from fastapi import APIRouter

from .endpoints import attack_path, risk, threat

api_router = APIRouter()
api_router.include_router(threat.router, prefix="/threats", tags=["Threats"])
api_router.include_router(
    attack_path.router, prefix="/attack-paths", tags=["Attack Paths"]
)
api_router.include_router(risk.router, prefix="/risks", tags=["Risks"])
