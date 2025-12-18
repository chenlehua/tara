"""Unit tests for STRIDE analysis engine."""

import pytest
from app.engines.stride_engine import STRIDEEngine


class TestSTRIDEEngine:
    """Tests for STRIDEEngine."""

    @pytest.fixture
    def engine(self):
        """Create STRIDE engine instance."""
        return STRIDEEngine()

    def test_analyze_ecu_asset(self, engine):
        """Test STRIDE analysis for ECU asset."""
        asset = {
            "id": 1,
            "name": "Engine ECU",
            "asset_type": "ecu",
            "description": "Engine control unit",
        }

        threats = engine.analyze_asset(asset)

        assert len(threats) > 0
        threat_types = [t["threat_type"] for t in threats]

        # ECUs should have multiple threat types
        assert "Tampering" in threat_types
        assert "Spoofing" in threat_types

    def test_analyze_gateway_asset(self, engine):
        """Test STRIDE analysis for gateway asset."""
        asset = {
            "id": 2,
            "name": "Central Gateway",
            "asset_type": "gateway",
            "description": "Vehicle central gateway",
        }

        threats = engine.analyze_asset(asset)

        assert len(threats) > 0
        # Gateways are critical and should have multiple threats
        threat_types = [t["threat_type"] for t in threats]
        assert len(set(threat_types)) >= 3

    def test_analyze_external_interface(self, engine):
        """Test STRIDE analysis for external interface."""
        asset = {
            "id": 3,
            "name": "OBD-II Port",
            "asset_type": "external_interface",
            "description": "Diagnostic interface",
        }

        threats = engine.analyze_asset(asset)

        assert len(threats) > 0
        # External interfaces should have spoofing and elevation threats
        threat_types = [t["threat_type"] for t in threats]
        assert "Spoofing" in threat_types

    def test_threat_output_format(self, engine):
        """Test that threats have correct output format."""
        asset = {
            "id": 1,
            "name": "Test Asset",
            "asset_type": "ecu",
        }

        threats = engine.analyze_asset(asset)

        for threat in threats:
            assert "threat_name" in threat
            assert "threat_type" in threat
            assert "asset_id" in threat
            assert threat["asset_id"] == 1

    def test_stride_coverage(self, engine):
        """Test all STRIDE categories can be generated."""
        # Use different asset types to cover all STRIDE
        asset_types = ["ecu", "gateway", "bus", "external_interface", "telematics"]
        all_threat_types = set()

        for asset_type in asset_types:
            asset = {
                "id": 1,
                "name": f"Test {asset_type}",
                "asset_type": asset_type,
            }
            threats = engine.analyze_asset(asset)
            for t in threats:
                all_threat_types.add(t["threat_type"])

        # Should cover most STRIDE categories
        expected_types = {
            "Spoofing",
            "Tampering",
            "Information Disclosure",
            "Denial of Service",
        }
        assert expected_types.issubset(all_threat_types)
