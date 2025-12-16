"""
Document Parsers
================

Parsers for different document formats.
"""

from .base_parser import BaseParser
from .pdf_parser import PDFParser
from .word_parser import WordParser

PARSER_MAP = {
    "pdf": PDFParser,
    "doc": WordParser,
    "docx": WordParser,
}


def get_parser(file_extension: str) -> BaseParser:
    """Get appropriate parser for file extension."""
    parser_class = PARSER_MAP.get(file_extension.lower(), BaseParser)
    return parser_class()


__all__ = ["get_parser", "BaseParser", "PDFParser", "WordParser"]
