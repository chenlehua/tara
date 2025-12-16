"""Pytest configuration and fixtures for shared module tests."""

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
# Import models to ensure they are registered
from tara_shared.models import (Asset, AttackPath, ControlMeasure,
                                DamageScenario, Document, Project, Report,
                                ThreatRisk)
# Import the Base from models - this is the one used by all models
from tara_shared.models.base import Base

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
    # Create all tables from the models' Base metadata
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


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "name": "Test TARA Project",
        "description": "A test project for TARA analysis",
        "vehicle_type": "BEV",
        "vehicle_model": "Test Model X",
        "standard": "ISO/SAE 21434",
        "owner": "Test User",
    }


@pytest.fixture
def sample_asset_data():
    """Sample asset data for testing."""
    return {
        "name": "Test ECU",
        "asset_type": "ECU",
        "category": "powertrain",
        "description": "Engine Control Unit for testing",
        "security_attrs": {
            "confidentiality": "medium",
            "integrity": "high",
            "availability": "high",
        },
    }


@pytest.fixture
def sample_threat_data():
    """Sample threat data for testing."""
    return {
        "threat_name": "CAN Bus Injection",
        "threat_type": "T",  # STRIDE: Tampering
        "threat_desc": "Injection of malicious CAN messages",
        "safety_impact": 3,
        "likelihood": 3,
    }
