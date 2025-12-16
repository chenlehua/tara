"""API Router for agent service."""

from fastapi import APIRouter

from .endpoints import agent, chat

api_router = APIRouter()
api_router.include_router(agent.router, prefix="/agent", tags=["Agent"])
# Chat endpoints are mounted under /agent/chat to match frontend expectations
api_router.include_router(chat.router, prefix="/agent/chat", tags=["Chat"])
# Also mount at /chat for backward compatibility
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
