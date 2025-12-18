"""Pytest configuration for report service tests.

This conftest uses lazy imports to avoid loading the full application
when running unit tests that don't need the app or database.
"""

from unittest.mock import MagicMock, patch

import pytest

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    from sqlalchemy import create_engine
    from sqlalchemy.pool import StaticPool
    from app.common.database.mysql import Base
    
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
    from sqlalchemy.orm import sessionmaker
    
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client."""
    from app.main import app
    from app.common.database.mysql import get_db
    from fastapi.testclient import TestClient

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
def sample_report_request():
    """Sample report generation request."""
    return {
        "project_id": 1,
        "template": "iso21434",
        "format": "pdf",
        "include_sections": [
            "executive_summary",
            "assets",
            "threats",
            "risks",
            "recommendations",
        ],
    }
