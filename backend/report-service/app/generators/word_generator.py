"""Word document report generator."""

import io
from typing import Any

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Inches, Pt
from tara_shared.utils import get_logger

logger = get_logger(__name__)


class WordGenerator:
    """Generate Word document reports."""

    async def generate(
        self,
        data: dict,
        template: str = "iso21434",
        sections: list[str] = None,
    ) -> io.BytesIO:
        """Generate Word document."""
        doc = Document()

        # Set document properties
        core_properties = doc.core_properties
        core_properties.author = "TARA System"
        core_properties.title = (
            f"TARA Report - {data.get('project', {}).get('name', 'Unknown')}"
        )

        # Title
        title = doc.add_heading("TARA Analysis Report", 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Project info
        project = data.get("project", {})
        doc.add_paragraph()
        info_para = doc.add_paragraph()
        info_para.add_run("Project: ").bold = True
        info_para.add_run(project.get("name", "N/A"))

        info_para = doc.add_paragraph()
        info_para.add_run("Vehicle Type: ").bold = True
        info_para.add_run(project.get("vehicle_type", "N/A"))

        info_para = doc.add_paragraph()
        info_para.add_run("Standard: ").bold = True
        info_para.add_run("ISO/SAE 21434")

        doc.add_paragraph()

        # Table of contents placeholder
        doc.add_heading("Table of Contents", 1)
        doc.add_paragraph("(Table of contents will be generated in final document)")
        doc.add_page_break()

        # Generate sections
        if template == "iso21434":
            await self._generate_iso21434_sections(doc, data, sections)
        else:
            await self._generate_default_sections(doc, data)

        # Save to buffer
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        return buffer

    async def _generate_iso21434_sections(
        self,
        doc: Document,
        data: dict,
        sections: list[str] = None,
    ):
        """Generate ISO 21434 format sections."""
        # 1. Executive Summary
        doc.add_heading("1. Executive Summary", 1)
        doc.add_paragraph(
            "This document presents the results of the Threat Analysis and Risk Assessment "
            "(TARA) conducted in accordance with ISO/SAE 21434 cybersecurity engineering "
            "requirements for road vehicles."
        )

        # Statistics table
        stats = data.get("statistics", {})
        doc.add_paragraph()
        doc.add_paragraph("Summary Statistics:", style="Intense Quote")

        table = doc.add_table(rows=5, cols=2)
        table.style = "Table Grid"
        table.alignment = WD_TABLE_ALIGNMENT.CENTER

        rows = [
            ("Total Assets", str(stats.get("total_assets", 0))),
            ("Total Threats", str(stats.get("total_threats", 0))),
            ("Attack Paths", str(stats.get("total_attack_paths", 0))),
            ("Control Measures", str(stats.get("total_controls", 0))),
            ("High Risk Items", str(stats.get("high_risk_count", 0))),
        ]

        for i, (label, value) in enumerate(rows):
            row = table.rows[i]
            row.cells[0].text = label
            row.cells[1].text = value

        doc.add_page_break()

        # 2. Scope Definition
        doc.add_heading("2. Scope Definition", 1)
        doc.add_paragraph(
            "The scope of this TARA covers the cybersecurity analysis of the vehicle "
            "electrical/electronic architecture and connected systems."
        )

        doc.add_heading("2.1 Item Definition", 2)
        doc.add_paragraph("Description of the item under assessment...")

        doc.add_heading("2.2 System Boundaries", 2)
        doc.add_paragraph("Definition of system boundaries and interfaces...")

        doc.add_page_break()

        # 3. Asset Identification
        doc.add_heading("3. Asset Identification", 1)
        doc.add_paragraph(
            "The following assets have been identified and categorized according to their "
            "cybersecurity relevance."
        )

        assets = data.get("assets", [])
        if assets:
            table = doc.add_table(rows=len(assets) + 1, cols=4)
            table.style = "Table Grid"

            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = "Asset Name"
            hdr_cells[1].text = "Type"
            hdr_cells[2].text = "Security Attributes"
            hdr_cells[3].text = "Interfaces"

            for i, asset in enumerate(assets):
                row = table.rows[i + 1]
                row.cells[0].text = asset.get("name", "")
                row.cells[1].text = asset.get("asset_type", "")
                row.cells[2].text = "C/I/A"
                row.cells[3].text = str(len(asset.get("interfaces", [])))
        else:
            doc.add_paragraph("No assets identified yet.", style="Intense Quote")

        doc.add_page_break()

        # 4. Threat Analysis
        doc.add_heading("4. Threat Analysis", 1)
        doc.add_paragraph(
            "Threats were systematically identified using the STRIDE methodology "
            "(Spoofing, Tampering, Repudiation, Information Disclosure, "
            "Denial of Service, Elevation of Privilege)."
        )

        doc.add_page_break()

        # 5. Risk Assessment
        doc.add_heading("5. Risk Assessment", 1)
        doc.add_paragraph(
            "Risk levels were determined based on the combination of impact severity "
            "and attack feasibility, in accordance with ISO/SAE 21434 methodology."
        )

        doc.add_heading("5.1 Impact Assessment", 2)
        doc.add_paragraph(
            "Impact assessment considers safety, financial, operational, and privacy impacts."
        )

        doc.add_heading("5.2 Attack Feasibility Assessment", 2)
        doc.add_paragraph(
            "Attack feasibility is evaluated based on attack potential factors."
        )

        doc.add_page_break()

        # 6. Risk Treatment
        doc.add_heading("6. Risk Treatment", 1)
        doc.add_paragraph(
            "Based on the risk assessment results, appropriate risk treatment decisions "
            "and control measures have been identified."
        )

        doc.add_page_break()

        # Appendices
        doc.add_heading("Appendices", 1)
        doc.add_heading("A. Glossary", 2)
        doc.add_paragraph("TARA - Threat Analysis and Risk Assessment")
        doc.add_paragraph(
            "STRIDE - Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege"
        )
        doc.add_paragraph("CAL - Cybersecurity Assurance Level")

    async def _generate_default_sections(self, doc: Document, data: dict):
        """Generate default sections."""
        await self._generate_iso21434_sections(doc, data, None)
