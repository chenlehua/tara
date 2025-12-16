"""Unit tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError
from tara_shared.schemas import (AssetCreate, AssetUpdate, ProjectCreate,
                                 ProjectResponse, ProjectUpdate, ReportCreate,
                                 ThreatRiskCreate)


class TestProjectSchemas:
    """Tests for Project schemas."""

    def test_project_create_valid(self):
        """Test valid project creation schema."""
        data = {
            "name": "Test Project",
            "description": "A test project",
            "vehicle_type": "BEV",
        }
        schema = ProjectCreate(**data)
        assert schema.name == "Test Project"
        assert schema.vehicle_type == "BEV"

    def test_project_create_missing_name(self):
        """Test project creation without required name field."""
        data = {"description": "A test project"}
        with pytest.raises(ValidationError):
            ProjectCreate(**data)

    def test_project_update_partial(self):
        """Test partial project update."""
        data = {"description": "Updated description"}
        schema = ProjectUpdate(**data)
        assert schema.description == "Updated description"
        assert schema.name is None


class TestAssetSchemas:
    """Tests for Asset schemas."""

    def test_asset_create_valid(self):
        """Test valid asset creation schema."""
        data = {
            "project_id": 1,
            "name": "Test ECU",
            "asset_type": "ecu",
        }
        schema = AssetCreate(**data)
        assert schema.name == "Test ECU"
        assert schema.asset_type == "ecu"

    def test_asset_create_with_security_attrs(self):
        """Test asset creation with security attributes."""
        data = {
            "project_id": 1,
            "name": "Gateway",
            "asset_type": "gateway",
            "security_attrs": {
                "confidentiality": "high",
                "integrity": "high",
                "availability": "medium",
            },
        }
        schema = AssetCreate(**data)
        assert schema.security_attrs.confidentiality == "high"


class TestThreatRiskSchemas:
    """Tests for ThreatRisk schemas."""

    def test_threat_create_valid(self):
        """Test valid threat creation schema."""
        data = {
            "project_id": 1,
            "threat_name": "CAN Injection",
            "threat_type": "Tampering",
        }
        schema = ThreatRiskCreate(**data)
        assert schema.threat_name == "CAN Injection"
        assert schema.threat_type == "Tampering"

    def test_threat_create_invalid_type(self):
        """Test threat creation with invalid STRIDE type."""
        data = {
            "project_id": 1,
            "threat_name": "Test Threat",
            "threat_type": "InvalidType",
        }
        # Should raise validation error for invalid threat type
        with pytest.raises(ValidationError):
            ThreatRiskCreate(**data)
