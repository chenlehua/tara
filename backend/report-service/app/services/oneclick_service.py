"""
One-click TARA Report Generation Service
=========================================

Service for generating TARA reports from uploaded files in one click.
"""

import asyncio
import csv
import io
import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session
from tara_shared.constants import ReportStatus
from tara_shared.models import Asset, Project, Report, ThreatRisk
from tara_shared.utils import get_logger

logger = get_logger(__name__)

# File storage path
UPLOAD_DIR = Path("/tmp/tara_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class OneClickGenerateService:
    """Service for one-click TARA report generation."""

    def __init__(self, db: Session):
        self.db = db

    async def start_generation(
        self,
        task_id: str,
        files: List[UploadFile],
        template: str,
        prompt: str,
        project_name: str,
        task_storage: dict,
    ) -> Dict[str, Any]:
        """
        Initialize report generation process.

        Returns project_id, report_id, and file_paths.
        """
        # Create project directory
        project_dir = UPLOAD_DIR / task_id
        project_dir.mkdir(parents=True, exist_ok=True)

        # Save uploaded files
        file_paths = []
        for file in files:
            file_path = project_dir / file.filename
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            file_paths.append(str(file_path))
            logger.info(f"Saved file: {file_path}")

        # Create project in database
        project = Project(
            name=project_name or f"一键生成项目_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description=f"通过一键生成创建的项目，任务ID: {task_id}",
            vehicle_type="通用",
            standard="ISO/SAE 21434",
            status=1,  # in_progress
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        logger.info(f"Created project: {project.id}")

        # Create report in database
        report = Report(
            project_id=project.id,
            name=f"TARA分析报告_{datetime.now().strftime('%Y-%m-%d')}",
            report_type="tara",
            description=f"一键生成的TARA分析报告，模板: {template}",
            template=template,
            status=ReportStatus.GENERATING.value,
            progress=0,
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        logger.info(f"Created report: {report.id}")

        return {
            "project_id": project.id,
            "report_id": report.id,
            "file_paths": file_paths,
        }

    async def run_generation(
        self,
        task_id: str,
        project_id: int,
        report_id: int,
        file_paths: List[str],
        template: str,
        prompt: str,
        task_storage: dict,
    ) -> None:
        """
        Run the full TARA report generation process.
        """
        try:
            # Step 1: Parse files
            await self._update_progress(task_storage, task_id, 0, 10, "解析文件")
            parsed_data = await self._parse_files(file_paths)
            await asyncio.sleep(1)  # Simulate processing time

            # Step 2: Identify assets
            await self._update_progress(task_storage, task_id, 1, 30, "识别资产")
            assets = await self._identify_assets(parsed_data)
            # Save assets to database
            db_asset_ids = await self._save_assets_to_db(project_id, assets)
            await asyncio.sleep(1.5)

            # Step 3: Threat analysis
            await self._update_progress(task_storage, task_id, 2, 50, "威胁分析")
            threats = await self._analyze_threats(assets, template, prompt)
            # Save threats to database
            await self._save_threats_to_db(project_id, threats, db_asset_ids)
            await asyncio.sleep(2)

            # Step 4: Risk assessment
            await self._update_progress(task_storage, task_id, 3, 75, "风险评估")
            risk_assessment = await self._assess_risks(threats)
            await asyncio.sleep(1.5)

            # Step 5: Generate report
            await self._update_progress(task_storage, task_id, 4, 90, "生成报告")
            report_data = await self._generate_report(
                project_id=project_id,
                report_id=report_id,
                assets=assets,
                threats=threats,
                risk_assessment=risk_assessment,
                template=template,
            )
            await asyncio.sleep(1)

            # Save report data to database
            await self._save_report_to_db(report_id, report_data, risk_assessment)

            # Update project status to completed
            await self._update_project_status(project_id, 2)  # 2 = completed

            # Complete
            task_storage[task_id]["status"] = "completed"
            task_storage[task_id]["progress"] = 100
            task_storage[task_id]["current_step"] = "完成"
            task_storage[task_id]["result"] = report_data
            for step in task_storage[task_id]["steps"]:
                step["completed"] = True
                step["active"] = False

            logger.info(f"Report generation completed for task {task_id}")

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            task_storage[task_id]["status"] = "failed"
            task_storage[task_id]["error"] = str(e)
            # Update report status to failed
            await self._update_report_status(report_id, ReportStatus.FAILED.value, str(e))

    async def _update_progress(
        self,
        task_storage: dict,
        task_id: str,
        step_index: int,
        progress: int,
        step_name: str,
    ) -> None:
        """Update task progress."""
        if task_id in task_storage:
            task_storage[task_id]["progress"] = progress
            task_storage[task_id]["current_step"] = step_name

            for i, step in enumerate(task_storage[task_id]["steps"]):
                if i < step_index:
                    step["completed"] = True
                    step["active"] = False
                elif i == step_index:
                    step["completed"] = False
                    step["active"] = True
                else:
                    step["completed"] = False
                    step["active"] = False

    async def _parse_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Parse uploaded files and extract data."""
        parsed_data = {
            "assets": [],
            "images": [],
            "raw_data": {},
        }

        for file_path in file_paths:
            path = Path(file_path)
            ext = path.suffix.lower()

            try:
                if ext == ".json":
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        parsed_data["raw_data"][path.name] = data
                        if "assets" in data:
                            parsed_data["assets"].extend(data["assets"])

                elif ext == ".csv":
                    with open(file_path, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            parsed_data["assets"].append(self._normalize_asset(row))

                elif ext in [".xlsx", ".xls"]:
                    # In real implementation, use openpyxl or pandas
                    logger.info(f"Excel file parsing: {file_path}")

                elif ext in [".png", ".jpg", ".jpeg", ".svg", ".gif"]:
                    parsed_data["images"].append(file_path)

                elif ext == ".pdf":
                    # In real implementation, use PDF parser
                    logger.info(f"PDF file parsing: {file_path}")

            except Exception as e:
                logger.error(f"Failed to parse file {file_path}: {e}")

        return parsed_data

    def _normalize_asset(self, row: dict) -> dict:
        """Normalize asset data from various formats."""
        # Map common column names
        name_keys = ["资产名称", "name", "Name", "Asset Name", "asset_name"]
        type_keys = ["资产类型", "type", "Type", "Asset Type", "asset_type"]

        asset = {
            "id": str(uuid.uuid4())[:8],
            "name": "",
            "type": "",
            "interfaces": [],
            "security_properties": {},
        }

        for key in name_keys:
            if key in row and row[key]:
                asset["name"] = row[key]
                break

        for key in type_keys:
            if key in row and row[key]:
                asset["type"] = row[key]
                break

        # Extract interfaces
        interface_keys = ["接口类型", "interfaces", "Interfaces"]
        for key in interface_keys:
            if key in row and row[key]:
                interfaces = row[key].split(",")
                asset["interfaces"] = [{"type": i.strip()} for i in interfaces]
                break

        # Extract security properties
        for prop, keys in [
            ("confidentiality", ["机密性", "confidentiality"]),
            ("integrity", ["完整性", "integrity"]),
            ("availability", ["可用性", "availability"]),
        ]:
            for key in keys:
                if key in row and row[key]:
                    asset["security_properties"][prop] = row[key]
                    break

        return asset

    async def _identify_assets(
        self, parsed_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify and classify assets from parsed data."""
        assets = parsed_data.get("assets", [])

        # If no assets found, generate sample assets
        if not assets:
            assets = self._generate_sample_assets()

        # Classify assets and calculate security levels
        for asset in assets:
            asset["security_level"] = self._calculate_security_level(asset)
            asset["attack_surface"] = self._calculate_attack_surface(asset)

        return assets

    def _generate_sample_assets(self) -> List[Dict[str, Any]]:
        """Generate sample assets for demo purposes."""
        return [
            {
                "id": "ASSET-001",
                "name": "整车控制器 (VCU)",
                "type": "ECU",
                "interfaces": [{"type": "CAN"}, {"type": "Ethernet"}],
                "security_properties": {
                    "confidentiality": "high",
                    "integrity": "critical",
                    "availability": "critical",
                },
            },
            {
                "id": "ASSET-002",
                "name": "电池管理系统 (BMS)",
                "type": "ECU",
                "interfaces": [{"type": "CAN"}, {"type": "LIN"}],
                "security_properties": {
                    "confidentiality": "high",
                    "integrity": "critical",
                    "availability": "critical",
                },
            },
            {
                "id": "ASSET-003",
                "name": "智能网关 (CGW)",
                "type": "Gateway",
                "interfaces": [{"type": "CAN"}, {"type": "Ethernet"}, {"type": "LIN"}],
                "security_properties": {
                    "confidentiality": "critical",
                    "integrity": "critical",
                    "availability": "critical",
                },
            },
            {
                "id": "ASSET-004",
                "name": "远程通信单元 (T-Box)",
                "type": "Gateway",
                "interfaces": [
                    {"type": "4G/5G"},
                    {"type": "WiFi"},
                    {"type": "Bluetooth"},
                ],
                "security_properties": {
                    "confidentiality": "critical",
                    "integrity": "critical",
                    "availability": "high",
                },
            },
            {
                "id": "ASSET-005",
                "name": "信息娱乐系统 (IVI)",
                "type": "ECU",
                "interfaces": [
                    {"type": "Ethernet"},
                    {"type": "USB"},
                    {"type": "Bluetooth"},
                ],
                "security_properties": {
                    "confidentiality": "medium",
                    "integrity": "medium",
                    "availability": "low",
                },
            },
        ]

    def _calculate_security_level(self, asset: dict) -> str:
        """Calculate asset security level (CAL)."""
        props = asset.get("security_properties", {})

        levels = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        max_level = 0

        for prop in ["confidentiality", "integrity", "availability"]:
            level = props.get(prop, "low")
            max_level = max(max_level, levels.get(level, 1))

        cal_map = {4: "CAL-4", 3: "CAL-3", 2: "CAL-2", 1: "CAL-1"}
        return cal_map.get(max_level, "CAL-1")

    def _calculate_attack_surface(self, asset: dict) -> int:
        """Calculate attack surface score based on interfaces."""
        interfaces = asset.get("interfaces", [])

        # Interface risk scores
        risk_scores = {
            "4g/5g": 5,
            "wifi": 5,
            "bluetooth": 4,
            "ethernet": 3,
            "can": 2,
            "lin": 1,
            "usb": 3,
        }

        total = 0
        for iface in interfaces:
            iface_type = iface.get("type", "").lower()
            for key, score in risk_scores.items():
                if key in iface_type:
                    total += score
                    break

        return min(total, 10)  # Cap at 10

    async def _analyze_threats(
        self,
        assets: List[Dict[str, Any]],
        template: str,
        prompt: str,
    ) -> List[Dict[str, Any]]:
        """Perform STRIDE-based threat analysis."""
        threats = []
        threat_id = 1

        # STRIDE categories
        stride_categories = [
            ("Spoofing", "身份伪造", "攻击者伪造合法身份访问系统"),
            ("Tampering", "数据篡改", "攻击者修改传输或存储的数据"),
            ("Repudiation", "抵赖", "用户否认执行过某操作"),
            ("Information Disclosure", "信息泄露", "敏感信息被未授权访问"),
            ("Denial of Service", "拒绝服务", "系统资源被耗尽导致服务不可用"),
            ("Elevation of Privilege", "权限提升", "攻击者获取更高权限"),
        ]

        for asset in assets:
            for stride_code, stride_name, stride_desc in stride_categories:
                # Generate threats based on asset type and interfaces
                if self._should_generate_threat(asset, stride_code):
                    threat = {
                        "id": f"THREAT-{threat_id:03d}",
                        "asset_id": asset["id"],
                        "asset_name": asset["name"],
                        "category": stride_code,
                        "category_name": stride_name,
                        "name": f"{asset['name']}的{stride_name}威胁",
                        "description": f"针对{asset['name']}的{stride_desc}",
                        "attack_vector": self._get_attack_vector(asset, stride_code),
                        "likelihood": self._calculate_likelihood(asset, stride_code),
                        "impact": self._calculate_impact(asset, stride_code),
                    }
                    threats.append(threat)
                    threat_id += 1

        return threats

    def _should_generate_threat(self, asset: dict, stride_code: str) -> bool:
        """Determine if a threat should be generated for this asset/STRIDE combo."""
        asset_type = asset.get("type", "").lower()
        interfaces = [i.get("type", "").lower() for i in asset.get("interfaces", [])]

        # Gateway assets are vulnerable to all threats
        if "gateway" in asset_type:
            return True

        # ECUs with external interfaces
        external_interfaces = ["wifi", "bluetooth", "4g", "5g", "usb"]
        has_external = any(
            any(ext in iface for ext in external_interfaces) for iface in interfaces
        )

        if has_external:
            return True

        # Internal threats for all ECUs
        if stride_code in ["Tampering", "Denial of Service"]:
            return True

        return False

    def _get_attack_vector(self, asset: dict, stride_code: str) -> str:
        """Get attack vector description."""
        interfaces = [i.get("type", "") for i in asset.get("interfaces", [])]

        vectors = {
            "Spoofing": f"通过{'/'.join(interfaces[:2])}接口伪造身份",
            "Tampering": f"通过{interfaces[0] if interfaces else 'CAN'}总线注入恶意消息",
            "Repudiation": "缺少足够的日志记录机制",
            "Information Disclosure": f"窃听{interfaces[0] if interfaces else 'CAN'}总线通信",
            "Denial of Service": f"向{interfaces[0] if interfaces else 'CAN'}总线发送大量报文",
            "Elevation of Privilege": "利用软件漏洞获取系统权限",
        }

        return vectors.get(stride_code, "未知攻击向量")

    def _calculate_likelihood(self, asset: dict, stride_code: str) -> dict:
        """Calculate attack likelihood."""
        attack_surface = asset.get("attack_surface", 5)

        # Base scores
        base_scores = {
            "expertise": 3,  # Expert knowledge required
            "equipment": 2,  # Specialized equipment
            "elapsed_time": 3,  # Days to months
            "knowledge": 2,  # Restricted information
            "window": 3,  # Unlimited/easy access
        }

        # Adjust based on attack surface
        if attack_surface >= 7:
            for key in base_scores:
                base_scores[key] = max(1, base_scores[key] - 1)
        elif attack_surface <= 3:
            for key in base_scores:
                base_scores[key] = min(5, base_scores[key] + 1)

        total = sum(base_scores.values())
        likelihood_level = "High" if total <= 10 else "Medium" if total <= 15 else "Low"

        return {
            "factors": base_scores,
            "total": total,
            "level": likelihood_level,
        }

    def _calculate_impact(self, asset: dict, stride_code: str) -> dict:
        """Calculate threat impact."""
        props = asset.get("security_properties", {})

        impact_map = {"critical": 4, "high": 3, "medium": 2, "low": 1}

        safety_impact = 0
        financial_impact = 0
        operational_impact = 0
        privacy_impact = 0

        if stride_code in ["Tampering", "Denial of Service"]:
            safety_impact = impact_map.get(props.get("integrity", "medium"), 2)
            operational_impact = impact_map.get(props.get("availability", "medium"), 2)

        if stride_code in ["Spoofing", "Information Disclosure"]:
            privacy_impact = impact_map.get(props.get("confidentiality", "medium"), 2)
            financial_impact = 2

        if stride_code == "Elevation of Privilege":
            safety_impact = 3
            operational_impact = 3

        total = max(safety_impact, financial_impact, operational_impact, privacy_impact)
        impact_level = (
            "Severe"
            if total >= 4
            else "Major" if total >= 3 else "Moderate" if total >= 2 else "Negligible"
        )

        return {
            "safety": safety_impact,
            "financial": financial_impact,
            "operational": operational_impact,
            "privacy": privacy_impact,
            "total": total,
            "level": impact_level,
        }

    async def _assess_risks(self, threats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform risk assessment on identified threats."""
        risk_matrix = {
            ("High", "Severe"): ("CAL-4", "极高"),
            ("High", "Major"): ("CAL-4", "极高"),
            ("High", "Moderate"): ("CAL-3", "高"),
            ("High", "Negligible"): ("CAL-2", "中"),
            ("Medium", "Severe"): ("CAL-4", "极高"),
            ("Medium", "Major"): ("CAL-3", "高"),
            ("Medium", "Moderate"): ("CAL-2", "中"),
            ("Medium", "Negligible"): ("CAL-1", "低"),
            ("Low", "Severe"): ("CAL-3", "高"),
            ("Low", "Major"): ("CAL-2", "中"),
            ("Low", "Moderate"): ("CAL-1", "低"),
            ("Low", "Negligible"): ("CAL-1", "低"),
        }

        risk_distribution = {
            "CAL-4": 0,
            "CAL-3": 0,
            "CAL-2": 0,
            "CAL-1": 0,
        }

        for threat in threats:
            likelihood = threat["likelihood"]["level"]
            impact = threat["impact"]["level"]

            cal, risk_name = risk_matrix.get((likelihood, impact), ("CAL-2", "中"))

            threat["risk_level"] = cal
            threat["risk_name"] = risk_name
            threat["control_measures"] = self._suggest_controls(threat)

            risk_distribution[cal] += 1

        return {
            "threats": threats,
            "distribution": risk_distribution,
            "summary": {
                "total": len(threats),
                "critical": risk_distribution["CAL-4"],
                "high": risk_distribution["CAL-3"],
                "medium": risk_distribution["CAL-2"],
                "low": risk_distribution["CAL-1"],
            },
        }

    def _suggest_controls(self, threat: dict) -> List[Dict[str, str]]:
        """Suggest control measures for a threat."""
        controls = []
        category = threat.get("category", "")

        control_suggestions = {
            "Spoofing": [
                {"name": "强身份认证", "description": "实施多因素认证机制"},
                {"name": "数字证书", "description": "使用PKI证书验证身份"},
            ],
            "Tampering": [
                {"name": "消息认证码", "description": "使用MAC验证消息完整性"},
                {"name": "安全启动", "description": "验证软件完整性"},
            ],
            "Repudiation": [
                {"name": "审计日志", "description": "记录所有关键操作"},
                {"name": "时间戳服务", "description": "为日志添加可信时间戳"},
            ],
            "Information Disclosure": [
                {"name": "数据加密", "description": "加密敏感数据传输和存储"},
                {"name": "访问控制", "description": "实施最小权限原则"},
            ],
            "Denial of Service": [
                {"name": "速率限制", "description": "限制请求频率"},
                {"name": "冗余设计", "description": "实施故障转移机制"},
            ],
            "Elevation of Privilege": [
                {"name": "权限隔离", "description": "实施最小权限原则"},
                {"name": "安全编码", "description": "防止缓冲区溢出等漏洞"},
            ],
        }

        controls = control_suggestions.get(
            category,
            [
                {"name": "安全审计", "description": "定期进行安全评估"},
            ],
        )

        return controls

    async def _generate_report(
        self,
        project_id: int,
        report_id: int,
        assets: List[Dict[str, Any]],
        threats: List[Dict[str, Any]],
        risk_assessment: Dict[str, Any],
        template: str,
    ) -> Dict[str, Any]:
        """Generate final report data."""
        summary = risk_assessment.get("summary", {})

        return {
            "report_id": report_id,
            "project_id": project_id,
            "report_name": f"TARA分析报告_{datetime.now().strftime('%Y-%m-%d')}",
            "template": template,
            "generated_at": datetime.now().isoformat(),
            "statistics": {
                "assets_count": len(assets),
                "threats_count": summary.get("total", 0),
                "high_risk_count": summary.get("critical", 0) + summary.get("high", 0),
                "measures_count": sum(
                    len(t.get("control_measures", [])) for t in threats
                ),
            },
            "assets": assets,
            "threats": risk_assessment.get("threats", []),
            "risk_distribution": risk_assessment.get("distribution", {}),
            "download_urls": {
                "pdf": f"/api/v1/reports/{report_id}/download?format=pdf",
                "docx": f"/api/v1/reports/{report_id}/download?format=docx",
            },
        }

    async def _save_report_to_db(
        self,
        report_id: int,
        report_data: Dict[str, Any],
        risk_assessment: Dict[str, Any],
    ) -> None:
        """Save generated report data to database."""
        try:
            report = self.db.query(Report).filter(Report.id == report_id).first()
            if report:
                report.status = ReportStatus.COMPLETED.value
                report.progress = 100
                report.statistics = report_data.get("statistics", {})
                report.content = {
                    "assets": report_data.get("assets", []),
                    "threats": report_data.get("threats", []),
                    "risk_distribution": report_data.get("risk_distribution", {}),
                    "generated_at": report_data.get("generated_at"),
                }
                self.db.commit()
                logger.info(f"Report {report_id} saved to database")
        except Exception as e:
            logger.error(f"Failed to save report to database: {e}")
            self.db.rollback()

    async def _update_report_status(
        self,
        report_id: int,
        status: int,
        error_message: Optional[str] = None,
    ) -> None:
        """Update report status in database."""
        try:
            report = self.db.query(Report).filter(Report.id == report_id).first()
            if report:
                report.status = status
                if error_message:
                    report.error_message = error_message
                self.db.commit()
        except Exception as e:
            logger.error(f"Failed to update report status: {e}")
            self.db.rollback()

    async def _save_assets_to_db(
        self,
        project_id: int,
        assets: List[Dict[str, Any]],
    ) -> Dict[str, int]:
        """Save identified assets to database.

        Returns a mapping of asset id (string) to database id (int).
        """
        asset_id_map = {}
        try:
            for asset_data in assets:
                # Map security properties to security_attrs format
                security_props = asset_data.get("security_properties", {})
                security_attrs = {
                    "confidentiality": security_props.get("confidentiality", "medium"),
                    "integrity": security_props.get("integrity", "medium"),
                    "availability": security_props.get("availability", "medium"),
                }

                # Determine criticality from security level
                security_level = asset_data.get("security_level", "CAL-2")
                criticality_map = {
                    "CAL-4": "critical",
                    "CAL-3": "high",
                    "CAL-2": "medium",
                    "CAL-1": "low",
                }
                criticality = criticality_map.get(security_level, "medium")

                asset = Asset(
                    project_id=project_id,
                    name=asset_data.get("name", "Unknown Asset"),
                    asset_type=asset_data.get("type", "ECU"),
                    category=self._get_asset_category(asset_data.get("type", "ECU")),
                    description=asset_data.get("description", ""),
                    interfaces=asset_data.get("interfaces", []),
                    security_attrs=security_attrs,
                    criticality=criticality,
                    source="oneclick_generated",
                )
                self.db.add(asset)
                self.db.flush()  # Get the ID without committing

                # Map the original asset id to database id
                original_id = asset_data.get("id", str(uuid.uuid4())[:8])
                asset_id_map[original_id] = asset.id
                # Also store the db id in the asset data for later use
                asset_data["db_id"] = asset.id

            self.db.commit()
            logger.info(f"Saved {len(assets)} assets to database for project {project_id}")

        except Exception as e:
            logger.error(f"Failed to save assets to database: {e}")
            self.db.rollback()

        return asset_id_map

    def _get_asset_category(self, asset_type: str) -> str:
        """Get asset category from asset type."""
        type_lower = asset_type.lower()
        if "gateway" in type_lower:
            return "gateway"
        elif "ecu" in type_lower:
            return "ecu"
        elif "sensor" in type_lower:
            return "sensor"
        elif "actuator" in type_lower:
            return "actuator"
        else:
            return "general"

    async def _save_threats_to_db(
        self,
        project_id: int,
        threats: List[Dict[str, Any]],
        asset_id_map: Dict[str, int],
    ) -> None:
        """Save analyzed threats to database."""
        try:
            for threat_data in threats:
                # Get the database asset id
                original_asset_id = threat_data.get("asset_id", "")
                db_asset_id = asset_id_map.get(original_asset_id)

                if not db_asset_id:
                    # Try to find by name match
                    asset_name = threat_data.get("asset_name", "")
                    for orig_id, db_id in asset_id_map.items():
                        if asset_name in orig_id or orig_id in asset_name:
                            db_asset_id = db_id
                            break

                # Get impact level from the impact data
                impact_data = threat_data.get("impact", {})
                impact_level = impact_data.get("total", 2) if isinstance(impact_data, dict) else 2

                # Get likelihood
                likelihood_data = threat_data.get("likelihood", {})
                likelihood = 2  # default medium
                if isinstance(likelihood_data, dict):
                    likelihood_level = likelihood_data.get("level", "Medium")
                    likelihood_map = {"High": 3, "Medium": 2, "Low": 1}
                    likelihood = likelihood_map.get(likelihood_level, 2)

                # Map STRIDE category to threat type code
                category = threat_data.get("category", "")
                threat_type_map = {
                    "Spoofing": "S",
                    "Tampering": "T",
                    "Repudiation": "R",
                    "Information Disclosure": "I",
                    "Denial of Service": "D",
                    "Elevation of Privilege": "E",
                }
                threat_type = threat_type_map.get(category, "T")

                # Calculate risk level
                risk_level = self._calculate_risk_level(likelihood, impact_level)

                threat = ThreatRisk(
                    project_id=project_id,
                    asset_id=db_asset_id,
                    threat_name=threat_data.get("name", "Unknown Threat"),
                    threat_type=threat_type,
                    threat_desc=threat_data.get("description", ""),
                    attack_vector=threat_data.get("attack_vector", ""),
                    likelihood=likelihood,
                    safety_impact=impact_data.get("safety", 0) if isinstance(impact_data, dict) else 0,
                    financial_impact=impact_data.get("financial", 0) if isinstance(impact_data, dict) else 0,
                    operational_impact=impact_data.get("operational", 0) if isinstance(impact_data, dict) else 0,
                    privacy_impact=impact_data.get("privacy", 0) if isinstance(impact_data, dict) else 0,
                    impact_level=impact_level,
                    risk_level=risk_level,
                    source="oneclick_generated",
                )
                self.db.add(threat)

                # Store the db id for later use
                self.db.flush()
                threat_data["db_id"] = threat.id

            self.db.commit()
            logger.info(f"Saved {len(threats)} threats to database for project {project_id}")

        except Exception as e:
            logger.error(f"Failed to save threats to database: {e}")
            self.db.rollback()

    def _calculate_risk_level(self, likelihood: int, impact: int) -> str:
        """Calculate risk level from likelihood and impact."""
        # Risk matrix based on ISO 21434
        risk_matrix = {
            (3, 4): "CAL-4",
            (3, 3): "CAL-4",
            (3, 2): "CAL-3",
            (3, 1): "CAL-2",
            (2, 4): "CAL-4",
            (2, 3): "CAL-3",
            (2, 2): "CAL-2",
            (2, 1): "CAL-1",
            (1, 4): "CAL-3",
            (1, 3): "CAL-2",
            (1, 2): "CAL-1",
            (1, 1): "CAL-1",
        }
        return risk_matrix.get((likelihood, impact), "CAL-2")

    async def _update_project_status(self, project_id: int, status: int) -> None:
        """Update project status in database."""
        try:
            project = self.db.query(Project).filter(Project.id == project_id).first()
            if project:
                project.status = status
                self.db.commit()
                logger.info(f"Updated project {project_id} status to {status}")
        except Exception as e:
            logger.error(f"Failed to update project status: {e}")
            self.db.rollback()
