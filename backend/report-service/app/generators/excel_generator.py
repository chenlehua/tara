"""Excel report generator."""

import io
from datetime import datetime
from typing import Any, Dict, List

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from tara_shared.utils import get_logger

logger = get_logger(__name__)


class ExcelGenerator:
    """Generate Excel reports."""

    def __init__(self):
        # Define styles
        self.header_fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
        self.header_font = Font(color="FFFFFF", bold=True, size=11)
        self.alt_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        self.border = Border(
            left=Side(style='thin', color='E2E8F0'),
            right=Side(style='thin', color='E2E8F0'),
            top=Side(style='thin', color='E2E8F0'),
            bottom=Side(style='thin', color='E2E8F0')
        )
        self.center_align = Alignment(horizontal='center', vertical='center')
        self.left_align = Alignment(horizontal='left', vertical='center', wrap_text=True)

    def _style_header_row(self, ws, row: int, col_count: int):
        """Apply header style to a row."""
        for col in range(1, col_count + 1):
            cell = ws.cell(row=row, column=col)
            cell.fill = self.header_fill
            cell.font = self.header_font
            cell.border = self.border
            cell.alignment = self.center_align

    def _style_data_row(self, ws, row: int, col_count: int, is_alt: bool = False):
        """Apply data row style."""
        for col in range(1, col_count + 1):
            cell = ws.cell(row=row, column=col)
            if is_alt:
                cell.fill = self.alt_fill
            cell.border = self.border
            cell.alignment = self.left_align

    def _auto_adjust_columns(self, ws, col_widths: Dict[int, int]):
        """Adjust column widths."""
        for col, width in col_widths.items():
            ws.column_dimensions[get_column_letter(col)].width = width

    async def generate(
        self,
        data: dict,
        template: str = "iso21434",
        sections: list[str] = None,
    ) -> io.BytesIO:
        """Generate Excel report."""
        wb = Workbook()
        
        # Get content
        content = data.get("content", {})
        project = content.get("project", data.get("project", {}))
        assets = content.get("assets", [])
        threats = content.get("threats", [])
        measures = content.get("control_measures", [])
        risk_dist = content.get("risk_distribution", {})

        # Create Summary sheet
        self._create_summary_sheet(wb, project, assets, threats, measures, risk_dist)
        
        # Create Assets sheet
        if assets:
            self._create_assets_sheet(wb, assets)
        
        # Create Threats sheet
        if threats:
            self._create_threats_sheet(wb, threats)
        
        # Create Measures sheet
        if measures:
            self._create_measures_sheet(wb, measures)
        
        # Create Risk Distribution sheet
        if risk_dist:
            self._create_risk_sheet(wb, risk_dist)

        # Save to buffer
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        return buffer

    def _create_summary_sheet(
        self, 
        wb: Workbook, 
        project: dict, 
        assets: list, 
        threats: list, 
        measures: list,
        risk_dist: dict
    ):
        """Create summary sheet."""
        ws = wb.active
        ws.title = "Summary"

        # Title
        ws['A1'] = "TARA Analysis Report - Summary"
        ws['A1'].font = Font(bold=True, size=16)
        ws.merge_cells('A1:D1')

        # Project Info
        row = 3
        ws.cell(row=row, column=1, value="Project Information").font = Font(bold=True, size=12)
        row += 1
        
        info = [
            ("Project Name", project.get("name", "N/A")),
            ("Vehicle Type", project.get("vehicle_type", "N/A")),
            ("Standard", project.get("standard", "ISO/SAE 21434")),
            ("Generated", datetime.now().strftime("%Y-%m-%d %H:%M")),
        ]
        
        for label, value in info:
            ws.cell(row=row, column=1, value=label).font = Font(bold=True)
            ws.cell(row=row, column=2, value=value)
            row += 1

        # Statistics
        row += 1
        ws.cell(row=row, column=1, value="Statistics").font = Font(bold=True, size=12)
        row += 1

        high_risk = risk_dist.get("CAL-4", 0) + risk_dist.get("CAL-3", 0)
        stats = [
            ("Total Assets", len(assets)),
            ("Total Threats", len(threats)),
            ("High Risk Items (CAL-3/4)", high_risk),
            ("Control Measures", len(measures)),
        ]

        for label, value in stats:
            ws.cell(row=row, column=1, value=label).font = Font(bold=True)
            ws.cell(row=row, column=2, value=value)
            row += 1

        # Risk Distribution
        row += 1
        ws.cell(row=row, column=1, value="Risk Distribution").font = Font(bold=True, size=12)
        row += 1

        for level in ["CAL-4", "CAL-3", "CAL-2", "CAL-1"]:
            ws.cell(row=row, column=1, value=level).font = Font(bold=True)
            ws.cell(row=row, column=2, value=risk_dist.get(level, 0))
            row += 1

        # Adjust column widths
        self._auto_adjust_columns(ws, {1: 30, 2: 40, 3: 20, 4: 20})

    def _create_assets_sheet(self, wb: Workbook, assets: list):
        """Create assets sheet."""
        ws = wb.create_sheet("Assets")

        headers = ["ID", "Asset Name", "Type", "Category", "Interfaces", "Security Level", "Description"]
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)
        self._style_header_row(ws, 1, len(headers))

        for row_idx, asset in enumerate(assets, 2):
            interfaces = asset.get("interfaces", [])
            iface_str = ", ".join([
                i.get("type", str(i)) if isinstance(i, dict) else str(i) 
                for i in interfaces
            ])
            
            values = [
                asset.get("id", row_idx - 1),
                asset.get("name", "N/A"),
                asset.get("type", asset.get("asset_type", "N/A")),
                asset.get("category", "-"),
                iface_str or "-",
                asset.get("security_level", asset.get("criticality", "CAL-2")),
                asset.get("description", "-"),
            ]
            
            for col, value in enumerate(values, 1):
                ws.cell(row=row_idx, column=col, value=str(value) if value else "-")
            
            self._style_data_row(ws, row_idx, len(headers), row_idx % 2 == 0)

        # Adjust column widths
        self._auto_adjust_columns(ws, {1: 12, 2: 35, 3: 15, 4: 15, 5: 30, 6: 15, 7: 50})

    def _create_threats_sheet(self, wb: Workbook, threats: list):
        """Create threats sheet."""
        ws = wb.create_sheet("Threats")

        headers = ["ID", "Threat Name", "STRIDE Category", "Attack Vector", "Risk Level", "Impact", "Description"]
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)
        self._style_header_row(ws, 1, len(headers))

        for row_idx, threat in enumerate(threats, 2):
            values = [
                threat.get("id", f"THR-{row_idx - 1:03d}"),
                threat.get("name", "N/A"),
                threat.get("category_name", threat.get("category", "N/A")),
                threat.get("attack_vector", "-"),
                threat.get("risk_level", "CAL-2"),
                threat.get("impact_level", "-"),
                threat.get("description", "-"),
            ]
            
            for col, value in enumerate(values, 1):
                ws.cell(row=row_idx, column=col, value=str(value) if value else "-")
            
            self._style_data_row(ws, row_idx, len(headers), row_idx % 2 == 0)

        # Adjust column widths
        self._auto_adjust_columns(ws, {1: 15, 2: 40, 3: 20, 4: 40, 5: 12, 6: 10, 7: 50})

    def _create_measures_sheet(self, wb: Workbook, measures: list):
        """Create control measures sheet."""
        ws = wb.create_sheet("Control Measures")

        headers = ["ID", "Measure Name", "Type", "Category", "Effectiveness", "ISO 21434 Ref", "Implementation"]
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)
        self._style_header_row(ws, 1, len(headers))

        for row_idx, measure in enumerate(measures, 2):
            eff = measure.get("effectiveness", "medium")
            eff_text = {"high": "High", "medium": "Medium", "low": "Low"}.get(eff, "Medium")
            
            values = [
                measure.get("id", row_idx - 1),
                measure.get("name", "N/A"),
                measure.get("control_type", "preventive"),
                measure.get("category", "-"),
                eff_text,
                measure.get("iso21434_ref", "-"),
                measure.get("implementation", measure.get("description", "-")),
            ]
            
            for col, value in enumerate(values, 1):
                ws.cell(row=row_idx, column=col, value=str(value) if value else "-")
            
            self._style_data_row(ws, row_idx, len(headers), row_idx % 2 == 0)

        # Adjust column widths
        self._auto_adjust_columns(ws, {1: 10, 2: 40, 3: 15, 4: 15, 5: 15, 6: 20, 7: 50})

    def _create_risk_sheet(self, wb: Workbook, risk_dist: dict):
        """Create risk distribution sheet."""
        ws = wb.create_sheet("Risk Distribution")

        headers = ["Risk Level", "Count", "Percentage", "Action Required"]
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)
        self._style_header_row(ws, 1, len(headers))

        total = sum(risk_dist.values()) or 1
        
        risk_data = [
            ("CAL-4 (Critical)", risk_dist.get("CAL-4", 0), "Immediate action required"),
            ("CAL-3 (High)", risk_dist.get("CAL-3", 0), "Priority treatment needed"),
            ("CAL-2 (Medium)", risk_dist.get("CAL-2", 0), "Planned treatment"),
            ("CAL-1 (Low)", risk_dist.get("CAL-1", 0), "Acceptable risk"),
        ]

        for row_idx, (level, count, action) in enumerate(risk_data, 2):
            pct = f"{(count / total * 100):.1f}%"
            values = [level, count, pct, action]
            
            for col, value in enumerate(values, 1):
                ws.cell(row=row_idx, column=col, value=value)
            
            self._style_data_row(ws, row_idx, len(headers), row_idx % 2 == 0)

        # Total row
        row = len(risk_data) + 2
        ws.cell(row=row, column=1, value="Total").font = Font(bold=True)
        ws.cell(row=row, column=2, value=total).font = Font(bold=True)
        ws.cell(row=row, column=3, value="100%").font = Font(bold=True)

        # Adjust column widths
        self._auto_adjust_columns(ws, {1: 20, 2: 12, 3: 15, 4: 30})
