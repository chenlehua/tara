"""
Asset Model
===========

SQLAlchemy models for Asset and DamageScenario entities.
"""

from sqlalchemy import JSON, BigInteger, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel


class Asset(BaseModel):
    """Asset model for system components."""

    __tablename__ = "assets"

    project_id = Column(
        BigInteger,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_id = Column(
        BigInteger, ForeignKey("assets.id", ondelete="SET NULL"), nullable=True
    )

    name = Column(String(200), nullable=False, index=True)
    asset_type = Column(String(50), nullable=False)  # ECU, Gateway, Sensor, etc.
    category = Column(String(50), nullable=True)  # Component category
    description = Column(Text, nullable=True)
    version = Column(String(50), nullable=True)
    vendor = Column(String(100), nullable=True)
    model_number = Column(String(100), nullable=True)
    location = Column(String(200), nullable=True)  # Physical location
    zone = Column(String(50), nullable=True)  # Security zone
    trust_boundary = Column(String(50), nullable=True)
    criticality = Column(String(20), nullable=True)  # low, medium, high, critical

    # Security attributes (CIA)
    security_attrs = Column(JSON, default=dict)

    # Interfaces
    interfaces = Column(JSON, default=list)  # List of interface definitions

    # Data types handled
    data_types = Column(JSON, default=list)

    # Flags
    is_external = Column(Integer, default=0)  # 0: internal, 1: external
    status = Column(Integer, default=1)  # 0: inactive, 1: active
    source = Column(String(50), default="manual")  # manual, ai_discovered

    # Relationships
    project = relationship("Project", back_populates="assets")
    children = relationship("Asset", backref="parent", remote_side="Asset.id")
    damage_scenarios = relationship(
        "DamageScenario", back_populates="asset", cascade="all, delete-orphan"
    )
    threat_risks = relationship("ThreatRisk", back_populates="asset")

    def __repr__(self) -> str:
        return f"<Asset(id={self.id}, name='{self.name}', type='{self.asset_type}')>"


class DamageScenario(BaseModel):
    """Damage scenario model for impact assessment."""

    __tablename__ = "damage_scenarios"

    asset_id = Column(
        BigInteger, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )

    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Impact ratings (0-4: negligible, low, medium, high, critical)
    safety_impact = Column(Integer, default=0)
    financial_impact = Column(Integer, default=0)
    operational_impact = Column(Integer, default=0)
    privacy_impact = Column(Integer, default=0)
    impact_level = Column(Integer, nullable=True)  # Maximum of all impacts

    impact_justification = Column(Text, nullable=True)
    stakeholders = Column(JSON, default=list)  # Affected stakeholders

    # Relationship
    asset = relationship("Asset", back_populates="damage_scenarios")
    threat_risks = relationship("ThreatRisk", back_populates="damage_scenario")

    def __repr__(self) -> str:
        return f"<DamageScenario(id={self.id}, name='{self.name}')>"
