"""Unit tests for diagram service."""
import pytest
from unittest.mock import MagicMock, patch
from io import BytesIO

from app.services.diagram_service import DiagramService


class TestDiagramService:
    """Tests for DiagramService."""

    @pytest.fixture
    def service(self):
        return DiagramService()

    @patch("app.services.diagram_service.plt")
    def test_generate_risk_matrix(self, mock_plt, service, sample_risk_matrix_data):
        """Test generating risk matrix diagram."""
        mock_fig = MagicMock()
        mock_plt.figure.return_value = mock_fig
        mock_plt.subplots.return_value = (mock_fig, MagicMock())
        
        result = service.generate_risk_matrix(sample_risk_matrix_data)
        
        assert result is not None

    @patch("app.services.diagram_service.nx")
    @patch("app.services.diagram_service.plt")
    def test_generate_asset_graph(self, mock_plt, mock_nx, service, sample_asset_graph_data):
        """Test generating asset graph diagram."""
        mock_graph = MagicMock()
        mock_nx.DiGraph.return_value = mock_graph
        mock_fig = MagicMock()
        mock_plt.figure.return_value = mock_fig
        
        result = service.generate_asset_graph(sample_asset_graph_data)
        
        assert result is not None

    @patch("app.services.diagram_service.plt")
    def test_generate_attack_tree(self, mock_plt, service, sample_attack_tree_data):
        """Test generating attack tree diagram."""
        mock_fig = MagicMock()
        mock_plt.figure.return_value = mock_fig
        mock_plt.subplots.return_value = (mock_fig, MagicMock())
        
        result = service.generate_attack_tree(sample_attack_tree_data)
        
        assert result is not None

    @patch("app.services.diagram_service.plt")
    def test_generate_risk_distribution(self, mock_plt, service):
        """Test generating risk distribution chart."""
        mock_fig = MagicMock()
        mock_plt.figure.return_value = mock_fig
        
        data = {
            "critical": 2,
            "high": 5,
            "medium": 10,
            "low": 8,
            "negligible": 3,
        }
        
        result = service.generate_risk_distribution(data)
        
        assert result is not None

    @patch("app.services.diagram_service.plt")
    def test_generate_stride_chart(self, mock_plt, service):
        """Test generating STRIDE distribution chart."""
        mock_fig = MagicMock()
        mock_plt.figure.return_value = mock_fig
        
        data = {
            "Spoofing": 3,
            "Tampering": 5,
            "Repudiation": 1,
            "Information Disclosure": 4,
            "Denial of Service": 6,
            "Elevation of Privilege": 2,
        }
        
        result = service.generate_stride_chart(data)
        
        assert result is not None

    def test_get_color_for_risk_level(self, service):
        """Test getting color for risk level."""
        assert service._get_risk_color("critical") == "#ff0000"
        assert service._get_risk_color("high") == "#ff6600"
        assert service._get_risk_color("medium") == "#ffcc00"
        assert service._get_risk_color("low") == "#00cc00"
        assert service._get_risk_color("unknown") == "#999999"

    def test_calculate_position_in_matrix(self, service):
        """Test calculating position in risk matrix."""
        # Impact 5 (severe), Likelihood 5 (very high) -> top-right
        x, y = service._calculate_matrix_position(5, 5)
        assert x == 4  # 0-indexed
        assert y == 4

        # Impact 1 (negligible), Likelihood 1 (very low) -> bottom-left
        x, y = service._calculate_matrix_position(1, 1)
        assert x == 0
        assert y == 0
