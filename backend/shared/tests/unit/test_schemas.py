"""Unit tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError
from tara_shared.schemas import (AssetCreate, AssetUpdate, ProjectCreate,
                                 ProjectResponse, ProjectUpdate, ReportCreate,
                                 ThreatRiskCreate)
from tara_shared.schemas.asset import SecurityAttribute, SecurityAttributes


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
            "asset_type": "ECU",
        }
        schema = AssetCreate(**data)
        assert schema.name == "Test ECU"
        assert schema.asset_type == "ECU"

    def test_asset_create_with_security_attrs(self):
        """Test asset creation with security attributes."""
        data = {
            "project_id": 1,
            "name": "Gateway",
            "asset_type": "Gateway",
            "security_attrs": SecurityAttributes(
                confidentiality=SecurityAttribute(level="high"),
                integrity=SecurityAttribute(level="high"),
                availability=SecurityAttribute(level="medium"),
            ),
        }
        schema = AssetCreate(**data)
        assert schema.security_attrs.confidentiality.level == "high"

    def test_asset_update_partial(self):
        """Test partial asset update."""
        data = {"description": "Updated description"}
        schema = AssetUpdate(**data)
        assert schema.description == "Updated description"
        assert schema.name is None


class TestThreatRiskSchemas:
    """Tests for ThreatRisk schemas."""

    def test_threat_create_valid(self):
        """Test valid threat creation schema."""
        data = {
            "project_id": 1,
            "asset_id": 1,
            "threat_name": "CAN Injection",
            "threat_type": "T",  # STRIDE: Tampering
        }
        schema = ThreatRiskCreate(**data)
        assert schema.threat_name == "CAN Injection"
        assert schema.threat_type == "T"

    def test_threat_create_with_impact(self):
        """Test threat creation with impact values."""
        data = {
            "project_id": 1,
            "asset_id": 1,
            "threat_name": "Test Threat",
            "threat_type": "S",
            "safety_impact": 3,
            "financial_impact": 2,
            "operational_impact": 2,
            "privacy_impact": 1,
        }
        schema = ThreatRiskCreate(**data)
        assert schema.safety_impact == 3
        assert schema.financial_impact == 2

    def test_threat_create_missing_required(self):
        """Test threat creation without required fields."""
        data = {
            "project_id": 1,
            "threat_name": "Test Threat",
            # Missing asset_id
        }
        with pytest.raises(ValidationError):
            ThreatRiskCreate(**data)

    def test_threat_impact_validation(self):
        """Test impact value validation (0-4 range)."""
        data = {
            "project_id": 1,
            "asset_id": 1,
            "threat_name": "Test Threat",
            "safety_impact": 5,  # Invalid: > 4
        }
        with pytest.raises(ValidationError):
            ThreatRiskCreate(**data)
