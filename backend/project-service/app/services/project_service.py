"""
Project Service
===============

Business logic for project management.
"""

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session
from tara_shared.models import Asset, Document, Project, Report, ThreatRisk
from tara_shared.schemas import ProjectCreate, ProjectUpdate
from tara_shared.utils import get_logger

from ..repositories.project_repo import ProjectRepository

logger = get_logger(__name__)


class ProjectService:
    """Service for project management operations."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = ProjectRepository(db)

    def create_project(self, data: ProjectCreate) -> Project:
        """
        Create a new project.

        Args:
            data: Project creation data

        Returns:
            Created project
        """
        logger.info(f"Creating project: {data.name}")

        project = Project(
            name=data.name,
            description=data.description,
            vehicle_type=data.vehicle_type,
            vehicle_model=data.vehicle_model,
            vehicle_year=data.vehicle_year,
            standard=data.standard,
            scope=data.scope,
            owner=data.owner,
            team=data.team,
            config=data.config,
            tags=data.tags,
            status=0,  # Draft
        )

        created = self.repo.create(project)
        logger.info(f"Project created: id={created.id}")
        return created

    def get_project(self, project_id: int) -> Optional[Project]:
        """
        Get project by ID.

        Args:
            project_id: Project ID

        Returns:
            Project or None
        """
        return self.repo.get_by_id(project_id)

    def list_projects(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        status: Optional[int] = None,
    ) -> Tuple[List[Project], int]:
        """
        List projects with pagination and filtering.

        Args:
            page: Page number
            page_size: Items per page
            keyword: Search keyword
            status: Project status filter

        Returns:
            Tuple of (projects list, total count)
        """
        return self.repo.list_projects(
            page=page,
            page_size=page_size,
            keyword=keyword,
            status=status,
        )

    def update_project(
        self,
        project_id: int,
        data: ProjectUpdate,
    ) -> Optional[Project]:
        """
        Update a project.

        Args:
            project_id: Project ID
            data: Update data

        Returns:
            Updated project or None
        """
        project = self.repo.get_by_id(project_id)
        if not project:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(project, key, value)

        updated = self.repo.update(project)
        logger.info(f"Project updated: id={project_id}")
        return updated

    def delete_project(self, project_id: int) -> bool:
        """
        Delete a project and all related data.

        Args:
            project_id: Project ID

        Returns:
            True if deleted, False if not found
        """
        project = self.repo.get_by_id(project_id)
        if not project:
            return False

        # Cascade delete is handled by SQLAlchemy relationships
        self.repo.delete(project)
        logger.info(f"Project deleted: id={project_id}")
        return True

    def update_project_status(
        self,
        project_id: int,
        status: int,
    ) -> Optional[Project]:
        """
        Update project status.

        Args:
            project_id: Project ID
            status: New status

        Returns:
            Updated project or None
        """
        project = self.repo.get_by_id(project_id)
        if not project:
            return None

        project.status = status
        updated = self.repo.update(project)
        logger.info(f"Project status updated: id={project_id}, status={status}")
        return updated

    def get_project_stats(self, project_id: int) -> Dict[str, Any]:
        """
        Get project statistics.

        Args:
            project_id: Project ID

        Returns:
            Statistics dictionary
        """
        return self.repo.get_stats(project_id)

    def clone_project(
        self,
        project_id: int,
        new_name: str,
        include_documents: bool = True,
        include_assets: bool = True,
        include_threats: bool = True,
    ) -> Optional[Project]:
        """
        Clone an existing project.

        Args:
            project_id: Source project ID
            new_name: Name for the cloned project
            include_documents: Clone documents
            include_assets: Clone assets
            include_threats: Clone threats

        Returns:
            Cloned project or None
        """
        source = self.repo.get_by_id(project_id)
        if not source:
            return None

        # Create new project with source data
        new_project = Project(
            name=new_name,
            description=source.description,
            vehicle_type=source.vehicle_type,
            vehicle_model=source.vehicle_model,
            vehicle_year=source.vehicle_year,
            standard=source.standard,
            scope=source.scope,
            owner=source.owner,
            team=source.team.copy() if source.team else [],
            config=source.config.copy() if source.config else {},
            tags=source.tags.copy() if source.tags else [],
            status=0,  # Start as draft
        )

        created = self.repo.create(new_project)

        # Clone related entities if requested
        if include_assets and source.assets:
            asset_id_map = {}  # Map old ID to new ID
            for asset in source.assets:
                new_asset = Asset(
                    project_id=created.id,
                    name=asset.name,
                    asset_type=asset.asset_type,
                    category=asset.category,
                    description=asset.description,
                    version=asset.version,
                    vendor=asset.vendor,
                    model_number=asset.model_number,
                    security_attrs=(
                        asset.security_attrs.copy() if asset.security_attrs else {}
                    ),
                    interfaces=asset.interfaces.copy() if asset.interfaces else [],
                    data_types=asset.data_types.copy() if asset.data_types else [],
                    location=asset.location,
                    zone=asset.zone,
                    trust_boundary=asset.trust_boundary,
                    is_external=asset.is_external,
                    criticality=asset.criticality,
                    source="cloned",
                )
                self.db.add(new_asset)
                self.db.flush()
                asset_id_map[asset.id] = new_asset.id

            # Update parent references
            for asset in source.assets:
                if asset.parent_id and asset.parent_id in asset_id_map:
                    new_asset_id = asset_id_map[asset.id]
                    new_asset = self.db.query(Asset).get(new_asset_id)
                    new_asset.parent_id = asset_id_map[asset.parent_id]

        if include_threats and source.threat_risks:
            for threat in source.threat_risks:
                # Only clone if the related asset was cloned
                new_asset_id = (
                    asset_id_map.get(threat.asset_id) if include_assets else None
                )
                if new_asset_id:
                    new_threat = ThreatRisk(
                        project_id=created.id,
                        asset_id=new_asset_id,
                        threat_name=threat.threat_name,
                        threat_type=threat.threat_type,
                        threat_desc=threat.threat_desc,
                        attack_vector=threat.attack_vector,
                        attack_surface=threat.attack_surface,
                        threat_source=threat.threat_source,
                        threat_agent=threat.threat_agent,
                        safety_impact=threat.safety_impact,
                        financial_impact=threat.financial_impact,
                        operational_impact=threat.operational_impact,
                        privacy_impact=threat.privacy_impact,
                        impact_level=threat.impact_level,
                        likelihood=threat.likelihood,
                        risk_value=threat.risk_value,
                        risk_level=threat.risk_level,
                        source="cloned",
                        cwe_ids=threat.cwe_ids.copy() if threat.cwe_ids else [],
                        capec_ids=threat.capec_ids.copy() if threat.capec_ids else [],
                    )
                    self.db.add(new_threat)

        self.db.commit()
        logger.info(f"Project cloned: source={project_id}, new={created.id}")

        return created
