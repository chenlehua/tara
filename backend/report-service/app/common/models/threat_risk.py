"""
Threat Risk Model
=================

SQLAlchemy models for ThreatRisk, AttackPath, and ControlMeasure entities.
"""

from sqlalchemy import JSON, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel


class ThreatRisk(BaseModel):
    """Threat and risk model combining threat identification and risk assessment."""

    __tablename__ = "threat_risks"

    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    asset_id = Column(
        Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    damage_scenario_id = Column(
        Integer, ForeignKey("damage_scenarios.id", ondelete="SET NULL"), nullable=True
    )

    # Threat identification
    threat_name = Column(String(200), nullable=False, index=True)
    threat_type = Column(String(20), nullable=True)  # STRIDE: S, T, R, I, D, E
    threat_desc = Column(Text, nullable=True)
    attack_vector = Column(Text, nullable=True)
    attack_surface = Column(String(100), nullable=True)
    threat_source = Column(String(100), nullable=True)  # External, Internal
    threat_agent = Column(String(100), nullable=True)  # Hacker, Insider, etc.

    # Impact assessment (0-4)
    safety_impact = Column(Integer, default=0)
    financial_impact = Column(Integer, default=0)
    operational_impact = Column(Integer, default=0)
    privacy_impact = Column(Integer, default=0)
    impact_level = Column(Integer, nullable=True)  # Max of all impacts

    # Likelihood and Risk
    likelihood = Column(Integer, nullable=True)  # 0-4
    risk_value = Column(Integer, nullable=True)  # Impact × Likelihood
    risk_level = Column(
        String(20), nullable=True
    )  # negligible, low, medium, high, critical

    # Treatment
    treatment = Column(String(50), nullable=True)  # avoid, reduce, share, accept
    treatment_desc = Column(Text, nullable=True)
    residual_risk = Column(Integer, nullable=True)

    # CAL (Cybersecurity Assurance Level)
    cal = Column(Integer, nullable=True)  # 1-4

    # References
    cwe_ids = Column(JSON, default=list)  # CWE references
    capec_ids = Column(JSON, default=list)  # CAPEC references

    # Source
    source = Column(String(50), default="manual")  # manual, ai_generated

    # Relationships
    project = relationship("Project", back_populates="threat_risks")
    asset = relationship("Asset", back_populates="threat_risks")
    damage_scenario = relationship("DamageScenario", back_populates="threat_risks")
    attack_paths = relationship(
        "AttackPath", back_populates="threat_risk", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ThreatRisk(id={self.id}, name='{self.threat_name}', type='{self.threat_type}')>"


class AttackPath(BaseModel):
    """Attack path model for threat scenarios."""

    __tablename__ = "attack_paths"

    threat_risk_id = Column(
        Integer,
        ForeignKey("threat_risks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    steps = Column(JSON, default=list)  # List of attack steps

    # Attack potential parameters (ISO 21434)
    expertise = Column(Integer, default=0)  # 0-8
    elapsed_time = Column(Integer, default=0)  # 0-19
    equipment = Column(Integer, default=0)  # 0-10
    knowledge = Column(Integer, default=0)  # 0-7
    window_of_opportunity = Column(Integer, default=0)  # 0-10

    # Calculated values
    attack_potential = Column(Integer, nullable=True)  # Sum of parameters
    feasibility_rating = Column(
        String(20), nullable=True
    )  # low, medium, high, very_high

    # Additional info
    prerequisites = Column(JSON, default=list)
    attack_techniques = Column(JSON, default=list)  # MITRE ATT&CK references

    # Relationship
    threat_risk = relationship("ThreatRisk", back_populates="attack_paths")
    control_measures = relationship(
        "ControlMeasure", back_populates="attack_path", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<AttackPath(id={self.id}, name='{self.name}')>"


class ControlMeasure(BaseModel):
    """Control measure model for risk mitigation."""

    __tablename__ = "control_measures"

    # Can be linked via attack_path or directly to threat_risk
    attack_path_id = Column(
        Integer,
        ForeignKey("attack_paths.id", ondelete="CASCADE"),
        nullable=True,  # Made optional to support direct threat linkage
        index=True,
    )
    threat_risk_id = Column(
        Integer,
        ForeignKey("threat_risks.id", ondelete="CASCADE"),
        nullable=True,  # Direct linkage to threat (for one-click generation)
        index=True,
    )

    name = Column(String(200), nullable=False)
    control_type = Column(
        String(50), nullable=True
    )  # preventive, detective, corrective
    category = Column(String(50), nullable=True)  # technical, organizational
    description = Column(Text, nullable=True)
    implementation = Column(Text, nullable=True)
    effectiveness = Column(String(20), nullable=True)  # low, medium, high
    cost_estimate = Column(String(50), nullable=True)
    
    # Status as string for flexibility
    status = Column(String(50), nullable=True)  # planned, in_progress, implemented

    # Implementation status (legacy int field)
    implementation_status = Column(
        Integer, default=0
    )  # 0: planned, 1: in_progress, 2: implemented
    verification_status = Column(Integer, default=0)  # 0: not_verified, 1: verified

    # Reference
    iso21434_ref = Column(String(50), nullable=True)  # ISO 21434 reference clause

    # Relationships
    attack_path = relationship("AttackPath", back_populates="control_measures")
    threat_risk = relationship("ThreatRisk", backref="control_measures")

    def __repr__(self) -> str:
        return f"<ControlMeasure(id={self.id}, name='{self.name}')>"
