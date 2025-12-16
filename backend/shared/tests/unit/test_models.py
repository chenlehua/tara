"""Unit tests for SQLAlchemy models."""

import pytest
from tara_shared.models import (Asset, AttackPath, Document, Project, Report,
                                ThreatRisk)


class TestProjectModel:
    """Tests for Project model."""

    def test_create_project(self, db_session, sample_project_data):
        """Test creating a project."""
        project = Project(**sample_project_data)
        db_session.add(project)
        db_session.commit()

        assert project.id is not None
        assert project.name == sample_project_data["name"]
        assert project.vehicle_type == sample_project_data["vehicle_type"]
        assert project.status == 0  # Default draft status

    def test_project_timestamps(self, db_session, sample_project_data):
        """Test that timestamps are set automatically."""
        project = Project(**sample_project_data)
        db_session.add(project)
        db_session.commit()

        assert project.created_at is not None
        assert project.updated_at is not None

    def test_project_to_dict(self, db_session, sample_project_data):
        """Test project to_dict method."""
        project = Project(**sample_project_data)
        db_session.add(project)
        db_session.commit()

        data = project.to_dict()
        assert data["name"] == sample_project_data["name"]
        assert "id" in data


class TestAssetModel:
    """Tests for Asset model."""

    def test_create_asset(self, db_session, sample_project_data, sample_asset_data):
        """Test creating an asset."""
        # First create a project
        project = Project(**sample_project_data)
        db_session.add(project)
        db_session.commit()

        # Create asset
        asset = Asset(project_id=project.id, **sample_asset_data)
        db_session.add(asset)
        db_session.commit()

        assert asset.id is not None
        assert asset.project_id == project.id
        assert asset.name == sample_asset_data["name"]
        assert asset.asset_type == sample_asset_data["asset_type"]

    def test_asset_security_attrs(
        self, db_session, sample_project_data, sample_asset_data
    ):
        """Test asset security attributes JSON field."""
        project = Project(**sample_project_data)
        db_session.add(project)
        db_session.commit()

        asset = Asset(project_id=project.id, **sample_asset_data)
        db_session.add(asset)
        db_session.commit()

        assert asset.security_attrs["confidentiality"] == "medium"
        assert asset.security_attrs["integrity"] == "high"
        assert asset.security_attrs["availability"] == "high"


class TestThreatRiskModel:
    """Tests for ThreatRisk model."""

    def test_create_threat(self, db_session, sample_project_data, sample_asset_data):
        """Test creating a threat."""
        project = Project(**sample_project_data)
        db_session.add(project)
        db_session.commit()

        asset = Asset(project_id=project.id, **sample_asset_data)
        db_session.add(asset)
        db_session.commit()

        threat = ThreatRisk(
            project_id=project.id,
            asset_id=asset.id,
            threat_name="CAN Bus Injection",
            threat_type="T",
            threat_desc="Injection of malicious CAN messages",
        )
        db_session.add(threat)
        db_session.commit()

        assert threat.id is not None
        assert threat.threat_name == "CAN Bus Injection"
        assert threat.threat_type == "T"

    def test_threat_with_impact(
        self, db_session, sample_project_data, sample_asset_data
    ):
        """Test threat with impact levels."""
        project = Project(**sample_project_data)
        db_session.add(project)
        db_session.commit()

        asset = Asset(project_id=project.id, **sample_asset_data)
        db_session.add(asset)
        db_session.commit()

        threat = ThreatRisk(
            project_id=project.id,
            asset_id=asset.id,
            threat_name="Test Threat",
            threat_type="S",
            safety_impact=3,
            financial_impact=2,
            operational_impact=2,
            privacy_impact=1,
            impact_level=3,
            likelihood=3,
            risk_level="high",
        )
        db_session.add(threat)
        db_session.commit()

        assert threat.safety_impact == 3
        assert threat.impact_level == 3
        assert threat.likelihood == 3
        assert threat.risk_level == "high"


class TestAttackPathModel:
    """Tests for AttackPath model."""

    def test_create_attack_path(
        self, db_session, sample_project_data, sample_asset_data
    ):
        """Test creating an attack path."""
        project = Project(**sample_project_data)
        db_session.add(project)
        db_session.commit()

        asset = Asset(project_id=project.id, **sample_asset_data)
        db_session.add(asset)
        db_session.commit()

        threat = ThreatRisk(
            project_id=project.id,
            asset_id=asset.id,
            threat_name="Test Threat",
            threat_type="T",
        )
        db_session.add(threat)
        db_session.commit()

        attack_path = AttackPath(
            threat_risk_id=threat.id,
            name="Physical CAN Access",
            expertise=4,
            elapsed_time=7,
            equipment=6,
            knowledge=4,
            window_of_opportunity=7,
        )
        db_session.add(attack_path)
        db_session.commit()

        assert attack_path.id is not None
        assert attack_path.name == "Physical CAN Access"
        assert attack_path.expertise == 4

    def test_attack_path_potential_calculation(
        self, db_session, sample_project_data, sample_asset_data
    ):
        """Test attack potential fields."""
        project = Project(**sample_project_data)
        db_session.add(project)
        db_session.commit()

        asset = Asset(project_id=project.id, **sample_asset_data)
        db_session.add(asset)
        db_session.commit()

        threat = ThreatRisk(
            project_id=project.id,
            asset_id=asset.id,
            threat_name="Test Threat",
            threat_type="T",
        )
        db_session.add(threat)
        db_session.commit()

        # Total: 4+7+6+4+7 = 28
        attack_path = AttackPath(
            threat_risk_id=threat.id,
            name="Physical CAN Access",
            expertise=4,
            elapsed_time=7,
            equipment=6,
            knowledge=4,
            window_of_opportunity=7,
            attack_potential=28,
            feasibility_rating="very_low",
        )
        db_session.add(attack_path)
        db_session.commit()

        assert attack_path.attack_potential == 28
        assert attack_path.feasibility_rating == "very_low"
