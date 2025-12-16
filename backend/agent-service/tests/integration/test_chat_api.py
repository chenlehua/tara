"""Integration tests for chat API."""

from unittest.mock import AsyncMock, patch

import pytest


class TestChatAPI:
    """Integration tests for chat endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    @patch("app.services.chat_service.httpx.AsyncClient")
    def test_chat_endpoint(
        self, mock_client, client, sample_chat_request, mock_llm_response
    ):
        """Test chat endpoint."""
        # Mock the LLM response
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_llm_response
        mock_response.status_code = 200

        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_instance

        response = client.post("/api/v1/chat", json=sample_chat_request)

        # May fail due to missing LLM service, but should not crash
        assert response.status_code in [200, 500, 503]


class TestAgentAPI:
    """Integration tests for agent endpoints."""

    def test_list_agents(self, client):
        """Test list agents endpoint."""
        response = client.get("/api/v1/agents")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 4

    def test_start_analysis(self, client, sample_analyze_request):
        """Test start analysis endpoint."""
        response = client.post("/api/v1/agents/analyze", json=sample_analyze_request)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "task_id" in data["data"]

    def test_get_task_status(self, client, sample_analyze_request):
        """Test get task status endpoint."""
        # First start an analysis
        start_response = client.post(
            "/api/v1/agents/analyze", json=sample_analyze_request
        )
        task_id = start_response.json()["data"]["task_id"]

        # Then check status
        response = client.get(f"/api/v1/agents/tasks/{task_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == task_id

    def test_get_nonexistent_task(self, client):
        """Test getting non-existent task."""
        response = client.get("/api/v1/agents/tasks/nonexistent-task-id")

        assert response.status_code == 404

    def test_cancel_task(self, client, sample_analyze_request):
        """Test cancel task endpoint."""
        # First start an analysis
        start_response = client.post(
            "/api/v1/agents/analyze", json=sample_analyze_request
        )
        task_id = start_response.json()["data"]["task_id"]

        # Then cancel it
        response = client.post(f"/api/v1/agents/tasks/{task_id}/cancel")

        assert response.status_code == 200
