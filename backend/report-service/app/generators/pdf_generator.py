"""PDF report generator."""

import io
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)
from app.common.config import settings
from app.common.utils import get_logger

logger = get_logger(__name__)

# Diagram service URL
DIAGRAM_SERVICE_URL = getattr(settings, 'diagram_service_url', 'http://diagram-service:8005')


class PDFGenerator:
    """Generate PDF reports."""

    def __init__(self):
        self._register_chinese_fonts()
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        self._diagram_cache: Dict[str, bytes] = {}

    async def _fetch_diagram(
        self,
        diagram_type: str,
        project_id: int,
        threat_id: Optional[int] = None,
    ) -> Optional[io.BytesIO]:
        """Fetch a diagram from the diagram service."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if diagram_type == "attack_tree" and threat_id:
                    url = f"{DIAGRAM_SERVICE_URL}/api/v1/diagrams/attack-tree/{threat_id}?format=png"
                else:
                    url = f"{DIAGRAM_SERVICE_URL}/api/v1/diagrams/{diagram_type.replace('_', '-')}/{project_id}?format=png"
                
                response = await client.get(url)
                
                if response.status_code == 200:
                    return io.BytesIO(response.content)
                else:
                    logger.warning(f"Failed to fetch diagram {diagram_type}: {response.status_code}")
        except Exception as e:
            logger.warning(f"Error fetching diagram {diagram_type}: {e}")
        
        return None

    def _add_diagram_to_story(
        self,
        story: list,
        diagram_buffer: Optional[io.BytesIO],
        title: str,
        width: float = 14 * cm,
        height: float = 10 * cm,
    ) -> None:
        """Add a diagram image to the story."""
        if diagram_buffer:
            try:
                diagram_buffer.seek(0)
                img = Image(diagram_buffer, width=width, height=height)
                story.append(img)
                story.append(Spacer(1, 8))
                story.append(Paragraph(f"<i>{title}</i>", self.styles["ChineseNormal"]))
                story.append(Spacer(1, 16))
            except Exception as e:
                logger.warning(f"Failed to add diagram to PDF: {e}")
                story.append(Paragraph(f"[图表加载失败: {title}]", self.styles["ChineseNormal"]))

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

        # Get project_id for diagrams
        project_id = content.get("project", {}).get("id") or data.get("project_id", 1)
        
        # 1.5 Architecture Overview
        story.append(PageBreak())
        story.append(Paragraph("1.5 Architecture Overview 架构概述", self.styles["ChineseHeading"]))
        story.append(Spacer(1, 12))
        
        # Item Boundary Section
        story.append(Paragraph("1.5.1 Item Boundary 项目边界", self.styles["ChineseSubHeading"]))
        story.append(
            Paragraph(
                "The item boundary defines the scope of this TARA analysis. "
                "Components within the boundary are subject to cybersecurity assessment.",
                self.styles["ChineseNormal"],
            )
        )
        story.append(Spacer(1, 8))
        
        # Fetch and add item boundary diagram
        item_boundary_diagram = await self._fetch_diagram("item-boundary", project_id)
        self._add_diagram_to_story(story, item_boundary_diagram, "图 1.1 项目边界图 (Item Boundary Diagram)")
        
        # Add boundary table
        project_name = content.get("project", {}).get("name", "Target System")
        boundary_data = [
            ["Component", "Type", "Within Boundary"],
            ["Core Processing Unit", "Internal", "Yes"],
            ["Security Module (HSM/SE)", "Internal", "Yes"],
            ["Communication Interface", "Internal", "Yes"],
            ["Data Storage", "Internal", "Yes"],
            ["External Network", "External", "Interface"],
            ["Cloud Services", "External", "Interface"],
            ["User Interface", "External", "Interface"],
        ]
        table = Table(boundary_data, colWidths=[6 * cm, 4 * cm, 4 * cm])
        table.setStyle(self._create_table_style())
        story.append(table)
        story.append(Spacer(1, 12))
        
        # System Architecture Section
        story.append(Paragraph("1.5.2 System Architecture 系统架构", self.styles["ChineseSubHeading"]))
        story.append(
            Paragraph(
                "The system architecture consists of multiple layers following industry best practices:",
                self.styles["ChineseNormal"],
            )
        )
        story.append(Spacer(1, 8))
        
        # Fetch and add system architecture diagram
        system_arch_diagram = await self._fetch_diagram("system-architecture", project_id)
        self._add_diagram_to_story(story, system_arch_diagram, "图 1.2 系统架构图 (System Architecture Diagram)")
        
        arch_data = [
            ["Layer", "Components", "Security Focus"],
            ["Application Layer", "HMI, Navigation, Media, ADAS", "Input Validation, Access Control"],
            ["Service Layer", "Security, Comm, Diagnostic, OTA", "Authentication, Encryption"],
            ["Middleware Layer", "AUTOSAR, Hypervisor, OS, Crypto", "Isolation, Secure Boot"],
            ["Hardware Layer", "SoC/MCU, HSM/SE, Memory, Network", "Hardware Security, Key Storage"],
        ]
        table = Table(arch_data, colWidths=[4 * cm, 5.5 * cm, 5.5 * cm])
        table.setStyle(self._create_table_style())
        story.append(table)
        story.append(Spacer(1, 12))
        
        # Software Architecture Section
        story.append(Paragraph("1.5.3 Software Architecture 软件架构", self.styles["ChineseSubHeading"]))
        story.append(
            Paragraph(
                "Key software modules and their security responsibilities:",
                self.styles["ChineseNormal"],
            )
        )
        story.append(Spacer(1, 8))
        
        # Fetch and add software architecture diagram
        sw_arch_diagram = await self._fetch_diagram("software-architecture", project_id)
        self._add_diagram_to_story(story, sw_arch_diagram, "图 1.3 软件架构图 (Software Architecture Diagram)")
        
        sw_arch_data = [
            ["Module", "Function", "Security Measures"],
            ["Security Manager", "Central security control", "Policy enforcement, Key management"],
            ["Application Manager", "App lifecycle management", "Sandbox, Privilege control"],
            ["Communication Manager", "Network protocols", "TLS/DTLS, Certificate validation"],
            ["Update Manager", "OTA updates", "Signature verification, Rollback protection"],
            ["Crypto Library", "Cryptographic operations", "AES, RSA, ECC, Hash functions"],
            ["Key Management", "Key lifecycle", "HSM integration, Key derivation"],
        ]
        table = Table(sw_arch_data, colWidths=[4.5 * cm, 5 * cm, 5.5 * cm])
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
        
        # Fetch and add asset relationship graph
        story.append(Paragraph("2.1 Asset Relationship Graph 资产关系图", self.styles["ChineseSubHeading"]))
        asset_graph_diagram = await self._fetch_diagram("asset-graph", project_id)
        self._add_diagram_to_story(story, asset_graph_diagram, "图 2.1 资产关系图 (Asset Relationship Graph)")
        
        # Fetch and add data flow diagram  
        story.append(Paragraph("2.2 Data Flow Diagram 数据流图", self.styles["ChineseSubHeading"]))
        data_flow_diagram = await self._fetch_diagram("data-flow", project_id)
        self._add_diagram_to_story(story, data_flow_diagram, "图 2.2 数据流图 (Data Flow Diagram)")
        
        story.append(Paragraph("2.3 Asset List 资产清单", self.styles["ChineseSubHeading"]))

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
        
        # Fetch and add attack tree diagram for first threat
        if threats:
            first_threat_id = threats[0].get("id")
            if first_threat_id and isinstance(first_threat_id, int):
                story.append(Paragraph("3.1 Attack Tree Analysis 攻击树分析", self.styles["ChineseSubHeading"]))
                attack_tree_diagram = await self._fetch_diagram("attack_tree", project_id, threat_id=first_threat_id)
                self._add_diagram_to_story(story, attack_tree_diagram, "图 3.1 攻击树示例 (Attack Tree Example)")
        
        story.append(Paragraph("3.2 Threat List 威胁清单", self.styles["ChineseSubHeading"]))

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
        
        # Fetch and add risk matrix diagram
        story.append(Paragraph("4.1 Risk Matrix 风险矩阵", self.styles["ChineseSubHeading"]))
        risk_matrix_diagram = await self._fetch_diagram("risk-matrix", project_id)
        self._add_diagram_to_story(story, risk_matrix_diagram, "图 4.1 风险矩阵 (Risk Matrix - ISO/SAE 21434)")
        
        story.append(Paragraph("4.2 Risk Distribution 风险分布", self.styles["ChineseSubHeading"]))

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
