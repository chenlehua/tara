"""Pytest configuration for agent service tests."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock

from app.main import app


@pytest.fixture(scope="function")
def client():
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_llm_response():
    """Mock LLM response."""
    return {
        "id": "test-123",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "This is a test response from the LLM.",
                },
                "finish_reason": "stop",
            }
        ],
    }


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for LLM calls."""
    with patch("httpx.AsyncClient") as mock:
        client_instance = AsyncMock()
        mock.return_value.__aenter__.return_value = client_instance
        yield client_instance


@pytest.fixture
def sample_chat_request():
    """Sample chat request data."""
    return {
        "message": "What are the main threats to CAN bus?",
        "project_id": 1,
        "stream": False,
    }


@pytest.fixture
def sample_analyze_request():
    """Sample analysis request data."""
    return {
        "project_id": 1,
    }
