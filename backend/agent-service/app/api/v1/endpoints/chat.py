"""
Chat Endpoints
==============

REST API endpoints for AI chat functionality.
"""

from typing import Any, Dict, List, Optional

from app.services.chat_service import ChatService
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse
from tara_shared.utils import get_logger, success_response

router = APIRouter()
logger = get_logger(__name__)


class ChatMessage(BaseModel):
    """Chat message model."""

    role: str = Field(..., description="角色: user, assistant, system")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """Chat request model (legacy format with messages array)."""

    messages: List[ChatMessage] = Field(..., description="消息历史")
    project_id: Optional[int] = Field(default=None, description="项目ID(上下文)")
    stream: bool = Field(default=False, description="是否流式响应")


class SimpleChatRequest(BaseModel):
    """Simple chat request model (single message format from frontend)."""

    message: str = Field(..., description="用户消息")
    project_id: Optional[str] = Field(default=None, description="项目ID(上下文)")
    context: Optional[Dict[str, Any]] = Field(default=None, description="额外上下文")


class ChatHistoryItem(BaseModel):
    """Chat history item."""

    id: str
    role: str
    content: str
    timestamp: str


def get_chat_service() -> ChatService:
    return ChatService()


@router.post("")
async def chat(
    request: SimpleChatRequest,
    service: ChatService = Depends(get_chat_service),
):
    """
    Send a chat message and get response.

    This endpoint accepts the frontend's simple message format:
    - message: The user's message
    - project_id: Optional project context
    - context: Optional additional context
    """
    try:
        # Convert project_id to int if provided
        project_id = None
        if request.project_id:
            try:
                project_id = int(request.project_id)
            except (ValueError, TypeError):
                pass

        # Build messages array for the service
        messages = [{"role": "user", "content": request.message}]

        # Call the chat service
        response = await service.chat(
            messages=messages,
            project_id=project_id,
            context=request.context,
        )

        return success_response(
            data={
                "role": "assistant",
                "content": response,
            }
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return success_response(
            data={
                "role": "assistant",
                "content": f"抱歉，处理您的请求时出现了错误。请稍后重试。\n\n错误信息: {str(e)}",
            }
        )


@router.post("/messages")
async def chat_with_messages(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
):
    """
    Send chat with full message history.

    This endpoint accepts the legacy format with messages array.
    """
    if request.stream:
        # Return streaming response
        async def event_generator():
            async for chunk in service.chat_stream(
                messages=[m.model_dump() for m in request.messages],
                project_id=request.project_id,
            ):
                yield {"event": "message", "data": chunk}
            yield {"event": "done", "data": ""}

        return EventSourceResponse(event_generator())
    else:
        # Return complete response
        response = await service.chat(
            messages=[m.model_dump() for m in request.messages],
            project_id=request.project_id,
        )

        return success_response(
            data={
                "role": "assistant",
                "content": response,
            }
        )


@router.post("/stream")
async def chat_stream(
    request: SimpleChatRequest,
    service: ChatService = Depends(get_chat_service),
):
    """Stream chat response using SSE."""

    # Convert project_id to int if provided
    project_id = None
    if request.project_id:
        try:
            project_id = int(request.project_id)
        except (ValueError, TypeError):
            pass

    # Build messages array for the service
    messages = [{"role": "user", "content": request.message}]

    async def event_generator():
        try:
            async for chunk in service.chat_stream(
                messages=messages,
                project_id=project_id,
            ):
                yield {"event": "message", "data": chunk}
            yield {"event": "done", "data": ""}
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield {"event": "error", "data": str(e)}

    return EventSourceResponse(event_generator())


@router.get("/history")
async def get_chat_history(
    project_id: Optional[str] = Query(default=None, description="项目ID"),
    service: ChatService = Depends(get_chat_service),
):
    """Get chat history for a project."""
    try:
        # Convert project_id to int if provided
        pid = None
        if project_id:
            try:
                pid = int(project_id)
            except (ValueError, TypeError):
                pass

        history = await service.get_history(project_id=pid)
        return success_response(data=history)
    except Exception as e:
        logger.error(f"Get history error: {e}")
        return success_response(data=[])


@router.delete("/history")
async def clear_chat_history(
    project_id: Optional[str] = Query(default=None, description="项目ID"),
    service: ChatService = Depends(get_chat_service),
):
    """Clear chat history for a project."""
    try:
        # Convert project_id to int if provided
        pid = None
        if project_id:
            try:
                pid = int(project_id)
            except (ValueError, TypeError):
                pass

        await service.clear_history(project_id=pid)
        return success_response(message="聊天记录已清除")
    except Exception as e:
        logger.error(f"Clear history error: {e}")
        return success_response(message="清除失败")
