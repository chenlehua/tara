"""PDF report generator."""

import io
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)
from tara_shared.utils import get_logger

logger = get_logger(__name__)


class PDFGenerator:
    """Generate PDF reports."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        """Setup custom styles."""
        self.styles.add(
            ParagraphStyle(
                name="ChineseNormal",
                fontName="Helvetica",
                fontSize=10,
                leading=14,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="ChineseTitle",
                fontName="Helvetica-Bold",
                fontSize=18,
                leading=22,
                spaceAfter=20,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="ChineseHeading",
                fontName="Helvetica-Bold",
                fontSize=14,
                leading=18,
                spaceBefore=12,
                spaceAfter=8,
            )
        )

    async def generate(
        self,
        data: dict,
        template: str = "iso21434",
        sections: list[str] = None,
    ) -> io.BytesIO:
        """Generate PDF report."""
        buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        story = []

        # Title
        story.append(Paragraph("TARA Analysis Report", self.styles["ChineseTitle"]))
        story.append(Spacer(1, 20))

        # Project info
        project = data.get("project", {})
        story.append(
            Paragraph(
                f"Project: {project.get('name', 'N/A')}", self.styles["ChineseNormal"]
            )
        )
        story.append(
            Paragraph(
                f"Vehicle Type: {project.get('vehicle_type', 'N/A')}",
                self.styles["ChineseNormal"],
            )
        )
        story.append(Spacer(1, 20))

        # Sections based on template
        if template == "iso21434":
            story.extend(await self._generate_iso21434_sections(data, sections))
        elif template == "simple":
            story.extend(await self._generate_simple_sections(data, sections))
        else:
            story.extend(await self._generate_default_sections(data))

        doc.build(story)
        buffer.seek(0)

        return buffer

    async def _generate_iso21434_sections(
        self,
        data: dict,
        sections: list[str] = None,
    ) -> list:
        """Generate ISO 21434 format sections."""
        story = []

        # Executive Summary
        story.append(Paragraph("1. Executive Summary", self.styles["ChineseHeading"]))
        story.append(
            Paragraph(
                "This report presents the results of the Threat Analysis and Risk Assessment (TARA) "
                "conducted in accordance with ISO/SAE 21434 requirements.",
                self.styles["ChineseNormal"],
            )
        )
        story.append(Spacer(1, 12))

        # Statistics
        stats = data.get("statistics", {})
        stats_data = [
            ["Metric", "Value"],
            ["Total Assets", str(stats.get("total_assets", 0))],
            ["Total Threats", str(stats.get("total_threats", 0))],
            ["Total Attack Paths", str(stats.get("total_attack_paths", 0))],
            ["Control Measures", str(stats.get("total_controls", 0))],
        ]

        table = Table(stats_data, colWidths=[8 * cm, 4 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 20))

        # Assets section
        story.append(PageBreak())
        story.append(
            Paragraph("2. Asset Identification", self.styles["ChineseHeading"])
        )
        story.append(
            Paragraph(
                "The following assets have been identified for the target vehicle system:",
                self.styles["ChineseNormal"],
            )
        )
        story.append(Spacer(1, 12))

        # Threats section
        story.append(PageBreak())
        story.append(Paragraph("3. Threat Analysis", self.styles["ChineseHeading"]))
        story.append(
            Paragraph(
                "Threats were identified using the STRIDE methodology:",
                self.styles["ChineseNormal"],
            )
        )
        story.append(Spacer(1, 12))

        # Risk Assessment section
        story.append(PageBreak())
        story.append(Paragraph("4. Risk Assessment", self.styles["ChineseHeading"]))
        story.append(
            Paragraph(
                "Risk levels were determined based on impact and attack feasibility:",
                self.styles["ChineseNormal"],
            )
        )

        return story

    async def _generate_simple_sections(
        self,
        data: dict,
        sections: list[str] = None,
    ) -> list:
        """Generate simple format sections."""
        story = []

        story.append(Paragraph("Summary", self.styles["ChineseHeading"]))
        story.append(
            Paragraph(
                "Brief overview of the threat analysis findings.",
                self.styles["ChineseNormal"],
            )
        )

        return story

    async def _generate_default_sections(self, data: dict) -> list:
        """Generate default sections."""
        return await self._generate_iso21434_sections(data)
