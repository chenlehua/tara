"""Unit tests for SQLAlchemy models."""

import pytest
from tara_shared.models import (Asset, AttackPath, DamageScenario, Document,
                                Project, Report, ThreatRisk)


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

    def test_create_threat(self, db_session, sample_project_data, sample_threat_data):
        """Test creating a threat."""
        project = Project(**sample_project_data)
        db_session.add(project)
        db_session.commit()

        threat = ThreatRisk(project_id=project.id, **sample_threat_data)
        db_session.add(threat)
        db_session.commit()

        assert threat.id is not None
        assert threat.threat_name == sample_threat_data["threat_name"]
        assert threat.threat_type == sample_threat_data["threat_type"]

    def test_calculate_risk(self, db_session, sample_project_data):
        """Test risk calculation method."""
        project = Project(**sample_project_data)
        db_session.add(project)
        db_session.commit()

        threat = ThreatRisk(
            project_id=project.id,
            threat_name="Test Threat",
            threat_type="Spoofing",
            impact_level="major",
            likelihood="high",
        )
        threat.calculate_risk()
        db_session.add(threat)
        db_session.commit()

        assert threat.risk_level is not None
        assert threat.risk_value is not None


class TestAttackPathModel:
    """Tests for AttackPath model."""

    def test_calculate_attack_potential(self, db_session, sample_project_data):
        """Test attack potential calculation."""
        project = Project(**sample_project_data)
        db_session.add(project)
        db_session.commit()

        threat = ThreatRisk(
            project_id=project.id,
            threat_name="Test Threat",
            threat_type="Tampering",
        )
        db_session.add(threat)
        db_session.commit()

        attack_path = AttackPath(
            threat_risk_id=threat.id,
            name="Physical CAN Access",
            expertise=2,  # Proficient
            elapsed_time=1,  # Less than 1 week
            equipment=1,  # Standard
            knowledge=2,  # Restricted
        )
        attack_path.calculate_attack_potential()
        db_session.add(attack_path)
        db_session.commit()

        assert attack_path.attack_potential is not None
        assert attack_path.feasibility_rating is not None
