"""Unit tests for document parsers."""

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from app.parsers import get_parser
from app.parsers.pdf_parser import PDFParser
from app.parsers.word_parser import WordParser


class TestGetParser:
    """Tests for parser factory."""

    def test_get_pdf_parser(self):
        """Test getting PDF parser."""
        parser = get_parser("pdf")
        assert isinstance(parser, PDFParser)

    def test_get_word_parser_docx(self):
        """Test getting Word parser for docx."""
        parser = get_parser("docx")
        assert isinstance(parser, WordParser)

    def test_get_word_parser_doc(self):
        """Test getting Word parser for doc."""
        parser = get_parser("doc")
        assert isinstance(parser, WordParser)

    def test_get_unknown_parser(self):
        """Test getting parser for unknown format."""
        parser = get_parser("xyz")
        assert parser is None


class TestPDFParser:
    """Tests for PDF parser."""

    @pytest.fixture
    def parser(self):
        return PDFParser()

    def test_can_parse_pdf(self, parser):
        """Test PDF format detection."""
        assert parser.can_parse("pdf") is True
        assert parser.can_parse("docx") is False

    @patch("app.parsers.pdf_parser.PdfReader")
    def test_parse_simple_pdf(self, mock_reader, parser):
        """Test parsing simple PDF."""
        # Mock PDF reader
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test content from PDF"
        mock_reader.return_value.pages = [mock_page]

        content = BytesIO(b"%PDF-1.4 test")
        result = parser.parse(content)

        assert "Test content from PDF" in result["text"]

    @patch("app.parsers.pdf_parser.PdfReader")
    def test_parse_multi_page_pdf(self, mock_reader, parser):
        """Test parsing multi-page PDF."""
        mock_pages = []
        for i in range(3):
            page = MagicMock()
            page.extract_text.return_value = f"Page {i+1} content"
            mock_pages.append(page)

        mock_reader.return_value.pages = mock_pages

        content = BytesIO(b"%PDF-1.4 test")
        result = parser.parse(content)

        assert result["page_count"] == 3


class TestWordParser:
    """Tests for Word parser."""

    @pytest.fixture
    def parser(self):
        return WordParser()

    def test_can_parse_docx(self, parser):
        """Test docx format detection."""
        assert parser.can_parse("docx") is True
        assert parser.can_parse("doc") is True
        assert parser.can_parse("pdf") is False

    @patch("app.parsers.word_parser.Document")
    def test_parse_simple_docx(self, mock_document, parser):
        """Test parsing simple Word document."""
        # Mock document
        mock_para = MagicMock()
        mock_para.text = "Test paragraph content"
        mock_para.style.name = "Normal"
        mock_document.return_value.paragraphs = [mock_para]
        mock_document.return_value.tables = []

        content = BytesIO(b"PK test")
        result = parser.parse(content)

        assert "Test paragraph content" in result["text"]
