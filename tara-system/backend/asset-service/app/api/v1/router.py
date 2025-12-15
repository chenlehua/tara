"""API Router for asset service."""

from fastapi import APIRouter
from .endpoints import asset, damage_scenario

api_router = APIRouter()
api_router.include_router(asset.router, prefix="/assets", tags=["Assets"])
api_router.include_router(damage_scenario.router, prefix="/damage-scenarios", tags=["Damage Scenarios"])
