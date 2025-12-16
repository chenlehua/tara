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
