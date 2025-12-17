"""Excel report generator - ISO 21434 TARA Format."""

import io
from datetime import datetime
from typing import Any, Dict, List, Optional

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.utils.cell import range_boundaries
from tara_shared.utils import get_logger

logger = get_logger(__name__)


class ExcelGenerator:
    """Generate Excel reports in ISO 21434 TARA format."""

    def __init__(self):
        # Define styles
        self.title_font = Font(bold=True, size=16, color="FFFFFF")
        self.title_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
        
        self.header_font = Font(bold=True, size=10, color="FFFFFF")
        self.header_fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")
        self.header_fill_alt = PatternFill(start_color="5B9BD5", end_color="5B9BD5", fill_type="solid")
        
        self.subheader_font = Font(bold=True, size=9)
        self.subheader_fill = PatternFill(start_color="BDD7EE", end_color="BDD7EE", fill_type="solid")
        
        self.data_font = Font(size=9)
        self.alt_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
        
        self.border = Border(
            left=Side(style='thin', color='000000'),
            right=Side(style='thin', color='000000'),
            top=Side(style='thin', color='000000'),
            bottom=Side(style='thin', color='000000')
        )
        
        self.center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
        self.left_align = Alignment(horizontal='left', vertical='center', wrap_text=True)

        # Risk colors
        self.risk_fills = {
            'CAL-4': PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid"),
            'CAL-3': PatternFill(start_color="FFC000", end_color="FFC000", fill_type="solid"),
            'CAL-2': PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid"),
            'CAL-1': PatternFill(start_color="92D050", end_color="92D050", fill_type="solid"),
        }

    def _apply_cell_style(self, cell, font=None, fill=None, alignment=None, border=True):
        """Apply styles to a cell."""
        if font:
            cell.font = font
        if fill:
            cell.fill = fill
        if alignment:
            cell.alignment = alignment
        if border:
            cell.border = self.border

    def _merge_and_style(self, ws, start_row, start_col, end_row, end_col, value, font=None, fill=None, alignment=None):
        """Merge cells and apply style."""
        ws.merge_cells(start_row=start_row, start_column=start_col, end_row=end_row, end_column=end_col)
        cell = ws.cell(row=start_row, column=start_col, value=value)
        self._apply_cell_style(cell, font, fill, alignment or self.center_align)
        
        # Apply border to all merged cells
        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                ws.cell(row=row, column=col).border = self.border

    async def generate(
        self,
        data: dict,
        template: str = "iso21434",
        sections: list[str] = None,
    ) -> io.BytesIO:
        """Generate Excel report in TARA format."""
        wb = Workbook()
        
        # Get content
        content = data.get("content", {})
        project = content.get("project", data.get("project", {}))
        assets = content.get("assets", [])
        threats = content.get("threats", [])
        measures = content.get("control_measures", [])
        risk_dist = content.get("risk_distribution", {})

        # Create sheets in order
        self._create_definitions_sheet(wb, project)
        self._create_asset_list_sheet(wb, assets)
        self._create_data_flow_sheet(wb, assets)
        self._create_attack_tree_sheet(wb, threats)
        self._create_tara_results_sheet(wb, assets, threats, measures, risk_dist)

        # Remove default sheet
        if 'Sheet' in wb.sheetnames:
            del wb['Sheet']

        # Save to buffer
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        return buffer

    def _create_definitions_sheet(self, wb: Workbook, project: dict):
        """Create 1-相关定义 sheet with diagrams."""
        ws = wb.create_sheet("1-相关定义", 0)

        project_name = project.get("name", "TARA分析项目")
        vehicle_type = project.get("vehicle_type", "车载系统")
        description = project.get("description", "")
        
        # Title
        self._merge_and_style(ws, 1, 1, 1, 12, 
                             f"{project_name} TARA分析报告 - 相关定义",
                             self.title_font, self.title_fill)
        
        # Section 1: Functional Description
        row = 3
        ws.cell(row=row, column=1, value="1. 功能描述 Functional Description").font = Font(bold=True, size=12)
        row += 1
        
        func_desc = description or f"{project_name}是一个需要进行威胁分析和风险评估(TARA)的车载系统组件。"
        ws.cell(row=row, column=1, value=func_desc)
        ws.merge_cells(start_row=row, start_column=1, end_row=row+2, end_column=12)
        ws.cell(row=row, column=1).alignment = Alignment(wrap_text=True, vertical='top')
        
        # Section 2: Item Boundary Diagram
        row = 9
        ws.cell(row=row, column=1, value="2. 项目边界图 Item Boundary Diagram").font = Font(bold=True, size=12)
        row += 1
        
        # Draw item boundary diagram using text/ASCII art
        boundary_diagram = """
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    系统边界 System Boundary                                       │
│                                                                                                   │
│   ┌────────────────────┐          ┌────────────────────┐          ┌────────────────────┐        │
│   │   Core Processing  │ ◄──────► │   Security Module   │ ◄──────► │   Communication    │        │
│   │   核心处理单元      │          │   安全模块          │          │   通信接口          │        │
│   └────────────────────┘          └────────────────────┘          └────────────────────┘        │
│            │                               │                               │                     │
│            ▼                               ▼                               ▼                     │
│   ┌────────────────────┐          ┌────────────────────┐          ┌────────────────────┐        │
│   │   Data Storage     │          │   Crypto Engine    │          │   Network Interface │        │
│   │   数据存储          │          │   加密引擎          │          │   网络接口          │        │
│   └────────────────────┘          └────────────────────┘          └────────────────────┘        │
│                                                                                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
           ▲                                  ▲                                  ▲
           │                                  │                                  │
    ┌──────┴──────┐                   ┌───────┴───────┐                  ┌───────┴───────┐
    │ User Input  │                   │ Cloud Services │                  │ External APIs │
    │ 用户输入     │                   │ 云端服务       │                  │ 外部接口       │
    └─────────────┘                   └───────────────┘                  └───────────────┘
"""
        ws.cell(row=row, column=1, value=boundary_diagram)
        ws.merge_cells(start_row=row, start_column=1, end_row=row+18, end_column=12)
        ws.cell(row=row, column=1).alignment = Alignment(wrap_text=True, vertical='top')
        ws.cell(row=row, column=1).font = Font(name='Courier New', size=9)
        
        # Section 3: System Architecture Diagram
        row = 30
        ws.cell(row=row, column=1, value="3. 系统架构图 System Architecture Diagram").font = Font(bold=True, size=12)
        row += 1
        
        system_arch = """
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              应用层 Application Layer                                              │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│   │     HMI      │    │  Navigation  │    │    Media     │    │     ADAS     │                  │
│   │   人机界面   │    │     导航     │    │    多媒体    │    │   辅助驾驶   │                  │
│   └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                              服务层 Service Layer                                                  │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│   │   Security   │    │     Comm     │    │  Diagnostic  │    │     OTA      │                  │
│   │   安全服务   │    │   通信服务   │    │   诊断服务   │    │   升级服务   │                  │
│   └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                              中间件层 Middleware Layer                                             │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│   │   AUTOSAR    │    │  Hypervisor  │    │      OS      │    │    Crypto    │                  │
│   │ 软件架构     │    │   虚拟化     │    │   操作系统   │    │   加密模块   │                  │
│   └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                              硬件层 Hardware Layer                                                 │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│   │   SoC/MCU    │    │   HSM/SE     │    │    Memory    │    │   Network    │                  │
│   │   处理器     │    │   安全芯片   │    │    存储器    │    │   网络接口   │                  │
│   └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
"""
        ws.cell(row=row, column=1, value=system_arch)
        ws.merge_cells(start_row=row, start_column=1, end_row=row+24, end_column=12)
        ws.cell(row=row, column=1).alignment = Alignment(wrap_text=True, vertical='top')
        ws.cell(row=row, column=1).font = Font(name='Courier New', size=9)
        
        # Section 4: Software Architecture Diagram
        row = 58
        ws.cell(row=row, column=1, value="4. 软件架构图 Software Architecture Diagram").font = Font(bold=True, size=12)
        row += 1
        
        software_arch = """
                           ┌────────────────────────────────────────┐
                           │        Security Manager 安全管理器     │
                           └───────────────────┬────────────────────┘
                                               │
              ┌────────────────────────────────┼────────────────────────────────┐
              │                                │                                │
              ▼                                ▼                                ▼
   ┌────────────────────┐         ┌────────────────────┐         ┌────────────────────┐
   │ Application Manager│         │Communication Manager│        │   Update Manager   │
   │    应用管理器      │         │    通信管理器       │        │   OTA升级管理器    │
   └─────────┬──────────┘         └─────────┬──────────┘         └─────────┬──────────┘
             │                              │                              │
             ▼                              ▼                              ▼
   ┌────────────────────┐         ┌────────────────────┐         ┌────────────────────┐
   │ Diagnostic Handler │         │   Crypto Library   │         │   Key Management   │
   │    诊断处理器      │         │      加密库        │         │     密钥管理       │
   └────────────────────┘         └────────────────────┘         └────────────────────┘
                                               │
                                               ▼
              ┌─────────────────────────────────────────────────────────────────┐
              │            Hardware Abstraction Layer (HAL) 硬件抽象层          │
              └─────────────────────────────────────────────────────────────────┘
"""
        ws.cell(row=row, column=1, value=software_arch)
        ws.merge_cells(start_row=row, start_column=1, end_row=row+18, end_column=12)
        ws.cell(row=row, column=1).alignment = Alignment(wrap_text=True, vertical='top')
        ws.cell(row=row, column=1).font = Font(name='Courier New', size=9)
        
        # Section 5: Reference Standards
        row = 80
        ws.cell(row=row, column=1, value="5. 参考标准 Reference Standards").font = Font(bold=True, size=12)
        row += 1
        standards = [
            "• ISO/SAE 21434:2021 - Road vehicles — Cybersecurity engineering",
            "• UN R155 - Cyber Security Management System",
            "• UN R156 - Software Update Management System",
            "• GB/T XXXXX - 汽车网络安全相关标准",
            "• ISO 26262 - Functional Safety",
            "• AUTOSAR Cybersecurity Guidelines",
        ]
        for std in standards:
            ws.cell(row=row, column=1, value=std)
            row += 1

        # Section 6: Document Info
        row += 2
        ws.cell(row=row, column=1, value="6. 文档信息 Document Information").font = Font(bold=True, size=12)
        row += 1
        
        doc_info = [
            ("文档版本 Version", "1.0"),
            ("创建日期 Created", datetime.now().strftime("%Y-%m-%d")),
            ("作者 Author", "TARA Pro System"),
            ("适用标准 Standard", project.get("standard", "ISO/SAE 21434")),
            ("车型 Vehicle Type", vehicle_type),
            ("项目阶段 Phase", "Concept/Development"),
        ]
        for label, value in doc_info:
            ws.cell(row=row, column=1, value=label).font = Font(bold=True)
            ws.cell(row=row, column=2, value=value)
            row += 1

        # Adjust column widths
        ws.column_dimensions['A'].width = 30
        for col in range(2, 13):
            ws.column_dimensions[get_column_letter(col)].width = 12
        
        # Set row heights for diagram sections
        for r in range(10, 28):
            ws.row_dimensions[r].height = 15
        for r in range(31, 55):
            ws.row_dimensions[r].height = 15
        for r in range(59, 77):
            ws.row_dimensions[r].height = 15

    def _create_asset_list_sheet(self, wb: Workbook, assets: list):
        """Create 2-资产列表 sheet."""
        ws = wb.create_sheet("2-资产列表")

        # Title
        self._merge_and_style(ws, 1, 1, 1, 10, 
                             "资产列表 Asset List",
                             self.title_font, self.title_fill)

        # Header Group Row 3
        self._merge_and_style(ws, 3, 1, 3, 4, 
                             "Asset Identification 资产识别",
                             self.header_font, self.header_fill)
        self._merge_and_style(ws, 3, 5, 3, 10, 
                             "Cybersecurity Attributes 网络安全属性",
                             self.header_font, self.header_fill_alt)

        # Header Row 4
        headers = [
            ("资产ID\nAsset ID", 10),
            ("资产名称\nAsset Name", 25),
            ("分类\nCategory", 12),
            ("备注\nRemarks", 30),
            ("真实性\nAuthenticity", 10),
            ("完整性\nIntegrity", 10),
            ("不可抵赖性\nNon-repudiation", 12),
            ("机密性\nConfidentiality", 12),
            ("可用性\nAvailability", 10),
            ("权限\nAuthorization", 12),
        ]
        
        for col, (header, width) in enumerate(headers, 1):
            cell = ws.cell(row=4, column=col, value=header)
            self._apply_cell_style(cell, self.subheader_font, self.subheader_fill, self.center_align)
            ws.column_dimensions[get_column_letter(col)].width = width

        # Data rows
        for row_idx, asset in enumerate(assets, 5):
            asset_id = asset.get("id", f"A-{row_idx-4:03d}")
            if isinstance(asset_id, int):
                asset_id = f"A-{asset_id:03d}"
            
            # Get security attributes
            security_attrs = asset.get("security_attrs", asset.get("security_attributes", {})) or {}
            
            row_data = [
                asset_id,
                asset.get("name", ""),
                asset.get("category", asset.get("asset_type", "内部实体")),
                asset.get("description", ""),
                "√" if security_attrs.get("authenticity") else "",
                "√" if security_attrs.get("integrity") else "√",  # Default integrity
                "√" if security_attrs.get("non_repudiation") else "",
                "√" if security_attrs.get("confidentiality") else "",
                "√" if security_attrs.get("availability") else "√",  # Default availability
                "√" if security_attrs.get("authorization") else "",
            ]
            
            for col, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_idx, column=col, value=value)
                fill = self.alt_fill if row_idx % 2 == 0 else None
                self._apply_cell_style(cell, self.data_font, fill, self.center_align if col >= 5 else self.left_align)

    def _create_data_flow_sheet(self, wb: Workbook, assets: list):
        """Create 3-数据流图 sheet."""
        ws = wb.create_sheet("3-数据流图")

        # Title
        self._merge_and_style(ws, 1, 1, 1, 14, 
                             "数据流图 Data Flow Diagram",
                             self.title_font, self.title_fill)

        # Create a simple data flow diagram using text
        row = 3
        ws.cell(row=row, column=1, value="系统数据流分析:").font = Font(bold=True, size=11)
        
        row = 5
        # Build a simple diagram based on assets
        external_entities = [a for a in assets if a.get("is_external", False) or "外部" in str(a.get("category", ""))]
        internal_entities = [a for a in assets if not a.get("is_external", False) and "外部" not in str(a.get("category", ""))]
        
        diagram_text = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                               系统边界 System Boundary                        │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐               │
│  │   外部接口    │ ───► │   核心处理   │ ───► │   内部通信   │               │
│  │ (WiFi/BT/4G) │ ◄─── │   (SOC/MCU)  │ ◄─── │  (CAN/ETH)   │               │
│  └──────────────┘      └──────────────┘      └──────────────┘               │
│         │                     │                     │                        │
│         ▼                     ▼                     ▼                        │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐               │
│  │   数据存储    │      │   安全模块   │      │   车身控制   │               │
│  │  (ROM/RAM)   │      │   (HSM/SE)   │      │   (BCM等)    │               │
│  └──────────────┘      └──────────────┘      └──────────────┘               │
└─────────────────────────────────────────────────────────────────────────────┘
"""
        ws.cell(row=row, column=1, value=diagram_text)
        ws.merge_cells(start_row=row, start_column=1, end_row=row+15, end_column=14)
        ws.cell(row=row, column=1).alignment = Alignment(wrap_text=True, vertical='top')
        ws.cell(row=row, column=1).font = Font(name='Courier New', size=10)

        # Asset interfaces table
        row = 25
        ws.cell(row=row, column=1, value="资产接口列表:").font = Font(bold=True, size=11)
        row += 2
        
        # Headers
        headers = ["资产", "接口类型", "连接对象", "数据流向"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col, value=header)
            self._apply_cell_style(cell, self.header_font, self.header_fill, self.center_align)
        
        row += 1
        for asset in assets[:15]:
            interfaces = asset.get("interfaces", [])
            for iface in interfaces[:2]:
                iface_type = iface.get("type", str(iface)) if isinstance(iface, dict) else str(iface)
                row_data = [
                    asset.get("name", "")[:20],
                    iface_type,
                    iface.get("connected_to", "-") if isinstance(iface, dict) else "-",
                    "双向"
                ]
                for col, value in enumerate(row_data, 1):
                    cell = ws.cell(row=row, column=col, value=value)
                    self._apply_cell_style(cell, self.data_font, None, self.left_align)
                row += 1

        # Adjust column widths
        for col in range(1, 15):
            ws.column_dimensions[get_column_letter(col)].width = 15

    def _create_attack_tree_sheet(self, wb: Workbook, threats: list):
        """Create 4-攻击树图 sheet."""
        ws = wb.create_sheet("4-攻击树图")

        # Title
        self._merge_and_style(ws, 1, 1, 1, 15, 
                             "攻击树分析 Attack Tree Analysis",
                             self.title_font, self.title_fill)

        row = 3
        
        # Group threats by STRIDE category
        stride_groups = {
            'S': [], 'T': [], 'R': [], 'I': [], 'D': [], 'E': []
        }
        for threat in threats:
            threat_type = threat.get("threat_type", threat.get("category", "T"))
            if threat_type in stride_groups:
                stride_groups[threat_type].append(threat)

        stride_names = {
            'S': 'Spoofing (欺骗)',
            'T': 'Tampering (篡改)',
            'R': 'Repudiation (抵赖)',
            'I': 'Information Disclosure (信息泄露)',
            'D': 'Denial of Service (拒绝服务)',
            'E': 'Elevation of Privilege (权限提升)'
        }

        tree_num = 1
        for stride_type, stride_threats in stride_groups.items():
            if not stride_threats:
                continue
                
            ws.cell(row=row, column=1, value=f"攻击树{tree_num}: {stride_names[stride_type]}").font = Font(bold=True, size=11)
            row += 1
            
            # Draw attack tree
            root_threat = stride_threats[0] if stride_threats else {}
            tree_text = f"""
                    ┌─────────────────────────────────────┐
                    │  攻击目标: {stride_names[stride_type][:15]}     │
                    └───────────────┬─────────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
      ┌───────┴───────┐     ┌───────┴───────┐     ┌───────┴───────┐
      │  攻击路径1     │     │  攻击路径2     │     │  攻击路径3     │
      │  远程攻击      │     │  物理接入      │     │  供应链攻击    │
      └───────┬───────┘     └───────┬───────┘     └───────┬───────┘
              │                     │                     │
        [具体手段]             [具体手段]             [具体手段]
"""
            ws.cell(row=row, column=1, value=tree_text)
            ws.merge_cells(start_row=row, start_column=1, end_row=row+12, end_column=15)
            ws.cell(row=row, column=1).alignment = Alignment(wrap_text=True, vertical='top')
            ws.cell(row=row, column=1).font = Font(name='Courier New', size=9)
            
            row += 14
            tree_num += 1
            
            if tree_num > 4:  # Limit to 4 attack trees
                break

        # Adjust column width
        ws.column_dimensions['A'].width = 100

    def _create_tara_results_sheet(self, wb: Workbook, assets: list, threats: list, measures: list, risk_dist: dict):
        """Create 5-TARA分析结果 sheet - Main analysis results."""
        ws = wb.create_sheet("5-TARA分析结果")

        # Title
        self._merge_and_style(ws, 1, 1, 1, 38, 
                             "TARA分析结果 TARA Analysis Results",
                             self.title_font, self.title_fill)

        # Row 3: Main header groups
        header_groups = [
            (1, 3, "Asset Identification\n资产识别"),
            (4, 8, "Threat & Damage Scenario\n威胁&损害场景"),
            (9, 18, "Threat Analysis\n威胁分析"),
            (19, 32, "Impact Analysis\n影响分析"),
            (33, 33, "Risk Assessment\n风险评估"),
            (34, 34, "Risk Treatment\n风险处置"),
            (35, 38, "Risk Mitigation\n风险缓解"),
        ]
        
        for start_col, end_col, title in header_groups:
            self._merge_and_style(ws, 3, start_col, 3, end_col, title,
                                 self.header_font, self.header_fill, self.center_align)

        # Row 4: Sub-headers
        sub_headers_row4 = {
            1: "资产ID\nAsset ID",
            2: "资产名称\nAsset Name",
            3: "分类\nCategory",
            4: "Security Attributes\n安全属性",
            5: "STRIDE Model\nSTRIDE模型",
            6: "Potential Threat\n潜在威胁和损害场景",
            7: "Attack Path\n攻击路径",
            8: "Source\nWP29 Mapping",
            9: "Attack Vector(V)\n攻击向量",
            11: "Attack Complexity(C)\n攻击复杂度",
            13: "Privileges Required(P)\n权限要求",
            15: "User Interaction(U)\n用户交互",
            17: "Attack Feasibility\n攻击可行性",
            19: "Safety\n安全",
            22: "Financial\n经济",
            25: "Operational\n操作",
            28: "Privacy\n隐私",
            31: "Impact Calculation\n影响计算",
            33: "Risk Level\n风险等级",
            34: "Risk Treatment\n风险处置决策",
            35: "Security Goal\n安全目标",
            36: "Security Requirement\n安全需求",
            37: "WP29 Control\n控制措施来源",
            38: "ISO 21434 Ref\n参考条款",
        }
        
        for col, title in sub_headers_row4.items():
            # Check if we need to merge
            if col in [9, 11, 13, 15, 19, 22, 25, 28, 31]:
                # These span 2-3 columns
                if col in [9, 11, 13, 15]:
                    self._merge_and_style(ws, 4, col, 4, col+1, title,
                                         self.subheader_font, self.subheader_fill)
                elif col in [19, 22, 25, 28]:
                    self._merge_and_style(ws, 4, col, 4, col+2, title,
                                         self.subheader_font, self.subheader_fill)
                elif col == 31:
                    self._merge_and_style(ws, 4, col, 4, col+1, title,
                                         self.subheader_font, self.subheader_fill)
                elif col == 17:
                    self._merge_and_style(ws, 4, col, 4, col+1, title,
                                         self.subheader_font, self.subheader_fill)
            else:
                cell = ws.cell(row=4, column=col, value=title)
                self._apply_cell_style(cell, self.subheader_font, self.subheader_fill, self.center_align)

        # Row 5: Detail headers for complex columns
        detail_headers = {
            9: "Content\n内容", 10: "Value\n值",
            11: "Content\n内容", 12: "Value\n值",
            13: "Level\n等级", 14: "Value\n值",
            15: "Level\n等级", 16: "Value\n值",
            17: "Calc\n计算", 18: "Level\n等级",
            19: "Content\n内容", 20: "Notes\n注释", 21: "Value\n值",
            22: "Content\n内容", 23: "Notes\n注释", 24: "Value\n值",
            25: "Content\n内容", 26: "Notes\n注释", 27: "Value\n值",
            28: "Content\n内容", 29: "Notes\n注释", 30: "Value\n值",
            31: "Calc\n计算", 32: "Level\n等级",
        }
        
        for col, title in detail_headers.items():
            cell = ws.cell(row=5, column=col, value=title)
            self._apply_cell_style(cell, Font(bold=True, size=8), self.subheader_fill, self.center_align)

        # Fill remaining row 5 cells with borders
        for col in range(1, 39):
            if col not in detail_headers:
                ws.cell(row=5, column=col).border = self.border

        # Prepare measures lookup
        measures_by_threat = {}
        for m in measures:
            tid = m.get("threat_id") or m.get("threat_risk_id")
            if tid:
                if tid not in measures_by_threat:
                    measures_by_threat[tid] = []
                measures_by_threat[tid].append(m)

        # Data rows
        row = 6
        for threat in threats:
            # Get associated asset
            asset_id = threat.get("asset_id", "")
            asset = next((a for a in assets if a.get("id") == asset_id), {})
            
            # Asset info
            asset_id_str = f"A-{asset_id:03d}" if isinstance(asset_id, int) else str(asset_id) or f"A-{row-5:03d}"
            asset_name = asset.get("name", "") or threat.get("asset_name", "")
            category = asset.get("category", asset.get("asset_type", "内部实体"))
            
            # Threat info
            threat_type = threat.get("threat_type", threat.get("category", "T"))
            stride_map = {
                'S': "S-Spoofing\n欺骗",
                'T': "T-Tampering\n篡改", 
                'R': "R-Repudiation\n抵赖",
                'I': "I-Info Disclosure\n信息泄露",
                'D': "D-DoS\n拒绝服务",
                'E': "E-Elevation\n权限提升"
            }
            stride_model = stride_map.get(threat_type, "T-Tampering\n篡改")
            
            threat_name = threat.get("name", threat.get("threat_name", ""))
            attack_path = threat.get("attack_path", threat.get("attack_vector", "-"))
            
            # Get security attribute affected
            sec_attr_map = {
                'S': "Authenticity\n真实性",
                'T': "Integrity\n完整性",
                'R': "Non-repudiation\n不可抵赖性",
                'I': "Confidentiality\n机密性",
                'D': "Availability\n可用性",
                'E': "Authorization\n权限"
            }
            sec_attr = sec_attr_map.get(threat_type, "Integrity\n完整性")
            
            # Attack analysis values
            attack_vector = self._get_attack_vector(threat)
            attack_complexity = self._get_attack_complexity(threat)
            privileges = self._get_privileges(threat)
            user_interaction = self._get_user_interaction(threat)
            
            # Calculate attack feasibility
            av_val = attack_vector[1]
            ac_val = attack_complexity[1]
            pr_val = privileges[1]
            ui_val = user_interaction[1]
            feasibility_calc = av_val + ac_val + pr_val + ui_val
            feasibility_level = self._get_feasibility_level(feasibility_calc)
            
            # Impact analysis
            safety = self._get_impact_safety(threat)
            financial = self._get_impact_financial(threat)
            operational = self._get_impact_operational(threat)
            privacy = self._get_impact_privacy(threat)
            
            # Calculate impact
            impact_calc = max(safety[2], financial[2], operational[2], privacy[2])
            impact_level = self._get_impact_level(impact_calc)
            
            # Risk level
            risk_level = threat.get("risk_level", self._calculate_risk_level(feasibility_calc, impact_calc))
            
            # Get measures
            threat_measures = measures_by_threat.get(threat.get("id"), [])
            sec_goal = threat_measures[0].get("name", "SC-01:安全控制") if threat_measures else "-"
            sec_req = threat_measures[0].get("implementation", "SR-01:实施安全措施") if threat_measures else "-"
            wp29_ref = threat_measures[0].get("iso21434_ref", "-") if threat_measures else "-"
            
            # Build row data
            row_data = [
                asset_id_str,                    # 1
                asset_name[:15],                 # 2
                category,                        # 3
                sec_attr,                        # 4
                stride_model,                    # 5
                threat_name[:40],                # 6
                attack_path[:20] if attack_path else "-",  # 7
                threat.get("wp29_ref", "-"),     # 8
                attack_vector[0], av_val,        # 9, 10
                attack_complexity[0], ac_val,    # 11, 12
                privileges[0], pr_val,           # 13, 14
                user_interaction[0], ui_val,     # 15, 16
                feasibility_calc, feasibility_level,  # 17, 18
                safety[0], safety[1], safety[2], # 19, 20, 21
                financial[0], financial[1], financial[2],  # 22, 23, 24
                operational[0], operational[1], operational[2],  # 25, 26, 27
                privacy[0], privacy[1], privacy[2],  # 28, 29, 30
                impact_calc, impact_level,       # 31, 32
                risk_level,                      # 33
                self._get_risk_treatment(risk_level),  # 34
                sec_goal[:20],                   # 35
                sec_req[:25],                    # 36
                wp29_ref,                        # 37
                threat.get("iso_clause", "-"),   # 38
            ]
            
            for col, value in enumerate(row_data, 1):
                cell = ws.cell(row=row, column=col, value=value)
                fill = self.alt_fill if row % 2 == 0 else None
                
                # Apply risk color to risk level column
                if col == 33 and value in self.risk_fills:
                    fill = self.risk_fills[value]
                    
                self._apply_cell_style(cell, self.data_font, fill, self.center_align if col > 3 else self.left_align)
            
            row += 1

        # Set column widths
        col_widths = {
            1: 8, 2: 15, 3: 10, 4: 12, 5: 12, 6: 35, 7: 15, 8: 8,
            9: 10, 10: 6, 11: 10, 12: 6, 13: 8, 14: 6, 15: 8, 16: 6, 17: 6, 18: 8,
            19: 12, 20: 12, 21: 6, 22: 12, 23: 12, 24: 6, 25: 12, 26: 12, 27: 6, 28: 12, 29: 12, 30: 6,
            31: 8, 32: 10, 33: 10, 34: 12, 35: 15, 36: 20, 37: 10, 38: 8
        }
        for col, width in col_widths.items():
            ws.column_dimensions[get_column_letter(col)].width = width

        # Freeze panes
        ws.freeze_panes = 'A6'

    # Helper methods for TARA analysis
    def _get_attack_vector(self, threat: dict) -> tuple:
        """Get attack vector content and value."""
        vector = threat.get("attack_vector", "").lower() if threat.get("attack_vector") else ""
        if "network" in vector or "remote" in vector or "网络" in vector:
            return ("Network\n网络", 4)
        elif "adjacent" in vector or "相邻" in vector:
            return ("Adjacent\n相邻", 3)
        elif "local" in vector or "本地" in vector:
            return ("Local\n本地", 2)
        else:
            return ("Physical\n物理", 1)

    def _get_attack_complexity(self, threat: dict) -> tuple:
        """Get attack complexity content and value."""
        # Higher impact often means easier attack is more concerning
        impact = threat.get("impact_level", 2)
        if impact >= 4:
            return ("Low\n低", 3)
        elif impact >= 3:
            return ("Medium\n中", 2)
        else:
            return ("High\n高", 1)

    def _get_privileges(self, threat: dict) -> tuple:
        """Get privileges required content and value."""
        threat_type = threat.get("threat_type", "")
        if threat_type in ['E', 'S']:  # Elevation, Spoofing usually need low privileges
            return ("Low\n低", 3)
        elif threat_type in ['T', 'D']:  # Tampering, DoS may need some privileges
            return ("Medium\n中", 2)
        else:
            return ("High\n高", 1)

    def _get_user_interaction(self, threat: dict) -> tuple:
        """Get user interaction requirement."""
        # Most automotive attacks don't require user interaction
        return ("None\n无需", 3)

    def _get_feasibility_level(self, calc: int) -> str:
        """Get feasibility level from calculation."""
        if calc >= 12:
            return "High\n高"
        elif calc >= 8:
            return "Medium\n中"
        else:
            return "Low\n低"

    def _get_impact_safety(self, threat: dict) -> tuple:
        """Get safety impact."""
        safety = threat.get("safety_impact", 0)
        if safety >= 4:
            return ("S3-Severe\n严重", "危及生命", 3)
        elif safety >= 3:
            return ("S2-Moderate\n中度", "可能受伤", 2)
        elif safety >= 1:
            return ("S1-Minor\n轻微", "不适或轻伤", 1)
        else:
            return ("S0-No Impact\n无影响", "非安全相关", 0)

    def _get_impact_financial(self, threat: dict) -> tuple:
        """Get financial impact."""
        financial = threat.get("financial_impact", 2)
        if financial >= 4:
            return ("S3-Severe\n严重", "重大经济损失", 3)
        elif financial >= 3:
            return ("S2-Moderate\n中度", "潜在经济损失", 2)
        elif financial >= 1:
            return ("S1-Minor\n轻微", "轻微损失", 1)
        else:
            return ("S0-No Impact\n无影响", "无影响", 0)

    def _get_impact_operational(self, threat: dict) -> tuple:
        """Get operational impact."""
        operational = threat.get("operational_impact", 2)
        if operational >= 4:
            return ("S3-Severe\n严重", "功能完全丧失", 3)
        elif operational >= 3:
            return ("S2-Moderate\n中度", "服务降级", 2)
        elif operational >= 1:
            return ("S1-Minor\n轻微", "轻微影响", 1)
        else:
            return ("S0-No Impact\n无影响", "无影响", 0)

    def _get_impact_privacy(self, threat: dict) -> tuple:
        """Get privacy impact."""
        privacy = threat.get("privacy_impact", 2)
        if privacy >= 4:
            return ("S3-Severe\n严重", "严重隐私泄露", 3)
        elif privacy >= 3:
            return ("S2-Moderate\n中度", "隐私泄露", 2)
        elif privacy >= 1:
            return ("S1-Minor\n轻微", "轻微泄露", 1)
        else:
            return ("S0-No Impact\n无影响", "无影响", 0)

    def _get_impact_level(self, calc: int) -> str:
        """Get impact level from calculation."""
        if calc >= 3:
            return "Severe\n严重"
        elif calc >= 2:
            return "Moderate\n中等"
        elif calc >= 1:
            return "Minor\n轻微"
        else:
            return "None\n无"

    def _calculate_risk_level(self, feasibility: int, impact: int) -> str:
        """Calculate risk level based on feasibility and impact."""
        risk_score = feasibility + impact * 2
        if risk_score >= 15:
            return "CAL-4"
        elif risk_score >= 10:
            return "CAL-3"
        elif risk_score >= 5:
            return "CAL-2"
        else:
            return "CAL-1"

    def _get_risk_treatment(self, risk_level: str) -> str:
        """Get risk treatment decision based on risk level."""
        treatment_map = {
            "CAL-4": "Reduce\n降低",
            "CAL-3": "Reduce\n降低",
            "CAL-2": "Reduce/Accept\n降低/接受",
            "CAL-1": "Accept\n接受",
        }
        return treatment_map.get(risk_level, "Reduce\n降低")
