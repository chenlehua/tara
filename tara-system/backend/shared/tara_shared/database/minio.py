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

    @classmethod
    def get_client(cls) -> Minio:
        """Get MinIO client instance (singleton)."""
        if cls._client is None:
            cls._client = Minio(
                settings.minio_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=False,  # Set to True in production with HTTPS
            )
        return cls._client

    @classmethod
    def init_buckets(cls) -> None:
        """Initialize required buckets."""
        client = cls.get_client()
        buckets = [
            settings.minio_bucket_documents,
            settings.minio_bucket_reports,
            settings.minio_bucket_diagrams,
        ]
        for bucket in buckets:
            if not client.bucket_exists(bucket):
                client.make_bucket(bucket)
                logger.info(f"Created bucket: {bucket}")


# Global client instance
minio_client = MinIOClient.get_client()


def get_minio_client() -> Minio:
    """Get MinIO client for dependency injection."""
    return MinIOClient.get_client()


class StorageService:
    """Service for file storage operations."""

    def __init__(self, client: Minio = None):
        self.client = client or minio_client

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


# Global storage service
storage_service = StorageService()
