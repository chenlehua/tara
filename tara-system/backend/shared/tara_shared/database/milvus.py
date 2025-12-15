"""
Milvus Vector Database Connection
=================================

Milvus client for vector similarity search.
"""

from typing import Any, Dict, List, Optional

from pymilvus import (
    MilvusClient,
    DataType,
    Collection,
    connections,
    utility,
)

from ..config import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MilvusManager:
    """Milvus connection and operation manager."""

    _client: Optional[MilvusClient] = None

    @classmethod
    def get_client(cls) -> MilvusClient:
        """Get Milvus client instance (singleton)."""
        if cls._client is None:
            cls._client = MilvusClient(
                uri=f"http://{settings.milvus_host}:{settings.milvus_port}",
                user=settings.milvus_user or None,
                password=settings.milvus_password or None,
            )
        return cls._client

    @classmethod
    def close(cls) -> None:
        """Close Milvus connection."""
        if cls._client is not None:
            cls._client.close()
            cls._client = None


def get_milvus_client() -> MilvusClient:
    """Get Milvus client for dependency injection."""
    return MilvusManager.get_client()


def init_milvus() -> None:
    """Initialize Milvus collections."""
    client = get_milvus_client()
    
    # Document embeddings collection
    if not client.has_collection("doc_embeddings"):
        client.create_collection(
            collection_name="doc_embeddings",
            dimension=1024,  # Qwen3-Embedding dimension
            metric_type="COSINE",
            auto_id=True,
        )
        logger.info("Created collection: doc_embeddings")
    
    # Threat embeddings collection
    if not client.has_collection("threat_embeddings"):
        client.create_collection(
            collection_name="threat_embeddings",
            dimension=1024,
            metric_type="COSINE",
            auto_id=True,
        )
        logger.info("Created collection: threat_embeddings")


class VectorService:
    """Service for vector database operations."""

    def __init__(self, client: MilvusClient = None):
        self.client = client or get_milvus_client()

    def insert_vectors(
        self,
        collection_name: str,
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Insert vectors into collection."""
        data = []
        for i, vector in enumerate(vectors):
            record = {"vector": vector}
            if metadata and i < len(metadata):
                record.update(metadata[i])
            data.append(record)
        
        result = self.client.insert(
            collection_name=collection_name,
            data=data,
        )
        return {"insert_count": result["insert_count"]}

    def search_vectors(
        self,
        collection_name: str,
        query_vectors: List[List[float]],
        top_k: int = 10,
        filter_expr: str = None,
        output_fields: List[str] = None,
    ) -> List[List[Dict[str, Any]]]:
        """Search similar vectors."""
        return self.client.search(
            collection_name=collection_name,
            data=query_vectors,
            limit=top_k,
            filter=filter_expr,
            output_fields=output_fields or ["*"],
        )

    def delete_vectors(
        self,
        collection_name: str,
        filter_expr: str,
    ) -> Dict[str, Any]:
        """Delete vectors by filter expression."""
        result = self.client.delete(
            collection_name=collection_name,
            filter=filter_expr,
        )
        return {"delete_count": result}

    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics."""
        stats = self.client.get_collection_stats(collection_name)
        return stats


# Global vector service
vector_service = VectorService()
