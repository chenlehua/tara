"""
Agent Endpoints
===============

REST API endpoints for AI agent operations.
"""

from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from pydantic import BaseModel, Field
from tara_shared.utils import success_response
from tara_shared.utils.exceptions import NotFoundException

from ....services.orchestrator import AgentOrchestrator

router = APIRouter()


class AnalyzeRequest(BaseModel):
    """Request for full TARA analysis."""

    project_id: int = Field(..., description="项目ID")
    document_ids: List[int] = Field(default_factory=list, description="文档ID列表")
    analysis_options: dict = Field(default_factory=dict, description="分析选项")


class TaskStatusResponse(BaseModel):
    """Task status response."""

    task_id: str
    status: str
    progress: int
    message: Optional[str] = None
    result: Optional[dict] = None


def get_orchestrator() -> AgentOrchestrator:
    return AgentOrchestrator()


@router.post("/analyze", response_model=dict)
async def start_analysis(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """Start a full TARA analysis."""
    task_id = orchestrator.create_task(
        task_type="full_analysis",
        project_id=request.project_id,
        document_ids=request.document_ids,
        options=request.analysis_options,
    )

    background_tasks.add_task(
        orchestrator.run_full_analysis,
        task_id=task_id,
        project_id=request.project_id,
        document_ids=request.document_ids,
        options=request.analysis_options,
    )

    return success_response(
        data={"task_id": task_id, "status": "started"},
        message="TARA分析任务已启动",
    )


@router.get("/tasks/{task_id}", response_model=dict)
async def get_task_status(
    task_id: str,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """Get task status."""
    status = orchestrator.get_task_status(task_id)
    if not status:
        raise NotFoundException("Task", task_id)

    return success_response(data=status)


@router.post("/tasks/{task_id}/cancel", response_model=dict)
async def cancel_task(
    task_id: str,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """Cancel a running task."""
    success = orchestrator.cancel_task(task_id)
    if not success:
        raise NotFoundException("Task", task_id)

    return success_response(message="任务已取消")


@router.get("/agents", response_model=dict)
async def list_agents(
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """List available agents."""
    agents = orchestrator.list_agents()
    return success_response(data=agents)
