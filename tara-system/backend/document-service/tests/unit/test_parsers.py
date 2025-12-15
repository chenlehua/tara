"""Unit tests for document parsers."""
import pytest
from unittest.mock import MagicMock, patch
import io

from app.parsers import get_parser
from app.parsers.pdf_parser import PDFParser
from app.parsers.word_parser import WordParser


class TestGetParser:
    """Tests for parser factory function."""

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
        """Test getting parser for unknown extension."""
        parser = get_parser("xyz")
        assert parser is None


class TestPDFParser:
    """Tests for PDF parser."""

    @pytest.fixture
    def parser(self):
        """Create PDF parser instance."""
        return PDFParser()

    def test_can_parse_pdf(self, parser):
        """Test PDF parser can parse PDF files."""
        assert parser.can_parse("pdf") is True
        assert parser.can_parse("docx") is False

    @patch('app.parsers.pdf_parser.PdfReader')
    def test_extract_text(self, mock_reader, parser):
        """Test text extraction from PDF."""
        # Mock PDF reader
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test content"
        mock_reader.return_value.pages = [mock_page]
        
        result = parser.extract_text(io.BytesIO(b"fake pdf"))
        
        assert "Test content" in result

    def test_parse_result_structure(self, parser):
        """Test parse result has correct structure."""
        # Mock the parsing
        with patch.object(parser, 'extract_text', return_value="Test"):
            with patch.object(parser, 'extract_structure', return_value={}):
                result = parser.parse(io.BytesIO(b"fake"))
        
                assert "content" in result
                assert "structure" in result


class TestWordParser:
    """Tests for Word parser."""

    @pytest.fixture
    def parser(self):
        """Create Word parser instance."""
        return WordParser()

    def test_can_parse_docx(self, parser):
        """Test Word parser can parse docx files."""
        assert parser.can_parse("docx") is True
        assert parser.can_parse("doc") is True
        assert parser.can_parse("pdf") is False

    @patch('app.parsers.word_parser.DocxDocument')
    def test_extract_text(self, mock_document, parser):
        """Test text extraction from Word document."""
        # Mock document
        mock_para = MagicMock()
        mock_para.text = "Test paragraph"
        mock_document.return_value.paragraphs = [mock_para]
        
        result = parser.extract_text(io.BytesIO(b"fake docx"))
        
        assert "Test paragraph" in result

    @patch('app.parsers.word_parser.DocxDocument')
    def test_extract_structure(self, mock_document, parser):
        """Test structure extraction from Word document."""
        # Mock document with headings
        mock_para1 = MagicMock()
        mock_para1.style.name = "Heading 1"
        mock_para1.text = "Chapter 1"
        
        mock_para2 = MagicMock()
        mock_para2.style.name = "Normal"
        mock_para2.text = "Content"
        
        mock_document.return_value.paragraphs = [mock_para1, mock_para2]
        
        result = parser.extract_structure(io.BytesIO(b"fake docx"))
        
        assert isinstance(result, dict)
