"""Unit tests for agent orchestrator."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.orchestrator import AgentOrchestrator, TaskManager


class TestTaskManager:
    """Tests for TaskManager."""

    @pytest.fixture
    def manager(self):
        return TaskManager()

    def test_create_task(self, manager):
        """Test task creation."""
        task_id = manager.create_task("test_task")

        assert task_id is not None
        assert len(task_id) == 36  # UUID format

    def test_get_task(self, manager):
        """Test getting task."""
        task_id = manager.create_task("test_task")
        task = manager.get_task(task_id)

        assert task is not None
        assert task["id"] == task_id
        assert task["status"] == "pending"

    def test_update_task(self, manager):
        """Test updating task."""
        task_id = manager.create_task("test_task")
        manager.update_task(task_id, status="running", progress=50)

        task = manager.get_task(task_id)
        assert task["status"] == "running"
        assert task["progress"] == 50

    def test_get_nonexistent_task(self, manager):
        """Test getting non-existent task."""
        task = manager.get_task("nonexistent-id")
        assert task is None


class TestAgentOrchestrator:
    """Tests for AgentOrchestrator."""

    @pytest.fixture
    def orchestrator(self):
        return AgentOrchestrator()

    def test_create_task(self, orchestrator):
        """Test creating analysis task."""
        task = orchestrator.create_task(project_id=1)

        assert task["id"] is not None
        assert task["status"] == "pending"

    def test_get_task_status(self, orchestrator):
        """Test getting task status."""
        task = orchestrator.create_task(project_id=1)
        status = orchestrator.get_task_status(task["id"])

        assert status is not None
        assert status["id"] == task["id"]

    def test_cancel_task(self, orchestrator):
        """Test canceling task."""
        task = orchestrator.create_task(project_id=1)
        result = orchestrator.cancel_task(task["id"])

        assert result is True
        status = orchestrator.get_task_status(task["id"])
        assert status["status"] == "cancelled"

    def test_list_agents(self, orchestrator):
        """Test listing available agents."""
        agents = orchestrator.list_agents()

        assert len(agents) == 4
        agent_names = [a["name"] for a in agents]
        assert "DocumentAgent" in agent_names
        assert "AssetAgent" in agent_names
        assert "ThreatRiskAgent" in agent_names
        assert "ReportAgent" in agent_names

    @pytest.mark.asyncio
    async def test_run_full_analysis_updates_progress(self, orchestrator):
        """Test that full analysis updates progress."""
        task = orchestrator.create_task(project_id=1)

        # Mock the agents
        with patch.multiple(
            orchestrator,
            document_agent=MagicMock(process_documents=AsyncMock(return_value=[])),
            asset_agent=MagicMock(discover_assets=AsyncMock(return_value=[])),
            threat_agent=MagicMock(analyze_threats=AsyncMock(return_value=[])),
            report_agent=MagicMock(generate_report=AsyncMock(return_value={})),
        ):
            await orchestrator.run_full_analysis(task["id"], project_id=1)

            status = orchestrator.get_task_status(task["id"])
            assert status["status"] == "completed"
            assert status["progress"] == 100
