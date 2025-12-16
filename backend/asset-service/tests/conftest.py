"""Pytest configuration for asset service tests."""

from unittest.mock import MagicMock, patch

import pytest
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from tara_shared.database.mysql import Base, get_db
from tara_shared.models import Asset, Project

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(engine):
    """Create database session."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_project(db_session):
    """Create a test project."""
    project = Project(
        name="Test Asset Project",
        vehicle_type="BEV",
        standard="ISO/SAE 21434",
    )
    db_session.add(project)
    db_session.commit()
    return project


@pytest.fixture
def sample_asset():
    """Sample asset data."""
    return {
        "name": "Gateway ECU",
        "asset_type": "gateway",
        "category": "connectivity",
        "description": "Central vehicle gateway",
        "security_attrs": {
            "confidentiality": "high",
            "integrity": "high",
            "availability": "high",
        },
        "interfaces": [
            {"name": "CAN1", "type": "CAN", "direction": "bidirectional"},
            {"name": "ETH0", "type": "Ethernet", "direction": "bidirectional"},
        ],
    }


@pytest.fixture
def mock_neo4j():
    """Mock Neo4j graph service."""
    with patch("app.services.asset_service.GraphService") as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        mock_instance.create_node.return_value = "node-123"
        yield mock_instance
