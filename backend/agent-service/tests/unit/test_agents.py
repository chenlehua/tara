"""Unit tests for AI agents."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.agents import AssetAgent, DocumentAgent, ReportAgent, ThreatRiskAgent


class TestDocumentAgent:
    """Tests for DocumentAgent."""

    @pytest.fixture
    def agent(self):
        return DocumentAgent()

    @pytest.mark.asyncio
    async def test_extract_structure(self, agent):
        """Test structure extraction."""
        with patch.object(agent, "call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = '{"sections": [{"title": "Introduction"}]}'

            result = await agent.extract_structure("Document content here")

            assert result is not None
            mock_llm.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_documents_placeholder(self, agent):
        """Test document processing (placeholder)."""
        result = await agent.process_documents(project_id=1)

        # Placeholder returns empty list
        assert isinstance(result, list)


class TestAssetAgent:
    """Tests for AssetAgent."""

    @pytest.fixture
    def agent(self):
        return AssetAgent()

    @pytest.mark.asyncio
    async def test_discover_assets(self, agent):
        """Test asset discovery."""
        with patch.object(agent, "call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = '{"assets": [{"name": "ECU", "type": "ecu"}]}'

            result = await agent.discover_assets(
                project_id=1, content="Technical document content"
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_classify_asset(self, agent):
        """Test asset classification."""
        with patch.object(agent, "call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = '{"type": "ecu", "category": "powertrain"}'

            result = await agent.classify_asset("Engine Control Unit")

            assert "type" in result


class TestThreatRiskAgent:
    """Tests for ThreatRiskAgent."""

    @pytest.fixture
    def agent(self):
        return ThreatRiskAgent()

    @pytest.mark.asyncio
    async def test_analyze_threats(self, agent):
        """Test threat analysis."""
        with patch.object(agent, "call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = """
            {
                "threats": [
                    {
                        "threat_name": "CAN Injection",
                        "threat_type": "Tampering"
                    }
                ]
            }
            """

            asset = {"id": 1, "name": "Gateway", "type": "gateway"}
            result = await agent.analyze_threats(project_id=1, asset=asset)

            assert result is not None

    @pytest.mark.asyncio
    async def test_assess_attack_feasibility(self, agent):
        """Test attack feasibility assessment."""
        with patch.object(agent, "call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = """
            {
                "attack_potential": 12,
                "feasibility_rating": "medium"
            }
            """

            attack_path = {
                "name": "OBD Access",
                "steps": [{"order": 1, "description": "Connect to OBD"}],
            }
            result = await agent.assess_attack_feasibility(attack_path)

            assert "feasibility_rating" in result


class TestReportAgent:
    """Tests for ReportAgent."""

    @pytest.fixture
    def agent(self):
        return ReportAgent()

    @pytest.mark.asyncio
    async def test_write_section(self, agent):
        """Test section writing."""
        with patch.object(agent, "call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "This section describes the executive summary..."

            result = await agent.write_section(
                section_name="Executive Summary", data={"project": "Test Project"}
            )

            assert isinstance(result, str)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_generate_report_placeholder(self, agent):
        """Test report generation (placeholder)."""
        result = await agent.generate_report(project_id=1, template="iso21434")

        assert isinstance(result, dict)
