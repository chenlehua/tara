"""Pytest configuration for report service unit tests.

This conftest is specifically for unit tests and does not require
database connections or full app initialization.
"""

import pytest


@pytest.fixture
def sample_project():
    """Sample project data for testing."""
    return {
        "name": "Test Project",
        "platform_name": "Test Platform",
        "description": "Test description",
        "doc_number": "TEST-001",
        "version": "1.0",
    }


@pytest.fixture
def sample_assets():
    """Sample assets data for testing."""
    return [
        {
            "id": "A001",
            "name": "Test Asset",
            "category": "内部实体",
            "description": "Test asset description",
            "security_attrs": {
                "authenticity": True,
                "integrity": True,
            }
        }
    ]


@pytest.fixture
def sample_threats():
    """Sample threats data for testing."""
    return [
        {
            "asset_id_str": "A001",
            "asset_name": "Test Asset",
            "category_sub1": "Test",
            "category_sub2": "",
            "category_sub3": "Test Asset",
            "category": "内部实体",
            "security_attribute": '"Integrity | 完整性"',
            "stride_model": "T篡改",
            "threat_scenario": "Test threat scenario",
            "attack_path": "Test attack path",
            "wp29_mapping": "1.1",
            "attack_vector": "本地",
            "attack_complexity": "低",
            "privileges_required": "低",
            "user_interaction": "不需要",
            "safety_impact": "中等的",
            "financial_impact": "中等的",
            "operational_impact": "中等的",
            "privacy_impact": "可忽略不计的",
            "security_requirement": "Test security requirement",
        }
    ]
