"""Pytest configuration and fixtures for project service tests."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from tara_shared.database.mysql import Base, get_db
from tara_shared.models import Project

from app.main import app


# Use SQLite for testing
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
    """Create a fresh database session for each test."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with database override."""
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
def sample_project():
    """Sample project data."""
    return {
        "name": "Test TARA Project",
        "description": "A test project for TARA analysis",
        "vehicle_type": "BEV",
        "vehicle_model": "Model X",
        "standard": "ISO/SAE 21434",
        "owner": "Test User",
    }


@pytest.fixture
def created_project(client, sample_project):
    """Create a project and return it."""
    response = client.post("/api/v1/projects", json=sample_project)
    return response.json()["data"]
