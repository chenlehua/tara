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
        project_id: Optional[int] = None,
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

        # Import document model
        from tara_shared.models import Document

        for doc_id in document_ids:
            try:
                # Get document from database
                doc = self.db.query(Document).filter(Document.id == doc_id).first()
                if not doc:
                    logger.warning(f"Document {doc_id} not found")
                    continue

                project_id = doc.project_id

                # Try to use AI service for asset extraction
                try:
                    import httpx
                    from tara_shared.config import settings

                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"{settings.qwen3_url}/chat/completions",
                            json={
                                "model": "qwen3",
                                "messages": [
                                    {
                                        "role": "system",
                                        "content": "你是一个汽车网络安全专家，请从以下文档内容中识别出所有的ECU、传感器、网关等资产，并以JSON数组格式返回。每个资产包含: name(名称), asset_type(类型:ECU/Gateway/Sensor/Actuator), category(类别), description(描述)。",
                                    },
                                    {
                                        "role": "user",
                                        "content": f"文档名称: {doc.name}\n内容: {doc.content[:4000] if doc.content else '无内容'}",
                                    },
                                ],
                                "temperature": 0.3,
                                "max_tokens": 2000,
                            },
                            timeout=60.0,
                        )
                        if response.status_code == 200:
                            result = response.json()
                            ai_response = result["choices"][0]["message"]["content"]
                            # Parse AI response and create assets
                            await self._parse_and_create_assets(
                                project_id, ai_response, include_relations
                            )
                            continue
                except Exception as e:
                    logger.warning(f"AI service unavailable, using fallback: {e}")

                # Fallback: create basic assets from document metadata
                doc_metadata = doc.doc_metadata or {}
                if "assets" in doc_metadata:
                    for asset_data in doc_metadata["assets"]:
                        asset = Asset(
                            project_id=project_id,
                            name=asset_data.get("name", "Unknown Asset"),
                            asset_type=asset_data.get("type", "ECU"),
                            category=asset_data.get("category", "general"),
                            description=asset_data.get("description", ""),
                            source="document_import",
                        )
                        self.db.add(asset)

                self.db.commit()
                logger.info(f"Asset discovery completed for document {doc_id}")

            except Exception as e:
                logger.error(f"Asset discovery failed for document {doc_id}: {e}")
                self.db.rollback()

    async def _parse_and_create_assets(
        self,
        project_id: int,
        ai_response: str,
        include_relations: bool = True,
    ) -> None:
        """Parse AI response and create assets in database."""
        import json
        import re

        try:
            # Extract JSON from AI response
            json_match = re.search(r"\[.*\]", ai_response, re.DOTALL)
            if not json_match:
                logger.warning("No JSON array found in AI response")
                return

            assets_data = json.loads(json_match.group())

            for asset_data in assets_data:
                asset = Asset(
                    project_id=project_id,
                    name=asset_data.get("name", "Unknown"),
                    asset_type=asset_data.get("asset_type", "ECU"),
                    category=asset_data.get("category", "general"),
                    description=asset_data.get("description", ""),
                    source="ai_discovered",
                )
                self.db.add(asset)

            self.db.commit()
            logger.info(f"Created {len(assets_data)} assets from AI discovery")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
        except Exception as e:
            logger.error(f"Failed to create assets from AI response: {e}")
            self.db.rollback()

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

    async def identify_from_document(
        self,
        project_id: int,
        document_id: int,
        include_relations: bool = True,
    ) -> Dict[str, Any]:
        """
        Identify assets from a parsed document.
        
        This is called by report service during one-click generation.
        Fetches extracted assets from document service and creates them in DB.
        """
        import httpx
        from tara_shared.config import settings

        logger.info(f"Identifying assets from document {document_id} for project {project_id}")

        created_assets = []
        relations = []

        try:
            # Call document service to get extracted assets
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.document_service_url}/api/v1/documents/{document_id}/extracted-assets",
                    timeout=30.0,
                )
                
                if response.status_code == 200:
                    result = response.json()
                    extracted_assets = result.get("data", {}).get("assets", [])
                    
                    if not extracted_assets:
                        logger.info("No assets found in document, trying parse-extract")
                        # Try to parse and extract if not done yet
                        parse_response = await client.post(
                            f"{settings.document_service_url}/api/v1/documents/{document_id}/parse-extract",
                            params={"extract_assets": True},
                            timeout=120.0,
                        )
                        if parse_response.status_code == 200:
                            parse_result = parse_response.json()
                            extracted_assets = parse_result.get("data", {}).get("extracted_data", {}).get("assets", [])

                    # Create assets in database
                    for asset_data in extracted_assets:
                        asset = await self._create_asset_from_extracted(
                            project_id, asset_data
                        )
                        if asset:
                            created_assets.append(asset)

                    # Create relationships if requested
                    if include_relations and len(created_assets) > 1:
                        relations = await self._create_asset_relations(created_assets)

        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch from document service: {e}")
            # Fallback: generate default assets
            created_assets = await self._generate_default_assets(project_id)

        return {
            "project_id": project_id,
            "document_id": document_id,
            "created_assets": len(created_assets),
            "assets": [
                {
                    "id": a.id,
                    "name": a.name,
                    "asset_type": a.asset_type,
                    "category": a.category,
                }
                for a in created_assets
            ],
            "relations": relations,
        }

    async def _create_asset_from_extracted(
        self,
        project_id: int,
        asset_data: dict,
    ) -> Optional[Asset]:
        """Create an asset from extracted data."""
        try:
            # Map security attributes
            security_attrs = asset_data.get("security_attrs", {})
            if isinstance(security_attrs, dict):
                # Normalize to expected format
                normalized_attrs = {}
                for key in ["authenticity", "integrity", "confidentiality", "availability"]:
                    if key in security_attrs:
                        val = security_attrs[key]
                        if isinstance(val, bool):
                            normalized_attrs[key] = "high" if val else "low"
                        elif isinstance(val, dict):
                            normalized_attrs[key] = val.get("level", "medium")
                        else:
                            normalized_attrs[key] = str(val)
                security_attrs = normalized_attrs

            # Map interfaces
            interfaces = []
            for iface in asset_data.get("interfaces", []):
                if isinstance(iface, dict):
                    interfaces.append({
                        "name": iface.get("name", iface.get("type", "Unknown")),
                        "interface_type": iface.get("interface_type", iface.get("type", "bus")),
                        "protocol": iface.get("protocol", ""),
                    })
                elif isinstance(iface, str):
                    interfaces.append({"name": iface, "interface_type": "bus", "protocol": ""})

            # Determine criticality based on security attributes
            criticality = "medium"
            if security_attrs:
                high_count = sum(1 for v in security_attrs.values() if v in ["high", "critical"])
                if high_count >= 2:
                    criticality = "high"
                elif high_count >= 1:
                    criticality = "medium"
                else:
                    criticality = "low"

            asset = Asset(
                project_id=project_id,
                name=asset_data.get("name", "Unknown Asset"),
                asset_type=asset_data.get("asset_type", "ECU"),
                category=asset_data.get("category", "内部实体"),
                description=asset_data.get("description", ""),
                security_attrs=security_attrs,
                interfaces=interfaces,
                criticality=criticality,
                source="document_extracted",
            )

            self.db.add(asset)
            self.db.commit()
            self.db.refresh(asset)

            # Create node in Neo4j
            try:
                self._create_graph_node(asset)
            except Exception as e:
                logger.error(f"Failed to create graph node: {e}")

            return asset

        except Exception as e:
            logger.error(f"Failed to create asset from extracted data: {e}")
            self.db.rollback()
            return None

    async def _create_asset_relations(
        self,
        assets: List[Asset],
    ) -> List[Dict[str, Any]]:
        """Create relationships between assets based on type."""
        relations = []

        # Find gateway to create hub-spoke relations
        gateway = next((a for a in assets if "gateway" in a.asset_type.lower()), None)
        
        if gateway:
            for asset in assets:
                if asset.id != gateway.id:
                    try:
                        self.add_asset_relation(
                            source_id=gateway.id,
                            target_id=asset.id,
                            relation_type="COMMUNICATES_WITH",
                        )
                        relations.append({
                            "source": gateway.id,
                            "target": asset.id,
                            "type": "COMMUNICATES_WITH",
                        })
                    except Exception as e:
                        logger.error(f"Failed to create relation: {e}")

        return relations

    async def _generate_default_assets(self, project_id: int) -> List[Asset]:
        """Generate default automotive assets as fallback."""
        default_assets = [
            {
                "name": "Central Gateway",
                "asset_type": "Gateway",
                "category": "内部实体",
                "description": "车辆中央网关，负责各域间通信",
                "interfaces": [
                    {"name": "CAN", "interface_type": "bus", "protocol": "CAN-FD"},
                    {"name": "Ethernet", "interface_type": "network", "protocol": "DoIP"},
                ],
                "security_attrs": {
                    "integrity": "high",
                    "availability": "high",
                    "confidentiality": "medium",
                },
            },
            {
                "name": "T-Box",
                "asset_type": "T-Box",
                "category": "外部接口",
                "description": "远程信息处理器，提供远程通信能力",
                "interfaces": [
                    {"name": "4G/5G", "interface_type": "wireless", "protocol": "LTE"},
                    {"name": "CAN", "interface_type": "bus", "protocol": "CAN"},
                ],
                "security_attrs": {
                    "integrity": "high",
                    "availability": "high",
                    "confidentiality": "high",
                },
            },
            {
                "name": "IVI System",
                "asset_type": "IVI",
                "category": "内部实体",
                "description": "车载信息娱乐系统",
                "interfaces": [
                    {"name": "Bluetooth", "interface_type": "wireless", "protocol": "BT5.0"},
                    {"name": "USB", "interface_type": "bus", "protocol": "USB3.0"},
                    {"name": "CAN", "interface_type": "bus", "protocol": "CAN"},
                ],
                "security_attrs": {
                    "integrity": "medium",
                    "availability": "medium",
                    "confidentiality": "medium",
                },
            },
        ]

        created = []
        for data in default_assets:
            asset = Asset(
                project_id=project_id,
                name=data["name"],
                asset_type=data["asset_type"],
                category=data["category"],
                description=data["description"],
                interfaces=data["interfaces"],
                security_attrs=data["security_attrs"],
                criticality="high" if "Gateway" in data["asset_type"] else "medium",
                source="auto_generated",
            )
            self.db.add(asset)
            created.append(asset)

        self.db.commit()
        for a in created:
            self.db.refresh(a)
            try:
                self._create_graph_node(a)
            except Exception:
                pass

        return created

    def get_assets_for_project(self, project_id: int) -> List[Dict[str, Any]]:
        """Get all assets for a project in API-friendly format."""
        assets = self.repo.get_all_by_project(project_id)
        return [
            {
                "id": a.id,
                "name": a.name,
                "asset_type": a.asset_type,
                "category": a.category,
                "description": a.description,
                "interfaces": a.interfaces or [],
                "security_attrs": a.security_attrs or {},
                "criticality": a.criticality,
            }
            for a in assets
        ]
