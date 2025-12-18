"""
PDF Parser
==========

Parser for PDF documents.
"""

import io
from typing import Any, Dict

import httpx
from pypdf import PdfReader
from app.common.config import settings
from app.common.utils import get_logger

from .base_parser import BaseParser

logger = get_logger(__name__)


class PDFParser(BaseParser):
    """PDF document parser with OCR support."""

    async def parse(
        self,
        content: bytes,
        filename: str,
        enable_ocr: bool = True,
        enable_structure: bool = True,
    ) -> Dict[str, Any]:
        """Parse PDF document."""
        result = {
            "title": filename,
            "content": "",
            "structure": {},
            "metadata": {},
            "page_count": 0,
            "ocr_result": {},
        }

        try:
            # Read PDF
            pdf_file = io.BytesIO(content)
            reader = PdfReader(pdf_file)

            result["page_count"] = len(reader.pages)
            result["metadata"] = {
                key: str(value)
                for key, value in (reader.metadata or {}).items()
                if value
            }

            # Extract text from each page
            pages_text = []
            pages_with_no_text = []

            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages_text.append(text)
                else:
                    pages_with_no_text.append(i)

            result["content"] = "\n\n".join(pages_text)

            # If some pages have no text and OCR is enabled, use OCR
            if enable_ocr and pages_with_no_text:
                ocr_result = await self._perform_ocr(content, pages_with_no_text)
                result["ocr_result"] = ocr_result

                # Merge OCR text with extracted text
                if ocr_result.get("text"):
                    result["content"] += "\n\n" + ocr_result["text"]

            # Extract structure if enabled
            if enable_structure:
                result["structure"] = self._extract_structure(reader)

        except Exception as e:
            logger.error(f"Failed to parse PDF: {e}")
            raise

        return result

    async def _perform_ocr(
        self,
        content: bytes,
        pages: list,
    ) -> Dict[str, Any]:
        """Perform OCR on specified pages."""
        try:
            async with httpx.AsyncClient() as client:
                # Call OCRFlux service
                response = await client.post(
                    f"{settings.ocrflux_url}/ocr",
                    files={"file": ("document.pdf", content, "application/pdf")},
                    data={"pages": ",".join(str(p) for p in pages)},
                    timeout=120.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return {}

    def _extract_structure(self, reader: PdfReader) -> Dict[str, Any]:
        """Extract document structure (outlines, etc.)."""
        structure = {
            "sections": [],
            "tables": [],
        }

        # Extract outline if available
        try:
            if reader.outline:
                structure["sections"] = self._parse_outline(reader.outline)
        except Exception:
            pass

        return structure

    def _parse_outline(self, outline, level: int = 0) -> list:
        """Parse PDF outline to sections."""
        sections = []
        for item in outline:
            if isinstance(item, list):
                sections.extend(self._parse_outline(item, level + 1))
            else:
                sections.append(
                    {
                        "title": item.title if hasattr(item, "title") else str(item),
                        "level": level,
                    }
                )
        return sections
