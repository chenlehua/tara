"""
Report Version Service
======================

Service for managing report versions, including creation, comparison, and rollback.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.common.models import (
    Asset, ControlMeasure, Report, ReportVersion, ReportVersionChange, ThreatRisk
)
from app.common.utils import get_logger
from app.common.utils.exceptions import NotFoundException, ValidationException

logger = get_logger(__name__)


class ReportVersionService:
    """Service for report version management."""

    def __init__(self, db: Session):
        self.db = db

    def create_version(
        self,
        report_id: int,
        is_major: bool = False,
        change_summary: Optional[str] = None,
        change_reason: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> ReportVersion:
        """
        Create a new version for a report.
        
        Args:
            report_id: Report ID
            is_major: Whether this is a major version upgrade (1.x -> 2.0)
            change_summary: Summary of changes
            change_reason: Reason for the change
            created_by: Creator name
        
        Returns:
            Newly created ReportVersion
        """
        report = self.db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise NotFoundException("Report", report_id)

        # Calculate new version number
        latest_version = self._get_latest_version(report_id)
        if latest_version:
            if is_major:
                major = latest_version.major_version + 1
                minor = 0
            else:
                major = latest_version.major_version
                minor = latest_version.minor_version + 1
        else:
            major, minor = 1, 0

        version_number = f"{major}.{minor}"

        # Create snapshot data
        snapshot_data = self._create_snapshot(report)

        # Calculate changes from previous version
        changes = []
        if latest_version and latest_version.snapshot_data:
            changes = self._calculate_changes(
                latest_version.snapshot_data,
                snapshot_data
            )

        # Clear current version flag from all other versions
        self.db.query(ReportVersion).filter(
            ReportVersion.report_id == report_id,
            ReportVersion.is_current == True
        ).update({"is_current": False})

        # Create new version
        new_version = ReportVersion(
            report_id=report_id,
            version_number=version_number,
            major_version=major,
            minor_version=minor,
            content=report.content,
            statistics=report.statistics,
            sections=report.sections,
            snapshot_data=snapshot_data,
            change_summary=change_summary or self._generate_change_summary(changes),
            change_reason=change_reason,
            created_by=created_by or "system",
            status="draft",
            is_current=True,
            is_baseline=False,
        )

        self.db.add(new_version)
        self.db.flush()  # Get the ID

        # Save change records
        for change in changes:
            change_record = ReportVersionChange(
                version_id=new_version.id,
                change_type=change["change_type"],
                entity_type=change["entity_type"],
                entity_id=change.get("entity_id"),
                entity_name=change.get("entity_name"),
                field_name=change.get("field_name"),
                old_value=json.dumps(change.get("old_value")) if change.get("old_value") else None,
                new_value=json.dumps(change.get("new_value")) if change.get("new_value") else None,
            )
            self.db.add(change_record)

        # Update report's version info
        report.version = version_number
        report.current_version_id = new_version.id
        report.version_count = (report.version_count or 0) + 1

        self.db.commit()
        self.db.refresh(new_version)

        logger.info(f"Created version {version_number} for report {report_id}")
        return new_version

    def get_version(
        self,
        report_id: int,
        version_number: str,
    ) -> Optional[ReportVersion]:
        """Get a specific version by version number."""
        return self.db.query(ReportVersion).filter(
            ReportVersion.report_id == report_id,
            ReportVersion.version_number == version_number
        ).first()

    def get_version_by_id(self, version_id: int) -> Optional[ReportVersion]:
        """Get a version by ID."""
        return self.db.query(ReportVersion).filter(
            ReportVersion.id == version_id
        ).first()

    def get_current_version(self, report_id: int) -> Optional[ReportVersion]:
        """Get the current version of a report."""
        return self.db.query(ReportVersion).filter(
            ReportVersion.report_id == report_id,
            ReportVersion.is_current == True
        ).first()

    def get_baseline_version(self, report_id: int) -> Optional[ReportVersion]:
        """Get the baseline version of a report."""
        return self.db.query(ReportVersion).filter(
            ReportVersion.report_id == report_id,
            ReportVersion.is_baseline == True
        ).first()

    def list_versions(
        self,
        report_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[ReportVersion], int]:
        """List all versions for a report."""
        query = self.db.query(ReportVersion).filter(
            ReportVersion.report_id == report_id
        ).order_by(ReportVersion.created_at.desc())

        total = query.count()
        versions = query.offset((page - 1) * page_size).limit(page_size).all()

        return versions, total

    def compare_versions(
        self,
        report_id: int,
        version_a: str,
        version_b: str,
    ) -> Dict[str, Any]:
        """
        Compare two versions and return the differences.
        
        Returns:
            {
                "version_a": "1.0",
                "version_b": "1.1",
                "summary": {"added": 5, "modified": 3, "deleted": 1},
                "changes": [...]
            }
        """
        v_a = self.get_version(report_id, version_a)
        v_b = self.get_version(report_id, version_b)

        if not v_a:
            raise NotFoundException("Version", version_a)
        if not v_b:
            raise NotFoundException("Version", version_b)

        # Calculate changes from v_a to v_b
        changes = self._calculate_changes(
            v_a.snapshot_data or {},
            v_b.snapshot_data or {}
        )

        # Generate summary
        summary = {
            "added": len([c for c in changes if c["change_type"] == "add"]),
            "modified": len([c for c in changes if c["change_type"] == "modify"]),
            "deleted": len([c for c in changes if c["change_type"] == "delete"]),
        }

        # Add descriptions to changes
        for change in changes:
            change["description"] = self._generate_change_description(change)

        return {
            "version_a": version_a,
            "version_b": version_b,
            "summary": summary,
            "changes": changes,
        }

    def rollback_to_version(
        self,
        report_id: int,
        version_number: str,
        created_by: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> ReportVersion:
        """
        Rollback to a specific version.
        
        Creates a new version with content copied from the target version.
        """
        target_version = self.get_version(report_id, version_number)
        if not target_version:
            raise NotFoundException("Version", version_number)

        report = self.db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise NotFoundException("Report", report_id)

        # Restore report content from target version
        report.content = target_version.content
        report.statistics = target_version.statistics
        report.sections = target_version.sections

        self.db.commit()

        # Create new version to record the rollback
        new_version = self.create_version(
            report_id=report_id,
            is_major=False,
            change_summary=f"回滚到版本 {version_number}",
            change_reason=reason or f"Rollback from version {version_number}",
            created_by=created_by,
        )

        logger.info(f"Rolled back report {report_id} to version {version_number}")
        return new_version

    def set_baseline(
        self,
        report_id: int,
        version_number: str,
    ) -> ReportVersion:
        """Set a version as the baseline."""
        version = self.get_version(report_id, version_number)
        if not version:
            raise NotFoundException("Version", version_number)

        # Clear previous baseline
        self.db.query(ReportVersion).filter(
            ReportVersion.report_id == report_id,
            ReportVersion.is_baseline == True
        ).update({"is_baseline": False})

        # Set new baseline
        version.is_baseline = True
        version.status = "approved"

        # Update report's baseline reference
        report = self.db.query(Report).filter(Report.id == report_id).first()
        if report:
            report.baseline_version_id = version.id

        self.db.commit()
        self.db.refresh(version)

        logger.info(f"Set version {version_number} as baseline for report {report_id}")
        return version

    def approve_version(
        self,
        report_id: int,
        version_number: str,
        approved_by: str,
    ) -> ReportVersion:
        """Approve a version."""
        version = self.get_version(report_id, version_number)
        if not version:
            raise NotFoundException("Version", version_number)

        version.status = "approved"
        version.approved_by = approved_by
        version.approved_at = datetime.now()

        self.db.commit()
        self.db.refresh(version)

        logger.info(f"Approved version {version_number} for report {report_id} by {approved_by}")
        return version

    # ==================== Private Methods ====================

    def _get_latest_version(self, report_id: int) -> Optional[ReportVersion]:
        """Get the latest version for a report."""
        return self.db.query(ReportVersion).filter(
            ReportVersion.report_id == report_id
        ).order_by(
            ReportVersion.major_version.desc(),
            ReportVersion.minor_version.desc()
        ).first()

    def _create_snapshot(self, report: Report) -> Dict[str, Any]:
        """Create a complete data snapshot for the report."""
        project_id = report.project_id

        # Get associated assets
        assets = self.db.query(Asset).filter(
            Asset.project_id == project_id
        ).all()

        # Get associated threats
        threats = self.db.query(ThreatRisk).filter(
            ThreatRisk.project_id == project_id
        ).all()

        # Get associated measures
        measures = self.db.query(ControlMeasure).filter(
            ControlMeasure.threat_risk_id.in_([t.id for t in threats])
        ).all() if threats else []

        return {
            "project": {
                "id": project_id,
                "name": report.project.name if report.project else None,
            },
            "report": {
                "id": report.id,
                "name": report.name,
                "template": report.template,
            },
            "assets": [
                {
                    "id": a.id,
                    "name": a.name,
                    "asset_type": a.asset_type,
                    "category": a.category,
                    "criticality": a.criticality,
                }
                for a in assets
            ],
            "threats": [
                {
                    "id": t.id,
                    "threat_name": t.threat_name,
                    "threat_type": t.threat_type,
                    "risk_level": t.risk_level,
                    "asset_id": t.asset_id,
                }
                for t in threats
            ],
            "measures": [
                {
                    "id": m.id,
                    "name": m.name,
                    "control_type": m.control_type,
                    "threat_risk_id": m.threat_risk_id,
                }
                for m in measures
            ],
            "statistics": report.statistics,
            "captured_at": datetime.now().isoformat(),
        }

    def _calculate_changes(
        self,
        old_snapshot: Dict[str, Any],
        new_snapshot: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Calculate changes between two snapshots."""
        changes = []

        # Compare assets
        changes.extend(self._compare_entities(
            old_snapshot.get("assets", []),
            new_snapshot.get("assets", []),
            "asset",
            "name"
        ))

        # Compare threats
        changes.extend(self._compare_entities(
            old_snapshot.get("threats", []),
            new_snapshot.get("threats", []),
            "threat",
            "threat_name"
        ))

        # Compare measures
        changes.extend(self._compare_entities(
            old_snapshot.get("measures", []),
            new_snapshot.get("measures", []),
            "measure",
            "name"
        ))

        return changes

    def _compare_entities(
        self,
        old_list: List[Dict],
        new_list: List[Dict],
        entity_type: str,
        name_field: str,
    ) -> List[Dict[str, Any]]:
        """Compare two lists of entities and return changes."""
        changes = []

        old_map = {e["id"]: e for e in old_list}
        new_map = {e["id"]: e for e in new_list}

        # Find added entities
        for eid, entity in new_map.items():
            if eid not in old_map:
                changes.append({
                    "change_type": "add",
                    "entity_type": entity_type,
                    "entity_id": eid,
                    "entity_name": entity.get(name_field),
                    "new_value": entity,
                })

        # Find deleted entities
        for eid, entity in old_map.items():
            if eid not in new_map:
                changes.append({
                    "change_type": "delete",
                    "entity_type": entity_type,
                    "entity_id": eid,
                    "entity_name": entity.get(name_field),
                    "old_value": entity,
                })

        # Find modified entities
        for eid, new_entity in new_map.items():
            if eid in old_map:
                old_entity = old_map[eid]
                if new_entity != old_entity:
                    # Find which fields changed
                    for key in set(old_entity.keys()) | set(new_entity.keys()):
                        if old_entity.get(key) != new_entity.get(key):
                            changes.append({
                                "change_type": "modify",
                                "entity_type": entity_type,
                                "entity_id": eid,
                                "entity_name": new_entity.get(name_field),
                                "field_name": key,
                                "old_value": old_entity.get(key),
                                "new_value": new_entity.get(key),
                            })

        return changes

    def _generate_change_summary(self, changes: List[Dict]) -> str:
        """Generate a change summary from changes list."""
        if not changes:
            return "初始版本"

        adds = len([c for c in changes if c["change_type"] == "add"])
        mods = len([c for c in changes if c["change_type"] == "modify"])
        dels = len([c for c in changes if c["change_type"] == "delete"])

        parts = []
        if adds:
            parts.append(f"新增 {adds} 项")
        if mods:
            parts.append(f"修改 {mods} 项")
        if dels:
            parts.append(f"删除 {dels} 项")

        return "，".join(parts) if parts else "无变更"

    def _generate_change_description(self, change: Dict) -> str:
        """Generate a human-readable description for a change."""
        entity_type_names = {
            "asset": "资产",
            "threat": "威胁",
            "measure": "措施",
        }
        change_type_names = {
            "add": "新增",
            "modify": "修改",
            "delete": "删除",
        }

        entity_name = entity_type_names.get(change["entity_type"], change["entity_type"])
        action = change_type_names.get(change["change_type"], change["change_type"])
        name = change.get("entity_name", "未知")

        if change["change_type"] == "modify" and change.get("field_name"):
            return f"{action}{entity_name}「{name}」的{change['field_name']}"
        else:
            return f"{action}{entity_name}「{name}」"
