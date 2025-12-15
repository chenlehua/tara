"""Unit tests for report generators."""
import pytest
from unittest.mock import MagicMock, patch
from io import BytesIO

from app.generators.pdf_generator import PDFGenerator
from app.generators.word_generator import WordGenerator


class TestPDFGenerator:
    """Tests for PDF generator."""

    @pytest.fixture
    def generator(self):
        return PDFGenerator()

    def test_create_instance(self, generator):
        """Test creating PDF generator instance."""
        assert generator is not None

    @patch("app.generators.pdf_generator.SimpleDocTemplate")
    def test_generate_report(self, mock_template, generator):
        """Test generating PDF report."""
        mock_doc = MagicMock()
        mock_template.return_value = mock_doc
        
        data = {
            "project": {"name": "Test Project"},
            "sections": [
                {"title": "Summary", "content": "Test content"},
            ],
        }
        
        result = generator.generate(data)
        
        assert result is not None

    def test_format_table(self, generator):
        """Test table formatting."""
        table_data = [
            ["Header 1", "Header 2"],
            ["Row 1 Col 1", "Row 1 Col 2"],
            ["Row 2 Col 1", "Row 2 Col 2"],
        ]
        
        result = generator._format_table(table_data)
        
        assert result is not None


class TestWordGenerator:
    """Tests for Word generator."""

    @pytest.fixture
    def generator(self):
        return WordGenerator()

    def test_create_instance(self, generator):
        """Test creating Word generator instance."""
        assert generator is not None

    @patch("app.generators.word_generator.Document")
    def test_generate_report(self, mock_document, generator):
        """Test generating Word report."""
        mock_doc = MagicMock()
        mock_document.return_value = mock_doc
        
        data = {
            "project": {"name": "Test Project"},
            "sections": [
                {"title": "Summary", "content": "Test content"},
            ],
        }
        
        result = generator.generate(data)
        
        assert result is not None

    @patch("app.generators.word_generator.Document")
    def test_add_heading(self, mock_document, generator):
        """Test adding heading to document."""
        mock_doc = MagicMock()
        mock_document.return_value = mock_doc
        
        generator._add_heading(mock_doc, "Test Heading", level=1)
        
        mock_doc.add_heading.assert_called()

    @patch("app.generators.word_generator.Document")
    def test_add_paragraph(self, mock_document, generator):
        """Test adding paragraph to document."""
        mock_doc = MagicMock()
        mock_document.return_value = mock_doc
        
        generator._add_paragraph(mock_doc, "Test paragraph content")
        
        mock_doc.add_paragraph.assert_called()

    @patch("app.generators.word_generator.Document")
    def test_add_table(self, mock_document, generator):
        """Test adding table to document."""
        mock_doc = MagicMock()
        mock_table = MagicMock()
        mock_doc.add_table.return_value = mock_table
        mock_document.return_value = mock_doc
        
        table_data = [
            ["Header 1", "Header 2"],
            ["Value 1", "Value 2"],
        ]
        
        generator._add_table(mock_doc, table_data)
        
        mock_doc.add_table.assert_called()
