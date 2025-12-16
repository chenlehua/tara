"""Unit tests for constants and enums."""

import pytest
from tara_shared.constants import (CAL, AssetType, DocumentParseStatus,
                                   FeasibilityRating, ProjectStatus,
                                   ReportStatus, RiskLevel, ThreatType,
                                   TreatmentDecision)
from tara_shared.constants.tara import (ATTACK_POTENTIAL_EXPERTISE,
                                        ATTACK_POTENTIAL_TO_FEASIBILITY,
                                        IMPACT_LEVELS, RISK_MATRIX,
                                        STRIDE_TYPES)


class TestEnums:
    """Tests for enum values."""

    def test_project_status_values(self):
        """Test project status enum values."""
        assert ProjectStatus.DRAFT.value == 0
        assert ProjectStatus.IN_PROGRESS.value == 1
        assert ProjectStatus.COMPLETED.value == 2
        assert ProjectStatus.ARCHIVED.value == 3

    def test_document_parse_status_values(self):
        """Test document parse status enum values."""
        assert DocumentParseStatus.PENDING.value == 0
        assert DocumentParseStatus.PARSING.value == 1
        assert DocumentParseStatus.COMPLETED.value == 2
        assert DocumentParseStatus.FAILED.value == 3

    def test_asset_type_values(self):
        """Test asset type enum values."""
        assert AssetType.ECU.value == "ecu"
        assert AssetType.BUS.value == "bus"
        assert AssetType.SENSOR.value == "sensor"
        assert AssetType.GATEWAY.value == "gateway"

    def test_threat_type_stride(self):
        """Test STRIDE threat type enum values."""
        assert ThreatType.SPOOFING.value == "Spoofing"
        assert ThreatType.TAMPERING.value == "Tampering"
        assert ThreatType.REPUDIATION.value == "Repudiation"
        assert ThreatType.INFORMATION_DISCLOSURE.value == "Information Disclosure"
        assert ThreatType.DENIAL_OF_SERVICE.value == "Denial of Service"
        assert ThreatType.ELEVATION_OF_PRIVILEGE.value == "Elevation of Privilege"

    def test_risk_level_values(self):
        """Test risk level enum values."""
        assert RiskLevel.NEGLIGIBLE.value == 1
        assert RiskLevel.LOW.value == 2
        assert RiskLevel.MEDIUM.value == 3
        assert RiskLevel.HIGH.value == 4
        assert RiskLevel.CRITICAL.value == 5

    def test_cal_levels(self):
        """Test CAL (Cybersecurity Assurance Level) enum values."""
        assert CAL.CAL1.value == 1
        assert CAL.CAL2.value == 2
        assert CAL.CAL3.value == 3
        assert CAL.CAL4.value == 4


class TestTaraConstants:
    """Tests for TARA-specific constants."""

    def test_stride_types_complete(self):
        """Test STRIDE types dictionary is complete."""
        assert len(STRIDE_TYPES) == 6
        assert "S" in STRIDE_TYPES
        assert "T" in STRIDE_TYPES
        assert "R" in STRIDE_TYPES
        assert "I" in STRIDE_TYPES
        assert "D" in STRIDE_TYPES
        assert "E" in STRIDE_TYPES

    def test_impact_levels_structure(self):
        """Test impact levels dictionary structure."""
        assert "negligible" in IMPACT_LEVELS
        assert "minor" in IMPACT_LEVELS
        assert "moderate" in IMPACT_LEVELS
        assert "major" in IMPACT_LEVELS
        assert "severe" in IMPACT_LEVELS

    def test_risk_matrix_structure(self):
        """Test risk matrix structure."""
        # Risk matrix should cover all impact-likelihood combinations
        assert ("severe", "very_high") in RISK_MATRIX
        assert ("negligible", "low") in RISK_MATRIX

        # Check some expected values
        assert RISK_MATRIX[("severe", "very_high")] == 5  # Critical
        assert RISK_MATRIX[("negligible", "low")] == 1  # Negligible

    def test_attack_potential_expertise_values(self):
        """Test attack potential expertise scoring."""
        assert ATTACK_POTENTIAL_EXPERTISE["layman"] == 0
        assert ATTACK_POTENTIAL_EXPERTISE["proficient"] == 3
        assert ATTACK_POTENTIAL_EXPERTISE["expert"] == 6
        assert ATTACK_POTENTIAL_EXPERTISE["multiple_experts"] == 8

    def test_attack_potential_to_feasibility_mapping(self):
        """Test attack potential to feasibility rating mapping."""
        # Low attack potential = High feasibility
        assert ATTACK_POTENTIAL_TO_FEASIBILITY[0] == "very_high"
        assert ATTACK_POTENTIAL_TO_FEASIBILITY[5] == "very_high"

        # High attack potential = Low feasibility
        assert ATTACK_POTENTIAL_TO_FEASIBILITY[20] == "low"
        assert ATTACK_POTENTIAL_TO_FEASIBILITY[25] == "very_low"
