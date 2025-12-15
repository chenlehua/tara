"""E2E test configuration and fixtures."""
import os
import pytest
import httpx
from typing import Generator

# Service URLs
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost")
PROJECT_SERVICE_URL = f"{BASE_URL}:8001"
DOCUMENT_SERVICE_URL = f"{BASE_URL}:8002"
ASSET_SERVICE_URL = f"{BASE_URL}:8003"
THREAT_SERVICE_URL = f"{BASE_URL}:8004"
AGENT_SERVICE_URL = f"{BASE_URL}:8007"


@pytest.fixture(scope="session")
def http_client() -> Generator[httpx.Client, None, None]:
    """Create HTTP client for E2E tests."""
    client = httpx.Client(timeout=30.0)
    yield client
    client.close()


@pytest.fixture(scope="session")
def auth_headers() -> dict:
    """Get authentication headers."""
    # For testing, use a mock token
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def project_client(http_client, auth_headers):
    """Client for project service."""
    def make_request(method: str, path: str, **kwargs):
        url = f"{PROJECT_SERVICE_URL}/api/v1{path}"
        kwargs.setdefault("headers", {}).update(auth_headers)
        return getattr(http_client, method)(url, **kwargs)
    return make_request


@pytest.fixture
def document_client(http_client, auth_headers):
    """Client for document service."""
    def make_request(method: str, path: str, **kwargs):
        url = f"{DOCUMENT_SERVICE_URL}/api/v1{path}"
        kwargs.setdefault("headers", {}).update(auth_headers)
        return getattr(http_client, method)(url, **kwargs)
    return make_request


@pytest.fixture
def asset_client(http_client, auth_headers):
    """Client for asset service."""
    def make_request(method: str, path: str, **kwargs):
        url = f"{ASSET_SERVICE_URL}/api/v1{path}"
        kwargs.setdefault("headers", {}).update(auth_headers)
        return getattr(http_client, method)(url, **kwargs)
    return make_request


@pytest.fixture
def threat_client(http_client, auth_headers):
    """Client for threat service."""
    def make_request(method: str, path: str, **kwargs):
        url = f"{THREAT_SERVICE_URL}/api/v1{path}"
        kwargs.setdefault("headers", {}).update(auth_headers)
        return getattr(http_client, method)(url, **kwargs)
    return make_request


@pytest.fixture
def agent_client(http_client, auth_headers):
    """Client for agent service."""
    def make_request(method: str, path: str, **kwargs):
        url = f"{AGENT_SERVICE_URL}/api/v1{path}"
        kwargs.setdefault("headers", {}).update(auth_headers)
        return getattr(http_client, method)(url, **kwargs)
    return make_request


@pytest.fixture
def test_project_data():
    """Test project data."""
    return {
        "name": "E2E Test Project",
        "description": "Project for E2E testing",
        "vehicle_type": "BEV",
        "standard": "ISO/SAE 21434",
    }


@pytest.fixture
def test_asset_data():
    """Test asset data."""
    return {
        "name": "Test ECU",
        "asset_type": "ecu",
        "description": "ECU for testing",
        "security_attrs": {
            "confidentiality": "high",
            "integrity": "high",
            "availability": "medium",
        },
    }


@pytest.fixture
def test_threat_data():
    """Test threat data."""
    return {
        "threat_name": "CAN Bus Injection",
        "threat_type": "Tampering",
        "description": "Injection of malicious CAN messages",
    }
