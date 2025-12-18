"""Test fixtures for Knowledge Service."""
import pytest


@pytest.fixture
def sample_document():
    """Sample document for testing."""
    return {
        "filename": "test.txt",
        "content": b"This is a test document for knowledge base.",
        "content_type": "text/plain",
    }
