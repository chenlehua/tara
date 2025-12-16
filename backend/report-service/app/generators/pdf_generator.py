"""PDF report generator."""

import io
import os
from datetime import datetime
from typing import Any, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)
from tara_shared.utils import get_logger

logger = get_logger(__name__)


class PDFGenerator:
    """Generate PDF reports."""

    def __init__(self):
        self._register_chinese_fonts()
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _register_chinese_fonts(self):
        """Register Chinese fonts for PDF generation."""
        try:
            # Try to register CID font for Chinese (built-in, no file needed)
            pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
            self.chinese_font = 'STSong-Light'
            self.chinese_font_bold = 'STSong-Light'
            logger.info("Registered CID font: STSong-Light")
        except Exception as e:
            logger.warning(f"Failed to register CID font: {e}")
            # Try common system fonts
            font_paths = [
                # Linux
                '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
                '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',
                # Alternative Linux paths
                '/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc',
                '/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc',
                # macOS
                '/System/Library/Fonts/PingFang.ttc',
                '/System/Library/Fonts/STHeiti Light.ttc',
                # Windows
                'C:/Windows/Fonts/simhei.ttf',
                'C:/Windows/Fonts/simsun.ttc',
            ]
            
            font_registered = False
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                        self.chinese_font = 'ChineseFont'
                        self.chinese_font_bold = 'ChineseFont'
                        font_registered = True
                        logger.info(f"Registered TTF font: {font_path}")
                        break
                    except Exception as ex:
                        logger.warning(f"Failed to register font {font_path}: {ex}")
            
            if not font_registered:
                # Fallback to Helvetica (won't display Chinese correctly but won't crash)
                logger.warning("No Chinese font found, using Helvetica as fallback")
                self.chinese_font = 'Helvetica'
                self.chinese_font_bold = 'Helvetica-Bold'

    def _setup_styles(self):
        """Setup custom styles with Chinese font support."""
        self.styles.add(
            ParagraphStyle(
                name="ChineseNormal",
                fontName=self.chinese_font,
                fontSize=10,
                leading=14,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="ChineseTitle",
                fontName=self.chinese_font_bold,
                fontSize=18,
                leading=22,
                spaceAfter=20,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="ChineseHeading",
                fontName=self.chinese_font_bold,
                fontSize=14,
                leading=18,
                spaceBefore=12,
                spaceAfter=8,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="ChineseSubHeading",
                fontName=self.chinese_font_bold,
                fontSize=12,
                leading=16,
                spaceBefore=8,
                spaceAfter=6,
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

        # Project info from content
        content = data.get("content", {})
        project = content.get("project", data.get("project", {}))
        
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
        story.append(
            Paragraph(
                f"Standard: {project.get('standard', 'ISO/SAE 21434')}",
                self.styles["ChineseNormal"],
            )
        )
        story.append(
            Paragraph(
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
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

    def _create_table_style(self) -> TableStyle:
        """Create standard table style with Chinese font support."""
        return TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), self.chinese_font_bold),
            ("FONTNAME", (0, 1), (-1, -1), self.chinese_font),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("TOPPADDING", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("TOPPADDING", (0, 1), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ])

    async def _generate_iso21434_sections(
        self,
        data: dict,
        sections: list[str] = None,
    ) -> list:
        """Generate ISO 21434 format sections."""
        story = []
        content = data.get("content", {})

        # 1. Executive Summary
        story.append(Paragraph("1. Executive Summary", self.styles["ChineseHeading"]))
        story.append(
            Paragraph(
                "This report presents the results of the Threat Analysis and Risk Assessment (TARA) "
                "conducted in accordance with ISO/SAE 21434 requirements.",
                self.styles["ChineseNormal"],
            )
        )
        story.append(Spacer(1, 12))

        # Statistics from content
        assets = content.get("assets", [])
        threats = content.get("threats", [])
        measures = content.get("control_measures", [])
        risk_dist = content.get("risk_distribution", {})
        
        high_risk = risk_dist.get("CAL-4", 0) + risk_dist.get("CAL-3", 0)
        
        stats_data = [
            ["Metric", "Value"],
            ["Total Assets", str(len(assets))],
            ["Total Threats", str(len(threats))],
            ["High Risk Items (CAL-3/4)", str(high_risk)],
            ["Control Measures", str(len(measures))],
        ]

        table = Table(stats_data, colWidths=[8 * cm, 4 * cm])
        table.setStyle(self._create_table_style())
        story.append(table)
        story.append(Spacer(1, 20))

        # 2. Asset Identification
        story.append(PageBreak())
        story.append(Paragraph("2. Asset Identification", self.styles["ChineseHeading"]))
        story.append(
            Paragraph(
                "The following assets have been identified for the target vehicle system:",
                self.styles["ChineseNormal"],
            )
        )
        story.append(Spacer(1, 12))

        if assets:
            asset_data = [["Name", "Type", "Interfaces", "Security Level"]]
            for asset in assets[:20]:  # Limit to 20 assets
                interfaces = asset.get("interfaces", [])
                iface_str = ", ".join([
                    i.get("type", str(i)) if isinstance(i, dict) else str(i) 
                    for i in interfaces[:3]
                ])
                if len(interfaces) > 3:
                    iface_str += f" (+{len(interfaces) - 3})"
                
                asset_data.append([
                    asset.get("name", "N/A")[:30],
                    asset.get("type", asset.get("asset_type", "N/A")),
                    iface_str or "-",
                    asset.get("security_level", asset.get("criticality", "CAL-2")),
                ])
            
            col_widths = [5 * cm, 3 * cm, 4 * cm, 3 * cm]
            table = Table(asset_data, colWidths=col_widths)
            table.setStyle(self._create_table_style())
            story.append(table)
            
            if len(assets) > 20:
                story.append(Spacer(1, 8))
                story.append(Paragraph(
                    f"... and {len(assets) - 20} more assets",
                    self.styles["ChineseNormal"],
                ))
        else:
            story.append(Paragraph("No assets identified.", self.styles["ChineseNormal"]))
        
        story.append(Spacer(1, 12))

        # 3. Threat Analysis
        story.append(PageBreak())
        story.append(Paragraph("3. Threat Analysis", self.styles["ChineseHeading"]))
        story.append(
            Paragraph(
                "Threats were identified using the STRIDE methodology "
                "(Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege):",
                self.styles["ChineseNormal"],
            )
        )
        story.append(Spacer(1, 12))

        if threats:
            threat_data = [["ID", "Threat Name", "Category", "Risk Level"]]
            for threat in threats[:20]:  # Limit to 20 threats
                threat_data.append([
                    threat.get("id", "N/A"),
                    threat.get("name", "N/A")[:35],
                    threat.get("category_name", threat.get("category", "N/A")),
                    threat.get("risk_level", "CAL-2"),
                ])
            
            col_widths = [2.5 * cm, 6.5 * cm, 3 * cm, 3 * cm]
            table = Table(threat_data, colWidths=col_widths)
            table.setStyle(self._create_table_style())
            story.append(table)
            
            if len(threats) > 20:
                story.append(Spacer(1, 8))
                story.append(Paragraph(
                    f"... and {len(threats) - 20} more threats",
                    self.styles["ChineseNormal"],
                ))
        else:
            story.append(Paragraph("No threats identified.", self.styles["ChineseNormal"]))

        story.append(Spacer(1, 12))

        # 4. Risk Assessment
        story.append(PageBreak())
        story.append(Paragraph("4. Risk Assessment", self.styles["ChineseHeading"]))
        story.append(
            Paragraph(
                "Risk levels were determined based on impact severity and attack feasibility:",
                self.styles["ChineseNormal"],
            )
        )
        story.append(Spacer(1, 12))

        if risk_dist:
            risk_data = [
                ["Risk Level", "Count", "Description"],
                ["CAL-4", str(risk_dist.get("CAL-4", 0)), "Critical - Immediate action required"],
                ["CAL-3", str(risk_dist.get("CAL-3", 0)), "High - Priority treatment needed"],
                ["CAL-2", str(risk_dist.get("CAL-2", 0)), "Medium - Planned treatment"],
                ["CAL-1", str(risk_dist.get("CAL-1", 0)), "Low - Acceptable risk"],
            ]
            
            col_widths = [3 * cm, 3 * cm, 9 * cm]
            table = Table(risk_data, colWidths=col_widths)
            table.setStyle(self._create_table_style())
            story.append(table)

        story.append(Spacer(1, 12))

        # 5. Control Measures
        story.append(PageBreak())
        story.append(Paragraph("5. Control Measures", self.styles["ChineseHeading"]))
        story.append(
            Paragraph(
                "The following security control measures have been recommended:",
                self.styles["ChineseNormal"],
            )
        )
        story.append(Spacer(1, 12))

        if measures:
            measure_data = [["Measure Name", "Type", "Effectiveness", "ISO 21434 Ref"]]
            for measure in measures[:20]:  # Limit to 20 measures
                eff = measure.get("effectiveness", "medium")
                eff_text = {"high": "High", "medium": "Medium", "low": "Low"}.get(eff, "Medium")
                
                measure_data.append([
                    measure.get("name", "N/A")[:35],
                    measure.get("control_type", measure.get("category", "preventive")),
                    eff_text,
                    measure.get("iso21434_ref", "-"),
                ])
            
            col_widths = [6 * cm, 3 * cm, 3 * cm, 3 * cm]
            table = Table(measure_data, colWidths=col_widths)
            table.setStyle(self._create_table_style())
            story.append(table)
            
            if len(measures) > 20:
                story.append(Spacer(1, 8))
                story.append(Paragraph(
                    f"... and {len(measures) - 20} more measures",
                    self.styles["ChineseNormal"],
                ))
        else:
            story.append(Paragraph("No control measures defined.", self.styles["ChineseNormal"]))

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
