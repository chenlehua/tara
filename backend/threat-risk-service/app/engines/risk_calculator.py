"""
Risk Calculator
===============

Engine for risk calculation based on ISO 21434.
"""

from typing import Dict, Tuple

from app.common.constants.tara import (ATTACK_POTENTIAL_TO_FEASIBILITY,
                                        RISK_LEVEL_TO_CAL, RISK_MATRIX)


class RiskCalculator:
    """Calculator for risk values based on ISO 21434."""

    @staticmethod
    def calculate_impact(
        safety: int,
        financial: int,
        operational: int,
        privacy: int,
    ) -> int:
        """Calculate overall impact level (max of all categories)."""
        return max(safety, financial, operational, privacy)

    @staticmethod
    def calculate_attack_potential(
        expertise: int,
        elapsed_time: int,
        equipment: int,
        knowledge: int,
        window_of_opportunity: int = 0,
    ) -> Tuple[int, str]:
        """
        Calculate attack potential and feasibility rating.

        Returns:
            Tuple of (attack_potential, feasibility_rating)
        """
        attack_potential = (
            expertise + elapsed_time + equipment + knowledge + window_of_opportunity
        )

        # Determine feasibility rating
        feasibility = "very_low"
        for min_val, max_val, rating in ATTACK_POTENTIAL_TO_FEASIBILITY:
            if min_val <= attack_potential <= max_val:
                feasibility = rating
                break

        return attack_potential, feasibility

    @staticmethod
    def feasibility_to_likelihood(feasibility: str) -> int:
        """Convert feasibility rating to likelihood value."""
        mapping = {
            "high": 4,
            "medium": 3,
            "low": 2,
            "very_low": 1,
        }
        return mapping.get(feasibility, 0)

    @staticmethod
    def calculate_risk(impact: int, likelihood: int) -> Tuple[int, str]:
        """
        Calculate risk value and level.

        Returns:
            Tuple of (risk_value, risk_level)
        """
        risk_value = impact * likelihood

        # Get risk level from matrix
        if 0 <= impact <= 4 and 0 <= likelihood <= 4:
            risk_level = RISK_MATRIX[impact][likelihood]
        else:
            risk_level = "unknown"

        return risk_value, risk_level

    @staticmethod
    def determine_cal(risk_level: str) -> int:
        """Determine Cybersecurity Assurance Level from risk level."""
        return RISK_LEVEL_TO_CAL.get(risk_level, 1)

    @classmethod
    def full_risk_assessment(
        cls,
        safety_impact: int,
        financial_impact: int,
        operational_impact: int,
        privacy_impact: int,
        expertise: int,
        elapsed_time: int,
        equipment: int,
        knowledge: int,
        window_of_opportunity: int = 0,
    ) -> Dict[str, any]:
        """
        Perform full risk assessment.

        Returns comprehensive risk assessment result.
        """
        # Calculate impact
        impact = cls.calculate_impact(
            safety_impact, financial_impact, operational_impact, privacy_impact
        )

        # Calculate attack potential and feasibility
        attack_potential, feasibility = cls.calculate_attack_potential(
            expertise, elapsed_time, equipment, knowledge, window_of_opportunity
        )

        # Convert feasibility to likelihood
        likelihood = cls.feasibility_to_likelihood(feasibility)

        # Calculate risk
        risk_value, risk_level = cls.calculate_risk(impact, likelihood)

        # Determine CAL
        cal = cls.determine_cal(risk_level)

        return {
            "impact_level": impact,
            "impact_breakdown": {
                "safety": safety_impact,
                "financial": financial_impact,
                "operational": operational_impact,
                "privacy": privacy_impact,
            },
            "attack_potential": attack_potential,
            "feasibility_rating": feasibility,
            "likelihood": likelihood,
            "risk_value": risk_value,
            "risk_level": risk_level,
            "cal": cal,
        }
