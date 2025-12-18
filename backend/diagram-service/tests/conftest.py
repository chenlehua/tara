"""Pytest configuration for diagram service tests."""

from unittest.mock import MagicMock

import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="function")
def client():
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_asset_graph_data():
    """Sample data for asset graph."""
    return {
        "nodes": [
            {"id": "1", "label": "Gateway ECU", "type": "gateway"},
            {"id": "2", "label": "Engine ECU", "type": "ecu"},
            {"id": "3", "label": "CAN Bus", "type": "bus"},
        ],
        "edges": [
            {"source": "1", "target": "3", "type": "connects_to"},
            {"source": "2", "target": "3", "type": "connects_to"},
        ],
    }


@pytest.fixture
def sample_attack_tree_data():
    """Sample data for attack tree."""
    return {
        "goal": "Compromise Engine Control",
        "children": [
            {
                "node": "Remote Attack",
                "type": "AND",
                "children": [
                    {"node": "Exploit Telematics", "type": "LEAF"},
                    {"node": "Access CAN Bus", "type": "LEAF"},
                ],
            },
            {
                "node": "Physical Attack",
                "type": "OR",
                "children": [
                    {"node": "OBD Access", "type": "LEAF"},
                    {"node": "Direct ECU Access", "type": "LEAF"},
                ],
            },
        ],
    }


@pytest.fixture
def sample_risk_matrix_data():
    """Sample data for risk matrix."""
    return {
        "threats": [
            {"id": 1, "impact": 4, "likelihood": 3, "name": "CAN Injection"},
            {"id": 2, "impact": 3, "likelihood": 4, "name": "DoS Attack"},
            {"id": 3, "impact": 2, "likelihood": 2, "name": "Data Leak"},
        ],
    }
