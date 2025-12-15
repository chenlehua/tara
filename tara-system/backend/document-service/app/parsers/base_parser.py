"""
Base Parser
===========

Base class for document parsers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseParser(ABC):
    """Base document parser."""

    async def parse(
        self,
        content: bytes,
        filename: str,
        enable_ocr: bool = True,
        enable_structure: bool = True,
    ) -> Dict[str, Any]:
        """
        Parse document content.
        
        Returns:
            Dictionary with parsed content:
            - title: Document title
            - content: Text content
            - structure: Document structure
            - metadata: Document metadata
            - page_count: Number of pages
            - ocr_result: OCR results if applicable
        """
        return {
            "title": filename,
            "content": "",
            "structure": {},
            "metadata": {},
            "page_count": 0,
            "ocr_result": {},
        }
