"""
Chat Endpoints
==============

REST API endpoints for AI chat functionality.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse
from tara_shared.utils import success_response

from ....services.chat_service import ChatService

router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message model."""

    role: str = Field(..., description="角色: user, assistant, system")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """Chat request model."""

    messages: List[ChatMessage] = Field(..., description="消息历史")
    project_id: Optional[int] = Field(default=None, description="项目ID(上下文)")
    stream: bool = Field(default=False, description="是否流式响应")


def get_chat_service() -> ChatService:
    return ChatService()


@router.post("", response_model=dict)
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
):
    """Send a chat message and get response."""
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
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
):
    """Stream chat response using SSE."""

    async def event_generator():
        async for chunk in service.chat_stream(
            messages=[m.model_dump() for m in request.messages],
            project_id=request.project_id,
        ):
            yield {"event": "message", "data": chunk}
        yield {"event": "done", "data": ""}

    return EventSourceResponse(event_generator())
