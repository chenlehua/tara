"""
MinIO Object Storage Connection
===============================

MinIO client for file storage operations.
"""

import io
from datetime import timedelta
from typing import Any, BinaryIO, Dict, List, Optional

from minio import Minio
from minio.error import S3Error

from ..config import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MinIOClient:
    """MinIO client wrapper."""

    _client: Optional[Minio] = None
    _connection_error: Optional[str] = None

    @classmethod
    def get_client(cls) -> Optional[Minio]:
        """Get MinIO client instance (singleton)."""
        if cls._client is None and cls._connection_error is None:
            try:
                cls._client = Minio(
                    settings.minio_endpoint,
                    access_key=settings.minio_access_key,
                    secret_key=settings.minio_secret_key,
                    secure=False,  # Set to True in production with HTTPS
                )
                # Test connection by listing buckets
                list(cls._client.list_buckets())
                logger.info(f"Connected to MinIO at {settings.minio_endpoint}")
            except Exception as e:
                cls._connection_error = str(e)
                logger.warning(f"Failed to connect to MinIO: {e}. File storage will be unavailable.")
                cls._client = None
        return cls._client

    @classmethod
    def is_available(cls) -> bool:
        """Check if MinIO is available."""
        return cls.get_client() is not None

    @classmethod
    def init_buckets(cls) -> None:
        """Initialize required buckets."""
        client = cls.get_client()
        if client is None:
            logger.warning("MinIO not available, skipping bucket initialization")
            return
        
        try:
            buckets = [
                settings.minio_bucket_documents,
                settings.minio_bucket_reports,
                settings.minio_bucket_diagrams,
            ]
            for bucket in buckets:
                if not client.bucket_exists(bucket):
                    client.make_bucket(bucket)
                    logger.info(f"Created bucket: {bucket}")
        except Exception as e:
            logger.warning(f"Failed to initialize buckets: {e}")


def get_minio_client() -> Optional[Minio]:
    """Get MinIO client for dependency injection."""
    return MinIOClient.get_client()


# Lazy-initialized global client
minio_client: Optional[Minio] = None


def get_global_minio_client() -> Optional[Minio]:
    """Get global MinIO client with lazy initialization."""
    global minio_client
    if minio_client is None:
        minio_client = MinIOClient.get_client()
    return minio_client


class StorageService:
    """Service for file storage operations."""

    def __init__(self, client: Minio = None):
        self._client = client
        self._lazy_client = client is None

    @property
    def client(self) -> Optional[Minio]:
        """Get client with lazy initialization."""
        if self._lazy_client and self._client is None:
            self._client = get_minio_client()
        return self._client

    def is_available(self) -> bool:
        """Check if storage service is available."""
        return self.client is not None

    def upload_file(
        self,
        bucket: str,
        object_name: str,
        file_data: BinaryIO,
        length: int,
        content_type: str = "application/octet-stream",
        metadata: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        """Upload a file to bucket."""
        if not self.is_available():
            logger.warning("MinIO not available, skipping file upload")
            return {"bucket": bucket, "object_name": object_name, "error": "Storage unavailable"}
        
        try:
            result = self.client.put_object(
                bucket_name=bucket,
                object_name=object_name,
                data=file_data,
                length=length,
                content_type=content_type,
                metadata=metadata,
            )
            return {
                "bucket": bucket,
                "object_name": object_name,
                "etag": result.etag,
                "version_id": result.version_id,
            }
        except S3Error as e:
            logger.error(f"Upload failed: {e}")
            raise

    def upload_bytes(
        self,
        bucket: str,
        object_name: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        """Upload bytes data to bucket."""
        return self.upload_file(
            bucket=bucket,
            object_name=object_name,
            file_data=io.BytesIO(data),
            length=len(data),
            content_type=content_type,
            metadata=metadata,
        )

    def download_file(self, bucket: str, object_name: str) -> bytes:
        """Download a file from bucket."""
        try:
            response = self.client.get_object(bucket, object_name)
            return response.read()
        except S3Error as e:
            logger.error(f"Download failed: {e}")
            raise
        finally:
            response.close()
            response.release_conn()

    def get_presigned_url(
        self,
        bucket: str,
        object_name: str,
        expires: int = 3600,  # 1 hour
    ) -> str:
        """Get presigned URL for file access."""
        return self.client.presigned_get_object(
            bucket_name=bucket,
            object_name=object_name,
            expires=timedelta(seconds=expires),
        )

    def get_upload_url(
        self,
        bucket: str,
        object_name: str,
        expires: int = 3600,
    ) -> str:
        """Get presigned URL for file upload."""
        return self.client.presigned_put_object(
            bucket_name=bucket,
            object_name=object_name,
            expires=timedelta(seconds=expires),
        )

    def delete_file(self, bucket: str, object_name: str) -> bool:
        """Delete a file from bucket."""
        try:
            self.client.remove_object(bucket, object_name)
            return True
        except S3Error as e:
            logger.error(f"Delete failed: {e}")
            return False

    def list_files(
        self,
        bucket: str,
        prefix: str = "",
        recursive: bool = True,
    ) -> List[Dict[str, Any]]:
        """List files in bucket."""
        objects = self.client.list_objects(
            bucket_name=bucket,
            prefix=prefix,
            recursive=recursive,
        )
        return [
            {
                "name": obj.object_name,
                "size": obj.size,
                "last_modified": obj.last_modified,
                "etag": obj.etag,
            }
            for obj in objects
        ]

    def file_exists(self, bucket: str, object_name: str) -> bool:
        """Check if file exists."""
        try:
            self.client.stat_object(bucket, object_name)
            return True
        except S3Error:
            return False

    def get_file_info(self, bucket: str, object_name: str) -> Dict[str, Any]:
        """Get file metadata."""
        try:
            stat = self.client.stat_object(bucket, object_name)
            return {
                "name": stat.object_name,
                "size": stat.size,
                "content_type": stat.content_type,
                "last_modified": stat.last_modified,
                "etag": stat.etag,
                "metadata": stat.metadata,
            }
        except S3Error as e:
            logger.error(f"Stat failed: {e}")
            raise


# Lazy-initialized global storage service
storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Get global storage service with lazy initialization."""
    global storage_service
    if storage_service is None:
        storage_service = StorageService()
    return storage_service
