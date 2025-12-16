"""API Router for agent service."""

from fastapi import APIRouter

from .endpoints import agent, chat

api_router = APIRouter()
api_router.include_router(agent.router, prefix="/agent", tags=["Agent"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
