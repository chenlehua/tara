"""Excel report generator - ISO 21434 TARA Format.

This generator creates Excel reports that match the MY25 EV平台中控主机_TARA分析报告.xlsx format,
including proper formulas for auto-calculated columns.
"""

import io
from datetime import datetime
from typing import Any, Dict, List, Optional

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

try:
    from app.common.utils import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class ExcelGenerator:
    """Generate Excel reports in ISO 21434 TARA format.
    
    This generator matches the format of MY25 EV平台中控主机_TARA分析报告.xlsx,
    including proper Excel formulas for auto-calculated columns.
    """

    def __init__(self):
        """Initialize styles matching the sample Excel format."""
        # Title style (Row 1)
        self.title_font = Font(bold=True, size=14, color="2F5496")
        self.title_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
        
        # Header group style (Row 3)
        self.header_font = Font(bold=True, size=10, color="FFFFFF")
        self.header_fill = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
        
        # Sub-header style (Row 4)
        self.subheader_font = Font(bold=True, size=10)
        self.subheader_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        
        # Detail header style (Row 5)
        self.detail_font = Font(bold=True, size=9)
        self.detail_fill = PatternFill(start_color="8EA9DB", end_color="8EA9DB", fill_type="solid")
        
        # Data font
        self.data_font = Font(size=9)
        
        # Border
        self.border = Border(
            left=Side(style='thin', color='000000'),
            right=Side(style='thin', color='000000'),
            top=Side(style='thin', color='000000'),
            bottom=Side(style='thin', color='000000')
        )
        
        # Alignments
        self.center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
        self.left_align = Alignment(horizontal='left', vertical='center', wrap_text=True)

        # Risk level colors (for conditional formatting)
        self.risk_fills = {
            'Critical': PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid"),
            'High': PatternFill(start_color="FFC000", end_color="FFC000", fill_type="solid"),
            'Medium': PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid"),
            'Low': PatternFill(start_color="92D050", end_color="92D050", fill_type="solid"),
            'QM': PatternFill(start_color="00B050", end_color="00B050", fill_type="solid"),
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
        """Generate Excel report in TARA format.
        
        Args:
            data: Dictionary containing project, assets, threats, and control_measures
            template: Template type (default: iso21434)
            sections: Optional list of sections to include
            
        Returns:
            BytesIO buffer containing the Excel file
        """
        wb = Workbook()
        
        # Get content
        content = data.get("content", data)
        project = content.get("project", data.get("project", {}))
        assets = content.get("assets", [])
        threats = content.get("threats", [])
        measures = content.get("control_measures", [])

        # Create sheets in order
        self._create_cover_sheet(wb, project)
        self._create_definitions_sheet(wb, project)
        self._create_asset_list_sheet(wb, assets, project)
        self._create_data_flow_sheet(wb, assets, project)
        self._create_attack_tree_sheet(wb, threats, project)
        self._create_tara_results_sheet(wb, assets, threats, measures, project)

        # Remove default sheet
        if 'Sheet' in wb.sheetnames:
            del wb['Sheet']

        # Save to buffer
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        return buffer

    def _create_cover_sheet(self, wb: Workbook, project: dict):
        """Create 0. 封面 Front Cover sheet."""
        ws = wb.create_sheet("0. 封面 Front Cover", 0)
        
        project_name = project.get("name", "TARA分析项目")
        platform_name = project.get("platform_name", project_name)
        
        # Data classification
        ws.cell(row=4, column=6, value="数据等级：秘密\nData level: Confidential")
        ws.cell(row=5, column=6, value=f"编号：{project.get('doc_number', 'IPC0011_JF_A30-44003')}\nNumber: {project.get('doc_number', 'IPC0011_JF_A30-44003')}")
        ws.cell(row=6, column=6, value=f"版本：{project.get('version', '1.0')}\nVersion：{project.get('version', '1.0')}")
        
        # Title
        title_cell = ws.cell(row=7, column=1, value="威胁分析和风险评估报告\nThreat Analysis And Risk Assessment Report")
        title_cell.font = Font(bold=True, size=24)
        title_cell.alignment = self.center_align
        ws.merge_cells(start_row=7, start_column=1, end_row=7, end_column=7)
        
        # Platform subtitle
        subtitle_cell = ws.cell(row=8, column=5, value=f"——{platform_name}")
        subtitle_cell.font = Font(size=16)
        
        # Author/Date info
        ws.cell(row=9, column=1, value="编制/日期：\nAuthor/Date")
        ws.cell(row=9, column=3, value=project.get("author_date", datetime.now().strftime("%Y.%m")))
        
        ws.cell(row=10, column=1, value="审核/日期：\nReview/Date")
        ws.cell(row=10, column=3, value=project.get("review_date", ""))
        
        ws.cell(row=11, column=1, value="会签/日期：\nSignature/Date")
        ws.cell(row=11, column=3, value=project.get("signature_date", ""))
        
        ws.cell(row=12, column=1, value="批准/日期：\nApprove/Date")
        ws.cell(row=12, column=3, value=project.get("approve_date", ""))
        
        # Set column widths
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['F'].width = 50

    def _create_definitions_sheet(self, wb: Workbook, project: dict):
        """Create 1-相关定义 sheet with definitions."""
        ws = wb.create_sheet("1-相关定义", 1)

        project_name = project.get("name", "TARA分析项目")
        
        # Title
        title_cell = ws.cell(row=1, column=1, value=f"{project_name} TARA分析报告 - 相关定义")
        title_cell.font = Font(bold=True, size=14, color="2F5496")
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=6)
        
        # Section 1: Functional Description
        row = 3
        ws.cell(row=row, column=1, value="1. 功能描述 Functional Description").font = Font(bold=True, size=12)
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
        
        row = 4
        func_desc = project.get("description", 
            "车载信息娱乐系统(In-Vehicle Infotainment, IVI)是一种集成多媒体娱乐、导航、车辆信息显示、通信和车辆控制功能于一体的车载电子系统。")
        ws.cell(row=row, column=1, value=func_desc)
        ws.merge_cells(start_row=row, start_column=1, end_row=row+2, end_column=6)
        ws.cell(row=row, column=1).alignment = Alignment(wrap_text=True, vertical='top')
        
        # Section 2: Item Boundary Diagram
        row = 12
        ws.cell(row=row, column=1, value="2. 项目边界图 Item Boundary Diagram").font = Font(bold=True, size=12)
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
        
        # Section 3: System Architecture Diagram
        row = 40
        ws.cell(row=row, column=1, value="3. 系统架构图 System Architecture Diagram").font = Font(bold=True, size=12)
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
        
        # Section 4: Reference Standards
        row = 70
        ws.cell(row=row, column=1, value="4. 参考标准 Reference Standards").font = Font(bold=True, size=12)
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
        
        row += 1
        standards = [
            "• ISO/SAE 21434:2021 - Road vehicles — Cybersecurity engineering",
            "• UN R155 - Cyber Security Management System",
            "• UN R156 - Software Update Management System",
            "• GB/T XXXXX - 汽车网络安全相关标准",
        ]
        for std in standards:
            ws.cell(row=row, column=2, value=std)
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=6)
            row += 1

        # Adjust column widths
        ws.column_dimensions['A'].width = 20
        for col in range(2, 7):
            ws.column_dimensions[get_column_letter(col)].width = 25

    def _create_asset_list_sheet(self, wb: Workbook, assets: list, project: dict):
        """Create 2-资产列表 sheet."""
        ws = wb.create_sheet("2-资产列表", 2)
        
        project_name = project.get("name", "TARA分析项目")

        # Title
        title_cell = ws.cell(row=1, column=1, value=f"{project_name}- 资产列表 Asset List")
        title_cell.font = Font(bold=True, size=14, color="2F5496")
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=10)

        # Header Group Row 3
        self._merge_and_style(ws, 3, 1, 3, 4, 
                             "Asset Identification 资产识别",
                             self.header_font, self.header_fill)
        self._merge_and_style(ws, 3, 5, 3, 10, 
                             "Cybersecurity Attributes 网络安全属性",
                             self.header_font, self.header_fill)

        # Header Row 4
        headers = [
            ("资产ID\nAsset ID", 10),
            ("资产名称\nAsset Name", 15),
            ("分类\nCategory", 12),
            ("备注\nRemarks", 40),
            ("真实性\nAuthenticity", 12),
            ("完整性\nIntegrity", 12),
            ("不可抵赖性\nNon-repudiation", 14),
            ("机密性\nConfidentiality", 12),
            ("可用性\nAvailability", 12),
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
                asset.get("description", asset.get("remarks", "")),
                "√" if security_attrs.get("authenticity") else "",
                "√" if security_attrs.get("integrity") else "",
                "√" if security_attrs.get("non_repudiation") else "",
                "√" if security_attrs.get("confidentiality") else "",
                "√" if security_attrs.get("availability") else "",
                "√" if security_attrs.get("authorization") else "",
            ]
            
            for col, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_idx, column=col, value=value)
                self._apply_cell_style(cell, self.data_font, None, 
                                      self.center_align if col >= 5 else self.left_align)

    def _create_data_flow_sheet(self, wb: Workbook, assets: list, project: dict):
        """Create 3-数据流图 sheet."""
        ws = wb.create_sheet("3-数据流图", 3)
        
        project_name = project.get("name", "TARA分析项目")

        # Title
        title_cell = ws.cell(row=1, column=1, value=f"{project_name}- 数据流图 Data Flow Diagram")
        title_cell.font = Font(bold=True, size=14, color="2F5496")
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=9)

        # Data flow diagram placeholder
        diagram_text = project.get("data_flow_diagram", """
┌────────────────────────────────────────────────────────────────────────┐
│                              系统边界                                    │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐         │
│  │   外部接口    │ ───► │   核心处理   │ ───► │   内部通信   │         │
│  │ (WiFi/BT/4G) │ ◄─── │   (SOC/MCU)  │ ◄─── │  (CAN/ETH)   │         │
│  └──────────────┘      └──────────────┘      └──────────────┘         │
│         │                     │                     │                  │
│         ▼                     ▼                     ▼                  │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐         │
│  │   数据存储    │      │   安全模块   │      │   车身控制   │         │
│  │  (ROM/RAM)   │      │   (HSM/SE)   │      │   (BCM等)    │         │
│  └──────────────┘      └──────────────┘      └──────────────┘         │
└────────────────────────────────────────────────────────────────────────┘
""")
        ws.cell(row=3, column=1, value=diagram_text)
        ws.merge_cells(start_row=3, start_column=1, end_row=40, end_column=9)
        ws.cell(row=3, column=1).alignment = Alignment(wrap_text=True, vertical='top')
        ws.cell(row=3, column=1).font = Font(name='Courier New', size=10)
        
        # Asset interface table
        row = 43
        ws.cell(row=row, column=1, value="资产接口列表 Asset Interface List").font = Font(bold=True, size=11)
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=9)

        # Adjust column widths
        for col in range(1, 10):
            ws.column_dimensions[get_column_letter(col)].width = 15

    def _create_attack_tree_sheet(self, wb: Workbook, threats: list, project: dict):
        """Create 4-攻击树图 sheet."""
        ws = wb.create_sheet("4-攻击树图", 4)
        
        project_name = project.get("name", "TARA分析项目")

        # Title
        title_cell = ws.cell(row=1, column=1, value=f"{project_name} - 攻击树分析 Attack Tree Analysis")
        title_cell.font = Font(bold=True, size=14, color="2F5496")
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=6)

        # Attack tree examples
        attack_trees = project.get("attack_trees", [
            {
                "name": "攻击树1 Attack Tree 1: 远程入侵IVI系统 Remote Compromise of IVI System",
                "diagram": """
                        ┌────────────────────────────────────┐
                        │     远程入侵IVI系统                  │
                        │   Remote Compromise of IVI         │
                        └───────────────┬────────────────────┘
                                        │
              ┌─────────────────────────┼─────────────────────────┐
              │                         │                         │
      ┌───────┴───────┐         ┌───────┴───────┐         ┌───────┴───────┐
      │  网络攻击入口  │         │  无线接口入口  │         │  云端服务入口  │
      │ Network Entry │         │ Wireless Entry│         │  Cloud Entry  │
      └───────────────┘         └───────────────┘         └───────────────┘
"""
            }
        ])
        
        row = 3
        for tree in attack_trees:
            ws.cell(row=row, column=1, value=tree.get("name", "攻击树")).font = Font(bold=True, size=11)
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
            row += 1
            
            ws.cell(row=row, column=1, value=tree.get("diagram", ""))
            ws.merge_cells(start_row=row, start_column=1, end_row=row+18, end_column=6)
            ws.cell(row=row, column=1).alignment = Alignment(wrap_text=True, vertical='top')
            ws.cell(row=row, column=1).font = Font(name='Courier New', size=9)
            row += 22

        # Adjust column width
        ws.column_dimensions['A'].width = 100

    def _create_tara_results_sheet(self, wb: Workbook, assets: list, threats: list, 
                                   measures: list, project: dict):
        """Create 5-TARA分析结果 sheet - Main analysis results with formulas.
        
        This sheet has 40 columns with proper Excel formulas for auto-calculated fields.
        """
        ws = wb.create_sheet("5-TARA分析结果", 5)
        
        project_name = project.get("name", "TARA分析项目")

        # Row 1: Title
        title_cell = ws.cell(row=1, column=1, value=f"{project_name}_TARA分析结果 TARA Analysis Results")
        title_cell.font = self.title_font
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=40)

        # Row 3: Main header groups
        header_groups = [
            (1, 6, "Asset Identification资产识别"),
            (7, 11, "Threat & Damage Scenario\n威胁&损害场景"),
            (12, 21, "Threat Analysis\n威胁分析"),
            (22, 35, "Impact Analysis\n影响分析"),
            (36, 36, "Risk Assessment\n风险评估"),
            (37, 37, "Risk Treatment\n风险处置"),
            (38, 40, "Risk Mitigation\n风险缓解"),
        ]
        
        for start_col, end_col, title in header_groups:
            self._merge_and_style(ws, 3, start_col, 3, end_col, title,
                                 self.header_font, self.header_fill, self.center_align)

        # Row 4: Sub-headers
        row4_headers = {
            1: ("Asset | ID\n资产ID", 1, 1),
            2: ("Asset Name\n资产名称", 2, 2),
            3: ("细分类", 3, 5),  # Spans 3 columns
            6: ("Category\n分类", 6, 6),
            7: ("Security Attributes\n安全属性", 7, 7),
            8: ("STRIDE Model\nSTRIDE模型", 8, 8),
            9: ("Potential Threat and Damage Scenario\n潜在威胁和损害场景", 9, 9),
            10: ("Attack Path\n攻击路径", 10, 10),
            11: ("来源\n", 11, 11),
            12: ("Attack Vector(V)\n攻击向量", 12, 13),
            14: ("Attack Complexity(C)\n攻击复杂度", 14, 15),
            16: ("Privileges Required(P)\n权限要求", 16, 17),
            18: ("User Interaction(U)\n用户交互", 18, 19),
            20: ("Attack Feasibility\n攻击可行性计算", 20, 21),
            22: ("Safety\n安全", 22, 24),
            25: ("Financial\n经济", 25, 27),
            28: ("Operational\n操作", 28, 30),
            31: ("Privacy & Legislation\n隐私和法律", 31, 33),
            34: ("Impact Level Calculation\n影响等级计算", 34, 35),
            36: ("Risk Level\n风险等级", 36, 36),
            37: ("Risk Treatment Decision\n风险处置决策", 37, 37),
            38: ("Security Goal\n安全目标", 38, 38),
            39: ("Security Requirement\n安全需求", 39, 39),
            40: ("Source来源\n", 40, 40),
        }
        
        for start_col, (title, col_start, col_end) in row4_headers.items():
            if col_start == col_end:
                cell = ws.cell(row=4, column=col_start, value=title)
                self._apply_cell_style(cell, self.subheader_font, self.subheader_fill, self.center_align)
                # Also merge with row 5 for single-column headers that don't have sub-headers
                if col_start in [1, 2, 6, 7, 8, 9, 10, 36, 37, 38, 39]:
                    self._merge_and_style(ws, 4, col_start, 5, col_end, title,
                                         self.subheader_font, self.subheader_fill, self.center_align)
            else:
                self._merge_and_style(ws, 4, col_start, 4, col_end, title,
                                     self.subheader_font, self.subheader_fill, self.center_align)

        # Row 5: Detail headers
        row5_headers = {
            3: "子领域一",
            4: "子领域二",
            5: "子领域三",
            11: "WP29威胁映射",
            12: "Time\n内容",
            13: "Value\n指标值",
            14: "Content\n内容",
            15: "Value\n指标值",
            16: "Level\n等级",
            17: "Value\n指标值",
            18: "Level\n等级",
            19: "Value\n指标值",
            20: "Calculation\n计算值",
            21: "Level\n等级",
            22: "Content\n内容",
            23: "Notes\n注释",
            24: "Value\n指标值",
            25: "Content\n内容",
            26: "Notes\n注释",
            27: "Value\n指标值",
            28: "Content\n内容",
            29: "Notes\n注释",
            30: "Value\n指标值",
            31: "Content\n内容",
            32: "Notes\n注释",
            33: "Value\n指标值",
            34: "Impact Calc\n影响计算",
            35: "Impact Level\n影响等级",
            40: "WP29 Control Mapping",
        }
        
        for col, title in row5_headers.items():
            cell = ws.cell(row=5, column=col, value=title)
            self._apply_cell_style(cell, self.detail_font, self.detail_fill, self.center_align)

        # Fill remaining row 5 cells with borders
        for col in range(1, 41):
            if col not in row5_headers:
                ws.cell(row=5, column=col).border = self.border

        # Prepare measures lookup
        measures_by_threat = {}
        for m in measures:
            tid = m.get("threat_id") or m.get("threat_risk_id")
            if tid:
                if tid not in measures_by_threat:
                    measures_by_threat[tid] = []
                measures_by_threat[tid].append(m)

        # Data rows with formulas
        row = 6
        for threat in threats:
            self._write_tara_data_row(ws, row, threat, assets, measures_by_threat)
            row += 1

        # Set column widths to match sample
        col_widths = {
            1: 8.0, 2: 12.0, 3: 10.0, 4: 13.0, 5: 13.0, 6: 14.9, 7: 27.0, 8: 12.3,
            9: 53.9, 10: 82.3, 11: 10.0, 12: 13.0, 13: 7.6, 14: 10.0, 15: 7.7,
            16: 10.0, 17: 8.0, 18: 10.0, 19: 7.9, 20: 8.0, 21: 10.0, 22: 14.0,
            23: 18.0, 24: 6.0, 25: 14.0, 26: 28.0, 27: 6.0, 28: 14.0, 29: 12.0,
            30: 6.0, 31: 14.0, 32: 23.7, 33: 6.0, 34: 8.0, 35: 10.0, 36: 13.0,
            37: 12.0, 38: 18.0, 39: 25.0, 40: 12.0
        }
        for col, width in col_widths.items():
            ws.column_dimensions[get_column_letter(col)].width = width

        # Freeze panes
        ws.freeze_panes = 'A6'

    def _write_tara_data_row(self, ws, row: int, threat: dict, assets: list, 
                             measures_by_threat: dict):
        """Write a single data row with proper formulas.
        
        Input columns (from threat data):
        - A(1): Asset ID
        - B(2): Asset Name
        - C(3): Category subdivision 1
        - D(4): Category subdivision 2
        - E(5): Category subdivision 3
        - F(6): Category
        - G(7): Security Attributes
        - H(8): STRIDE Model
        - I(9): Threat and Damage Scenario
        - J(10): Attack Path
        - K(11): WP29 Mapping
        - L(12): Attack Vector content
        - N(14): Attack Complexity content
        - P(16): Privileges Required level
        - R(18): User Interaction level
        - V(22): Safety content
        - Y(25): Financial content
        - AB(28): Operational content
        - AE(31): Privacy content
        - AM(39): Security Requirement
        
        Auto-calculated columns (formulas):
        - M(13), O(15), Q(17), S(19): Value columns
        - T(20), U(21): Attack Feasibility
        - W(23), X(24), Z(26), AA(27), AC(29), AD(30), AF(32), AG(33): Impact notes/values
        - AH(34), AI(35): Impact calculation/level
        - AJ(36): Risk Level
        - AK(37): Risk Treatment
        - AL(38): Security Goal
        - AN(40): WP29 Control Mapping
        """
        # Get associated asset
        asset_id = threat.get("asset_id", "")
        asset = next((a for a in assets if a.get("id") == asset_id), {})
        
        # Input columns
        # A(1): Asset ID
        ws.cell(row=row, column=1, value=threat.get("asset_id_str", asset_id or ""))
        
        # B(2): Asset Name
        ws.cell(row=row, column=2, value=threat.get("asset_name", asset.get("name", "")))
        
        # C(3): Category subdivision 1
        ws.cell(row=row, column=3, value=threat.get("category_sub1", asset.get("category_sub1", "")))
        
        # D(4): Category subdivision 2
        ws.cell(row=row, column=4, value=threat.get("category_sub2", asset.get("category_sub2", "")))
        
        # E(5): Category subdivision 3
        ws.cell(row=row, column=5, value=threat.get("category_sub3", asset.get("category_sub3", "")))
        
        # F(6): Category
        ws.cell(row=row, column=6, value=threat.get("category", asset.get("category", "")))
        
        # G(7): Security Attributes
        ws.cell(row=row, column=7, value=threat.get("security_attribute", ""))
        
        # H(8): STRIDE Model
        ws.cell(row=row, column=8, value=threat.get("stride_model", ""))
        
        # I(9): Threat and Damage Scenario
        ws.cell(row=row, column=9, value=threat.get("threat_scenario", threat.get("description", "")))
        
        # J(10): Attack Path
        ws.cell(row=row, column=10, value=threat.get("attack_path", ""))
        
        # K(11): WP29 Mapping
        ws.cell(row=row, column=11, value=threat.get("wp29_mapping", ""))
        
        # L(12): Attack Vector content (Input)
        ws.cell(row=row, column=12, value=threat.get("attack_vector", ""))
        
        # M(13): Attack Vector value (Formula)
        ws.cell(row=row, column=13, 
                value=f'=IF(L{row}="网络",0.85,IF(L{row}="邻居",0.62,IF(L{row}="本地",0.55,IF(L{row}="物理",0.2))))')
        
        # N(14): Attack Complexity content (Input)
        ws.cell(row=row, column=14, value=threat.get("attack_complexity", ""))
        
        # O(15): Attack Complexity value (Formula)
        ws.cell(row=row, column=15, value=f'=IF(N{row}="低",0.77,IF(N{row}="高",0.44))')
        
        # P(16): Privileges Required level (Input)
        ws.cell(row=row, column=16, value=threat.get("privileges_required", ""))
        
        # Q(17): Privileges Required value (Formula)
        ws.cell(row=row, column=17, value=f'=IF(P{row}="无",0.85,IF(P{row}="低",0.62,IF(P{row}="高",0.27)))')
        
        # R(18): User Interaction level (Input)
        ws.cell(row=row, column=18, value=threat.get("user_interaction", ""))
        
        # S(19): User Interaction value (Formula)
        ws.cell(row=row, column=19, value=f'=IF(R{row}="不需要",0.85,IF(R{row}="需要",0.62))')
        
        # T(20): Attack Feasibility Calculation (Formula)
        ws.cell(row=row, column=20, value=f'=8.22*M{row}*O{row}*Q{row}*S{row}')
        
        # U(21): Attack Feasibility Level (Formula)
        ws.cell(row=row, column=21, 
                value=f'=IF(T{row}<=1.05,"很低",IF(T{row}<=1.99,"低",IF(T{row}<=2.95,"中",IF(T{row}<=3.89,"高"))))')
        
        # V(22): Safety content (Input)
        ws.cell(row=row, column=22, value=threat.get("safety_impact", ""))
        
        # W(23): Safety Notes (Formula)
        ws.cell(row=row, column=23, 
                value=f'=IF(V{row}="可忽略不计的","没有受伤",IF(V{row}="中等的","轻度和中度伤害",IF(V{row}="重大的","重伤和生命危险（可能幸存）",IF(V{row}="严重的","威胁生命的伤害（尚不确定生存），致命伤害"))))')
        
        # X(24): Safety Value (Formula)
        ws.cell(row=row, column=24, 
                value=f'=IF(V{row}="可忽略不计的",0,IF(V{row}="中等的",10,IF(V{row}="重大的",100,IF(V{row}="严重的",1000))))')
        
        # Y(25): Financial content (Input)
        ws.cell(row=row, column=25, value=threat.get("financial_impact", ""))
        
        # Z(26): Financial Notes (Formula)
        ws.cell(row=row, column=26, 
                value=f'=IF(Y{row}="可忽略不计的","财务损失不会产生任何影响，可忽略给后果或与利益相关者无关",IF(Y{row}="中等的","经济损失会带来不便的后果，受影响的利益相关者将能够用有限的资源来克服这些后果",IF(Y{row}="重大的","经济损失导致重大后果，受影响的利益相关者将能够克服",IF(Y{row}="严重的","经济损失导致灾难性后果，受影响的利益相关者可能无法克服"))))')
        
        # AA(27): Financial Value (Formula)
        ws.cell(row=row, column=27, 
                value=f'=IF(Y{row}="可忽略不计的",0,IF(Y{row}="中等的","10",IF(Y{row}="重大的",100,IF(Y{row}="严重的",1000))))')
        
        # AB(28): Operational content (Input)
        ws.cell(row=row, column=28, value=threat.get("operational_impact", ""))
        
        # AC(29): Operational Notes (Formula)
        ws.cell(row=row, column=29, 
                value=f'=IF(AB{row}="可忽略不计的","操作损坏不会导致车辆功能或性能下降，也不会导致性能下降",IF(AB{row}="中等的","操作损坏会导致车辆功能或性能的部分下降",IF(AB{row}="重大的","操作损坏导致车辆功能丧失",IF(AB{row}="严重的","操作损坏导致车辆从不希望的运行到无法运行的所有车辆不工作"))))')
        
        # AD(30): Operational Value (Formula)
        ws.cell(row=row, column=30, 
                value=f'=IF(AB{row}="可忽略不计的",0,IF(AB{row}="中等的",1,IF(AB{row}="重大的",10,IF(AB{row}="严重的",100))))')
        
        # AE(31): Privacy content (Input)
        ws.cell(row=row, column=31, value=threat.get("privacy_impact", ""))
        
        # AF(32): Privacy Notes (Formula)
        ws.cell(row=row, column=32, 
                value=f'=IF(AE{row}="可忽略不计的","隐私危害不会产生任何影响,也不会给道路使用者带来不便",IF(AE{row}="中等的","隐私危害给道路使用者带来极大的不便",IF(AE{row}="重大的","隐私危害会严重影响道路使用者",IF(AE{row}="严重的","隐私危害对道路使用者造成重大甚至不可逆转的影响"))))')
        
        # AG(33): Privacy Value (Formula)
        ws.cell(row=row, column=33, 
                value=f'=IF(AE{row}="可忽略不计的",0,IF(AE{row}="中等的",1,IF(AE{row}="重大的",10,IF(AE{row}="严重的",100))))')
        
        # AH(34): Impact Calculation (Formula)
        ws.cell(row=row, column=34, value=f'=SUM(X{row}+AA{row}+AD{row}+AG{row})')
        
        # AI(35): Impact Level (Formula)
        ws.cell(row=row, column=35, 
                value=f'=IF(AH{row}>=1000,"严重的",IF(AH{row}>=100,"重大的",IF(AH{row}>=20,"中等的",IF(AH{row}>=10,"微不足道","无影响"))))')
        
        # AJ(36): Risk Level (Formula - complex matrix)
        risk_formula = f'''=IF(AND(AI{row}="无影响",U{row}="无"),"QM",IF(AND(AI{row}="无影响",U{row}="很低"),"QM",IF(AND(AI{row}="无影响",U{row}="低"),"QM",IF(AND(AI{row}="无影响",U{row}="中"),"QM",IF(AND(AI{row}="无影响",U{row}="高"),"Low",IF(AND(AI{row}="微不足道",U{row}="无"),"QM",IF(AND(AI{row}="微不足道",U{row}="很低"),"Low",IF(AND(AI{row}="微不足道",U{row}="低"),"Low",IF(AND(AI{row}="微不足道",U{row}="中"),"Low",IF(AND(AI{row}="微不足道",U{row}="高"),"Medium",IF(AND(AI{row}="中等的",U{row}="无"),"QM",IF(AND(AI{row}="中等的",U{row}="很低"),"Low",IF(AND(AI{row}="中等的",U{row}="低"),"Medium",IF(AND(AI{row}="中等的",U{row}="中"),"Medium",IF(AND(AI{row}="中等的",U{row}="高"),"High",IF(AND(AI{row}="重大的",U{row}="无"),"QM",IF(AND(AI{row}="重大的",U{row}="很低"),"Low",IF(AND(AI{row}="重大的",U{row}="低"),"Medium",IF(AND(AI{row}="重大的",U{row}="中"),"High",IF(AND(AI{row}="重大的",U{row}="高"),"High",IF(AND(AI{row}="严重的",U{row}="无"),"Low",IF(AND(AI{row}="严重的",U{row}="很低"),"Medium",IF(AND(AI{row}="严重的",U{row}="低"),"High",IF(AND(AI{row}="严重的",U{row}="中"),"High",IF(AND(AI{row}="严重的",U{row}="高"),"Critical")))))))))))))))))))))))))'''
        ws.cell(row=row, column=36, value=risk_formula)
        
        # AK(37): Risk Treatment Decision (Formula)
        ws.cell(row=row, column=37, 
                value=f'=IF(OR(AJ{row}="QM",AJ{row}="Low"),"保留风险",IF(OR(AJ{row}="Medium",AJ{row}="Critical",AJ{row}="High"),"降低风险","保留风险"))')
        
        # AL(38): Security Goal (Formula)
        ws.cell(row=row, column=38, 
                value=f'=IF(AK{row}="保留风险","/",IF(OR(AK{row}="降低风险",AK{row}="转移风险",AK{row}="消除风险"),"应保护"&E{row}&"的"&G{row},"NA"))')
        
        # AM(39): Security Requirement (Input)
        ws.cell(row=row, column=39, value=threat.get("security_requirement", ""))
        
        # AN(40): WP29 Control Mapping (Formula)
        ws.cell(row=row, column=40, 
                value=f'=IF(H{row}="T篡改","M10",IF(H{row}="D拒绝服务","M13",IF(H{row}="I信息泄露","M12"&CHAR(10)&"M24",IF(H{row}="S欺骗","M10"&CHAR(10)&"M11",IF(H{row}="E权限提升","M8"&CHAR(10)&"M9",IF(H{row}="R抵赖","M9"&CHAR(10)&"M10"))))))')
        
        # Apply styles to all cells in this row
        for col in range(1, 41):
            cell = ws.cell(row=row, column=col)
            cell.border = self.border
            cell.font = self.data_font
            cell.alignment = self.center_align if col > 2 else self.left_align
