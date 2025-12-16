"""
Asset Service
=============

Business logic for asset management.
"""

import uuid
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session
from tara_shared.database.neo4j import graph_service
from tara_shared.models import Asset
from tara_shared.schemas.asset import AssetCreate, AssetUpdate
from tara_shared.utils import get_logger

from ..repositories.asset_repo import AssetRepository

logger = get_logger(__name__)


class AssetService:
    """Service for asset operations."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = AssetRepository(db)

    def create_asset(self, data: AssetCreate) -> Asset:
        """Create a new asset."""
        logger.info(f"Creating asset: {data.name}")

        asset = Asset(
            project_id=data.project_id,
            parent_id=data.parent_id,
            name=data.name,
            asset_type=data.asset_type,
            category=data.category,
            description=data.description,
            version=data.version,
            vendor=data.vendor,
            model_number=data.model_number,
            security_attrs=(
                data.security_attrs.model_dump() if data.security_attrs else {}
            ),
            interfaces=[i.model_dump() for i in data.interfaces],
            data_types=data.data_types,
            location=data.location,
            zone=data.zone,
            trust_boundary=data.trust_boundary,
            is_external=data.is_external,
            criticality=data.criticality,
            source="manual",
        )

        created = self.repo.create(asset)

        # Create node in Neo4j
        try:
            self._create_graph_node(created)
        except Exception as e:
            logger.error(f"Failed to create graph node: {e}")

        return created

    def get_asset(self, asset_id: int) -> Optional[Asset]:
        """Get asset by ID."""
        return self.repo.get_by_id(asset_id)

    def list_assets(
        self,
        project_id: int,
        page: int = 1,
        page_size: int = 20,
        asset_type: str = None,
        category: str = None,
        keyword: str = None,
    ) -> Tuple[List[Asset], int]:
        """List assets with pagination and filtering."""
        return self.repo.list_assets(
            project_id=project_id,
            page=page,
            page_size=page_size,
            asset_type=asset_type,
            category=category,
            keyword=keyword,
        )

    def update_asset(self, asset_id: int, data: AssetUpdate) -> Optional[Asset]:
        """Update an asset."""
        asset = self.repo.get_by_id(asset_id)
        if not asset:
            return None

        update_data = data.model_dump(exclude_unset=True)

        # Handle nested objects
        if "security_attrs" in update_data and update_data["security_attrs"]:
            update_data["security_attrs"] = (
                update_data["security_attrs"].model_dump()
                if hasattr(update_data["security_attrs"], "model_dump")
                else update_data["security_attrs"]
            )
        if "interfaces" in update_data and update_data["interfaces"]:
            update_data["interfaces"] = [
                i.model_dump() if hasattr(i, "model_dump") else i
                for i in update_data["interfaces"]
            ]

        for key, value in update_data.items():
            setattr(asset, key, value)

        return self.repo.update(asset)

    def delete_asset(self, asset_id: int) -> bool:
        """Delete an asset."""
        asset = self.repo.get_by_id(asset_id)
        if not asset:
            return False

        # Delete from Neo4j
        try:
            self._delete_graph_node(asset)
        except Exception as e:
            logger.error(f"Failed to delete graph node: {e}")

        self.repo.delete(asset)
        return True

    def get_asset_graph(self, project_id: int) -> Dict[str, Any]:
        """Get asset relationship graph."""
        assets = self.repo.get_all_by_project(project_id)

        nodes = []
        edges = []

        for asset in assets:
            nodes.append(
                {
                    "id": asset.id,
                    "name": asset.name,
                    "asset_type": asset.asset_type,
                    "category": asset.category,
                }
            )

            # Parent-child relationships
            if asset.parent_id:
                edges.append(
                    {
                        "source": asset.parent_id,
                        "target": asset.id,
                        "relation_type": "contains",
                    }
                )

        # Get relationships from Neo4j
        try:
            neo4j_edges = self._get_graph_relations(project_id)
            edges.extend(neo4j_edges)
        except Exception as e:
            logger.error(f"Failed to get graph relations: {e}")

        return {"nodes": nodes, "edges": edges}

    def add_asset_relation(
        self,
        source_id: int,
        target_id: int,
        relation_type: str,
    ) -> bool:
        """Add a relationship between two assets."""
        source = self.repo.get_by_id(source_id)
        target = self.repo.get_by_id(target_id)

        if not source or not target:
            return False

        try:
            graph_service.create_relationship(
                from_label="Asset",
                from_property="mysql_id",
                from_value=source_id,
                to_label="Asset",
                to_property="mysql_id",
                to_value=target_id,
                rel_type=relation_type.upper(),
            )
            return True
        except Exception as e:
            logger.error(f"Failed to create relationship: {e}")
            return False

    def start_asset_discovery(
        self,
        document_ids: List[int],
        include_relations: bool = True,
    ) -> str:
        """Start asset discovery task and return task ID."""
        return str(uuid.uuid4())

    async def run_asset_discovery(
        self,
        task_id: str,
        document_ids: List[int],
        include_relations: bool = True,
    ) -> None:
        """Run asset discovery (background task)."""
        logger.info(f"Starting asset discovery task {task_id}")
        # Implementation would call AI service for asset extraction
        # This is a placeholder for the actual AI-powered discovery
        pass

    def _create_graph_node(self, asset: Asset) -> None:
        """Create asset node in Neo4j."""
        graph_service.create_node(
            label="Asset",
            properties={
                "mysql_id": asset.id,
                "name": asset.name,
                "type": asset.asset_type,
                "category": asset.category,
                "project_id": asset.project_id,
            },
        )

    def _delete_graph_node(self, asset: Asset) -> None:
        """Delete asset node from Neo4j."""
        graph_service.execute_write(
            "MATCH (n:Asset {mysql_id: $id}) DETACH DELETE n",
            {"id": asset.id},
        )

    def _get_graph_relations(self, project_id: int) -> List[Dict[str, Any]]:
        """Get asset relationships from Neo4j."""
        results = graph_service.execute_query(
            """
            MATCH (a:Asset {project_id: $project_id})-[r]->(b:Asset {project_id: $project_id})
            RETURN a.mysql_id as source, b.mysql_id as target, type(r) as relation_type
            """,
            {"project_id": project_id},
        )
        return [
            {
                "source": r["source"],
                "target": r["target"],
                "relation_type": r["relation_type"],
            }
            for r in results
        ]
