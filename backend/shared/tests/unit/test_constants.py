"""Unit tests for constants and enums."""

import pytest
from tara_shared.constants import (CAL, AssetCategory, AssetType,
                                   DocumentParseStatus, FeasibilityRating,
                                   ProjectStatus, ReportStatus, RiskLevel,
                                   ThreatType, TreatmentDecision)
from tara_shared.constants.tara import (ATTACK_POTENTIAL_EXPERTISE,
                                        ATTACK_POTENTIAL_TO_FEASIBILITY,
                                        CAL_LEVELS, IMPACT_LEVELS, RISK_MATRIX,
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
        assert AssetType.ECU.value == "ECU"
        assert AssetType.SENSOR.value == "Sensor"
        assert AssetType.GATEWAY.value == "Gateway"
        assert AssetType.TBOX.value == "T-Box"

    def test_asset_category_values(self):
        """Test asset category enum values."""
        assert AssetCategory.HARDWARE.value == "Hardware"
        assert AssetCategory.SOFTWARE.value == "Software"
        assert AssetCategory.DATA.value == "Data"
        assert AssetCategory.NETWORK.value == "Network"

    def test_threat_type_stride(self):
        """Test STRIDE threat type enum values."""
        assert ThreatType.SPOOFING.value == "S"
        assert ThreatType.TAMPERING.value == "T"
        assert ThreatType.REPUDIATION.value == "R"
        assert ThreatType.INFO_DISCLOSURE.value == "I"
        assert ThreatType.DENIAL_OF_SERVICE.value == "D"
        assert ThreatType.ELEVATION.value == "E"

    def test_risk_level_values(self):
        """Test risk level enum values."""
        assert RiskLevel.NEGLIGIBLE.value == "negligible"
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"

    def test_treatment_decision_values(self):
        """Test treatment decision enum values."""
        assert TreatmentDecision.AVOID.value == "avoid"
        assert TreatmentDecision.REDUCE.value == "reduce"
        assert TreatmentDecision.SHARE.value == "share"
        assert TreatmentDecision.RETAIN.value == "retain"

    def test_feasibility_rating_values(self):
        """Test feasibility rating enum values."""
        assert FeasibilityRating.HIGH.value == "high"
        assert FeasibilityRating.MEDIUM.value == "medium"
        assert FeasibilityRating.LOW.value == "low"
        assert FeasibilityRating.VERY_LOW.value == "very_low"

    def test_report_status_values(self):
        """Test report status enum values."""
        assert ReportStatus.PENDING.value == 0
        assert ReportStatus.GENERATING.value == 1
        assert ReportStatus.COMPLETED.value == 2
        assert ReportStatus.FAILED.value == 3

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

    def test_stride_types_structure(self):
        """Test STRIDE types dictionary structure."""
        for key, value in STRIDE_TYPES.items():
            assert "name" in value
            assert "name_zh" in value
            assert "description" in value
            assert "violated_property" in value

    def test_impact_levels_structure(self):
        """Test impact levels dictionary structure."""
        assert 0 in IMPACT_LEVELS
        assert 1 in IMPACT_LEVELS
        assert 2 in IMPACT_LEVELS
        assert 3 in IMPACT_LEVELS
        assert 4 in IMPACT_LEVELS

        # Check structure
        for level, data in IMPACT_LEVELS.items():
            assert "level" in data
            assert "level_zh" in data
            assert "description" in data

    def test_risk_matrix_structure(self):
        """Test risk matrix structure."""
        # Risk matrix should be 5x5 (impact levels 0-4, likelihood levels 0-4)
        assert len(RISK_MATRIX) == 5
        for row in RISK_MATRIX:
            assert len(row) == 5

        # Check some expected values
        assert RISK_MATRIX[4][4] == "critical"  # Impact 4, Likelihood 4 = Critical
        assert RISK_MATRIX[0][0] == "negligible"  # Impact 0, Likelihood 0 = Negligible

    def test_attack_potential_expertise_values(self):
        """Test attack potential expertise scoring."""
        assert 0 in ATTACK_POTENTIAL_EXPERTISE
        assert 2 in ATTACK_POTENTIAL_EXPERTISE
        assert 4 in ATTACK_POTENTIAL_EXPERTISE
        assert 6 in ATTACK_POTENTIAL_EXPERTISE
        assert 8 in ATTACK_POTENTIAL_EXPERTISE

    def test_attack_potential_to_feasibility_mapping(self):
        """Test attack potential to feasibility rating mapping."""
        assert len(ATTACK_POTENTIAL_TO_FEASIBILITY) == 4

        # Check structure: each item should be (min, max, rating)
        for item in ATTACK_POTENTIAL_TO_FEASIBILITY:
            assert len(item) == 3
            assert isinstance(item[0], int)
            assert isinstance(item[1], int)
            assert isinstance(item[2], str)

        # Check ranges
        assert ATTACK_POTENTIAL_TO_FEASIBILITY[0] == (0, 9, "high")
        assert ATTACK_POTENTIAL_TO_FEASIBILITY[3] == (25, 100, "very_low")

    def test_cal_levels_structure(self):
        """Test CAL levels dictionary structure."""
        assert len(CAL_LEVELS) == 4

        for level in [1, 2, 3, 4]:
            assert level in CAL_LEVELS
            assert "level" in CAL_LEVELS[level]
            assert "description" in CAL_LEVELS[level]
            assert "description_en" in CAL_LEVELS[level]
            assert "requirements" in CAL_LEVELS[level]
