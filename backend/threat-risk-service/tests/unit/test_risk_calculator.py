"""Unit tests for risk calculator."""

import pytest
from app.engines.risk_calculator import RiskCalculator


class TestRiskCalculator:
    """Tests for RiskCalculator."""

    def test_calculate_impact_severe(self):
        """Test impact calculation for severe scenario."""
        damage_scenario = {
            "safety_impact": "severe",
            "financial_impact": "major",
            "operational_impact": "moderate",
            "privacy_impact": "minor",
        }

        impact = RiskCalculator.calculate_impact(damage_scenario)

        # Highest impact should be the result
        assert impact == "severe"

    def test_calculate_impact_moderate(self):
        """Test impact calculation for moderate scenario."""
        damage_scenario = {
            "safety_impact": "moderate",
            "financial_impact": "minor",
            "operational_impact": "moderate",
            "privacy_impact": "minor",
        }

        impact = RiskCalculator.calculate_impact(damage_scenario)

        assert impact == "moderate"

    def test_calculate_attack_potential_low(self):
        """Test attack potential for easy attack."""
        factors = {
            "expertise": 0,  # Layman
            "elapsed_time": 0,  # Less than 1 day
            "equipment": 0,  # Standard
            "knowledge": 0,  # Public
        }

        potential, rating = RiskCalculator.calculate_attack_potential(factors)

        assert potential == 0
        assert rating == "very_high"  # Very feasible

    def test_calculate_attack_potential_high(self):
        """Test attack potential for difficult attack."""
        factors = {
            "expertise": 8,  # Multiple experts
            "elapsed_time": 5,  # More than 6 months
            "equipment": 6,  # Bespoke
            "knowledge": 7,  # Critical
        }

        potential, rating = RiskCalculator.calculate_attack_potential(factors)

        assert potential >= 20
        assert rating in ["low", "very_low"]

    def test_feasibility_to_likelihood(self):
        """Test feasibility to likelihood conversion."""
        assert RiskCalculator.feasibility_to_likelihood("very_high") == "very_high"
        assert RiskCalculator.feasibility_to_likelihood("high") == "high"
        assert RiskCalculator.feasibility_to_likelihood("medium") == "medium"
        assert RiskCalculator.feasibility_to_likelihood("low") == "low"
        assert RiskCalculator.feasibility_to_likelihood("very_low") == "low"

    def test_calculate_risk_critical(self):
        """Test risk calculation for critical scenario."""
        impact = "severe"
        likelihood = "very_high"

        risk_level, risk_value = RiskCalculator.calculate_risk(impact, likelihood)

        assert risk_value == 5
        assert risk_level == "critical"

    def test_calculate_risk_low(self):
        """Test risk calculation for low scenario."""
        impact = "minor"
        likelihood = "low"

        risk_level, risk_value = RiskCalculator.calculate_risk(impact, likelihood)

        assert risk_value <= 2
        assert risk_level in ["negligible", "low"]

    def test_calculate_risk_medium(self):
        """Test risk calculation for medium scenario."""
        impact = "moderate"
        likelihood = "medium"

        risk_level, risk_value = RiskCalculator.calculate_risk(impact, likelihood)

        assert risk_value == 3
        assert risk_level == "medium"

    def test_determine_cal_critical(self):
        """Test CAL determination for critical risk."""
        cal = RiskCalculator.determine_cal(5)  # Critical risk

        assert cal == 4  # CAL 4

    def test_determine_cal_low(self):
        """Test CAL determination for low risk."""
        cal = RiskCalculator.determine_cal(2)  # Low risk

        assert cal == 1  # CAL 1

    def test_risk_matrix_symmetry(self):
        """Test that risk matrix covers all combinations."""
        impacts = ["negligible", "minor", "moderate", "major", "severe"]
        likelihoods = ["low", "medium", "high", "very_high"]

        for impact in impacts:
            for likelihood in likelihoods:
                risk_level, risk_value = RiskCalculator.calculate_risk(
                    impact, likelihood
                )

                assert risk_level is not None
                assert 1 <= risk_value <= 5
