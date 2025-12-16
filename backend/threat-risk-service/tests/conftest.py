"""Pytest configuration and fixtures for threat-risk service tests."""

import pytest
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from tara_shared.database.mysql import Base, get_db
from tara_shared.models import Asset, AttackPath, Project, ThreatRisk

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
def test_project(db_session):
    """Create a test project."""
    project = Project(
        name="Test Project",
        vehicle_type="BEV",
        standard="ISO/SAE 21434",
    )
    db_session.add(project)
    db_session.commit()
    return project


@pytest.fixture
def test_asset(db_session, test_project):
    """Create a test asset."""
    asset = Asset(
        project_id=test_project.id,
        name="Test ECU",
        asset_type="ecu",
    )
    db_session.add(asset)
    db_session.commit()
    return asset


@pytest.fixture
def sample_threat():
    """Sample threat data."""
    return {
        "threat_name": "CAN Bus Message Injection",
        "threat_type": "Tampering",
        "description": "Attacker injects malicious CAN messages",
    }


@pytest.fixture
def sample_attack_path():
    """Sample attack path data."""
    return {
        "name": "Physical OBD Access",
        "description": "Attack via physical OBD-II access",
        "steps": [
            {"order": 1, "description": "Access OBD-II port"},
            {"order": 2, "description": "Connect CAN interface"},
            {"order": 3, "description": "Inject messages"},
        ],
        "expertise": 3,
        "elapsed_time": 1,
        "equipment": 2,
        "knowledge": 2,
    }
