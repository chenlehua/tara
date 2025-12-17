"""
Document Service
================

Business logic for document management and parsing.
"""

from typing import List, Optional, Tuple

import httpx
from sqlalchemy.orm import Session
from tara_shared.config import settings
from tara_shared.database.minio import storage_service
from tara_shared.models import Document
from tara_shared.utils import (generate_file_path, get_file_extension,
                               get_logger, get_mime_type)

from ..parsers import get_parser
from ..repositories.document_repo import DocumentRepository

logger = get_logger(__name__)


class DocumentService:
    """Service for document operations."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = DocumentRepository(db)

    async def upload_document(
        self,
        project_id: int,
        filename: str,
        content: bytes,
        content_type: str = None,
        doc_type: str = None,
    ) -> Document:
        """Upload a document to storage and create database record."""
        logger.info(f"Uploading document: {filename} for project {project_id}")

        # Generate storage path
        file_extension = get_file_extension(filename)
        file_path = generate_file_path(
            bucket=settings.minio_bucket_documents,
            project_id=project_id,
            filename=filename,
        )

        # Upload to MinIO
        storage_service.upload_bytes(
            bucket=settings.minio_bucket_documents,
            object_name=file_path,
            data=content,
            content_type=content_type or get_mime_type(filename),
        )

        # Create database record
        document = Document(
            project_id=project_id,
            filename=filename,
            file_path=file_path,
            file_size=len(content),
            file_type=content_type or get_mime_type(filename),
            file_extension=file_extension,
            doc_type=doc_type,
            parse_status=0,  # Pending
        )

        created = self.repo.create(document)
        logger.info(f"Document uploaded: id={created.id}")
        return created

    def get_document(self, document_id: int) -> Optional[Document]:
        """Get document by ID."""
        return self.repo.get_by_id(document_id)

    def list_documents(
        self,
        project_id: int,
        page: int = 1,
        page_size: int = 20,
        doc_type: str = None,
    ) -> Tuple[List[Document], int]:
        """List documents for a project."""
        return self.repo.list_documents(
            project_id=project_id,
            page=page,
            page_size=page_size,
            doc_type=doc_type,
        )

    async def parse_document(
        self,
        document_id: int,
        enable_ocr: bool = True,
        enable_structure: bool = True,
        enable_embedding: bool = False,
    ) -> Document:
        """Parse a document (OCR + structure extraction)."""
        document = self.repo.get_by_id(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        logger.info(f"Starting parse for document {document_id}")

        # Update status to parsing
        document.parse_status = 1
        document.parse_progress = 0
        self.repo.update(document)

        try:
            # Download file from storage
            file_content = storage_service.download_file(
                bucket=settings.minio_bucket_documents,
                object_name=document.file_path,
            )

            # Get appropriate parser
            parser = get_parser(document.file_extension)

            # Parse document
            parse_result = await parser.parse(
                content=file_content,
                filename=document.filename,
                enable_ocr=enable_ocr,
                enable_structure=enable_structure,
            )

            # Update document with parsed content
            document.title = parse_result.get("title")
            document.content = parse_result.get("content")
            document.structure = parse_result.get("structure", {})
            document.metadata = parse_result.get("metadata", {})
            document.page_count = parse_result.get("page_count")
            document.ocr_result = parse_result.get("ocr_result", {})
            document.parse_status = 2  # Completed
            document.parse_progress = 100

            # Generate embeddings if requested
            if enable_embedding and document.content:
                await self._generate_embeddings(document)
                document.embedding_status = 1

            self.repo.update(document)
            logger.info(f"Document {document_id} parsed successfully")

        except Exception as e:
            logger.error(f"Failed to parse document {document_id}: {e}")
            document.parse_status = 3  # Failed
            document.parse_error = str(e)
            self.repo.update(document)
            raise

        return document

    async def _generate_embeddings(self, document: Document) -> None:
        """Generate embeddings for document content."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.embedding_url}/embeddings",
                    json={
                        "input": document.content[:8000],  # Truncate for embedding
                        "model": "qwen3-embedding",
                    },
                    timeout=60.0,
                )
                response.raise_for_status()
                # Store embeddings in Milvus
                # ... (implementation)
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")

    def delete_document(self, document_id: int) -> bool:
        """Delete a document."""
        document = self.repo.get_by_id(document_id)
        if not document:
            return False

        # Delete from storage
        try:
            storage_service.delete_file(
                bucket=settings.minio_bucket_documents,
                object_name=document.file_path,
            )
        except Exception as e:
            logger.error(f"Failed to delete file from storage: {e}")

        # Delete from database
        self.repo.delete(document)
        logger.info(f"Document deleted: id={document_id}")
        return True

    async def parse_and_extract(
        self,
        document_id: int,
        extract_assets: bool = True,
        extract_threats: bool = False,
    ) -> dict:
        """
        Parse document and extract structured data for TARA analysis.
        
        This is the main entry point for one-click report generation.
        Returns extracted assets, threats, and other structured data.
        """
        document = self.repo.get_by_id(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        logger.info(f"Starting parse and extract for document {document_id}")

        # Parse document first if not already parsed
        if document.parse_status != 2:  # Not completed
            await self.parse_document(document_id)
            document = self.repo.get_by_id(document_id)

        result = {
            "document_id": document_id,
            "project_id": document.project_id,
            "filename": document.filename,
            "content": document.content,
            "structure": document.structure or {},
            "metadata": document.metadata or {},
            "extracted_data": {},
        }

        # Extract assets from content
        if extract_assets and document.content:
            assets = await self._extract_assets_from_content(document)
            result["extracted_data"]["assets"] = assets

        # Extract threats if requested
        if extract_threats and document.content:
            threats = await self._extract_threats_from_content(document)
            result["extracted_data"]["threats"] = threats

        # Store extracted data in document metadata
        document.metadata = document.metadata or {}
        document.metadata["extracted_data"] = result["extracted_data"]
        self.repo.update(document)

        logger.info(f"Parse and extract completed for document {document_id}")
        return result

    async def _extract_assets_from_content(self, document) -> List[dict]:
        """Extract asset information from document content."""
        assets = []
        content = document.content or ""

        # Try AI-based extraction
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.qwen3_url}/chat/completions",
                    json={
                        "model": "qwen3",
                        "messages": [
                            {
                                "role": "system",
                                "content": """你是汽车网络安全专家。请从文档内容中识别所有车载电子电气资产。
返回JSON数组，每个资产包含:
- name: 资产名称
- asset_type: 类型(ECU/Gateway/Sensor/Actuator/Interface/Data)
- category: 类别(内部实体/外部接口/数据存储)
- description: 描述
- interfaces: 接口列表[{type: 接口类型, protocol: 协议}]
- security_attrs: {authenticity, integrity, confidentiality, availability}""",
                            },
                            {
                                "role": "user",
                                "content": f"文档: {document.filename}\n\n内容:\n{content[:6000]}",
                            },
                        ],
                        "temperature": 0.2,
                        "max_tokens": 3000,
                    },
                    timeout=90.0,
                )
                if response.status_code == 200:
                    import json
                    import re
                    result = response.json()
                    ai_content = result["choices"][0]["message"]["content"]
                    # Extract JSON from response
                    json_match = re.search(r'\[.*\]', ai_content, re.DOTALL)
                    if json_match:
                        assets = json.loads(json_match.group())
                        logger.info(f"Extracted {len(assets)} assets using AI")
        except Exception as e:
            logger.warning(f"AI extraction failed, using fallback: {e}")

        # Fallback: keyword-based extraction
        if not assets:
            assets = self._extract_assets_by_keywords(content)

        return assets

    def _extract_assets_by_keywords(self, content: str) -> List[dict]:
        """Fallback keyword-based asset extraction."""
        import re
        assets = []
        
        # Common automotive asset patterns
        patterns = [
            (r'(ECU|控制器|控制单元)', 'ECU', '内部实体'),
            (r'(Gateway|网关|CGW)', 'Gateway', '内部实体'),
            (r'(T-Box|Telematics|远程信息)', 'T-Box', '外部接口'),
            (r'(IVI|信息娱乐|车机)', 'IVI', '内部实体'),
            (r'(ADAS|辅助驾驶)', 'ADAS', '内部实体'),
            (r'(BCM|车身控制)', 'BCM', '内部实体'),
            (r'(传感器|Sensor)', 'Sensor', '内部实体'),
            (r'(OBD|诊断接口)', 'Interface', '外部接口'),
        ]
        
        seen_names = set()
        for pattern, asset_type, category in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                name = match if isinstance(match, str) else match[0]
                if name.lower() not in seen_names:
                    seen_names.add(name.lower())
                    assets.append({
                        "name": name,
                        "asset_type": asset_type,
                        "category": category,
                        "description": f"从文档中识别的{asset_type}资产",
                        "interfaces": [],
                        "security_attrs": {
                            "authenticity": True,
                            "integrity": True,
                            "availability": True,
                        },
                    })
        
        return assets

    async def _extract_threats_from_content(self, document) -> List[dict]:
        """Extract threat information from document content."""
        threats = []
        content = document.content or ""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.qwen3_url}/chat/completions",
                    json={
                        "model": "qwen3",
                        "messages": [
                            {
                                "role": "system",
                                "content": """你是汽车网络安全专家。请从文档中识别安全威胁。
返回JSON数组，每个威胁包含:
- name: 威胁名称
- threat_type: STRIDE类型(S/T/R/I/D/E)
- description: 威胁描述
- attack_vector: 攻击向量
- impact_level: 影响等级(1-4)""",
                            },
                            {
                                "role": "user",
                                "content": f"文档: {document.filename}\n\n内容:\n{content[:6000]}",
                            },
                        ],
                        "temperature": 0.2,
                        "max_tokens": 2000,
                    },
                    timeout=60.0,
                )
                if response.status_code == 200:
                    import json
                    import re
                    result = response.json()
                    ai_content = result["choices"][0]["message"]["content"]
                    json_match = re.search(r'\[.*\]', ai_content, re.DOTALL)
                    if json_match:
                        threats = json.loads(json_match.group())
        except Exception as e:
            logger.warning(f"Threat extraction failed: {e}")

        return threats

    def get_parsed_content(self, document_id: int) -> Optional[dict]:
        """Get parsed content and extracted data for a document."""
        document = self.repo.get_by_id(document_id)
        if not document:
            return None

        return {
            "document_id": document_id,
            "project_id": document.project_id,
            "filename": document.filename,
            "title": document.title,
            "content": document.content,
            "structure": document.structure,
            "metadata": document.metadata,
            "extracted_data": (document.metadata or {}).get("extracted_data", {}),
            "parse_status": document.parse_status,
        }

    def get_extracted_assets(self, document_id: int) -> List[dict]:
        """Get extracted assets from a parsed document."""
        document = self.repo.get_by_id(document_id)
        if not document:
            return []

        metadata = document.metadata or {}
        extracted = metadata.get("extracted_data", {})
        return extracted.get("assets", [])
