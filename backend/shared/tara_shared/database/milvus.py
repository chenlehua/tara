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
    _connection_error: Optional[str] = None

    @classmethod
    def get_client(cls) -> Optional[MilvusClient]:
        """Get Milvus client instance (singleton)."""
        if cls._client is None and cls._connection_error is None:
            try:
                cls._client = MilvusClient(
                    uri=f"http://{settings.milvus_host}:{settings.milvus_port}",
                    user=settings.milvus_user or None,
                    password=settings.milvus_password or None,
                )
                logger.info(f"Connected to Milvus at {settings.milvus_host}:{settings.milvus_port}")
            except Exception as e:
                cls._connection_error = str(e)
                logger.warning(f"Failed to connect to Milvus: {e}. Vector search will be unavailable.")
                return None
        return cls._client

    @classmethod
    def is_available(cls) -> bool:
        """Check if Milvus is available."""
        return cls.get_client() is not None

    @classmethod
    def close(cls) -> None:
        """Close Milvus connection."""
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            cls._connection_error = None


def get_milvus_client() -> Optional[MilvusClient]:
    """Get Milvus client for dependency injection."""
    return MilvusManager.get_client()


def init_milvus() -> None:
    """Initialize Milvus collections."""
    client = get_milvus_client()
    
    if client is None:
        logger.warning("Milvus not available, skipping collection initialization")
        return
    
    try:
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
    except Exception as e:
        logger.warning(f"Failed to initialize Milvus collections: {e}")


class VectorService:
    """Service for vector database operations."""

    def __init__(self, client: MilvusClient = None):
        self._client = client
        self._lazy_client = client is None

    @property
    def client(self) -> Optional[MilvusClient]:
        """Get client with lazy initialization."""
        if self._lazy_client and self._client is None:
            self._client = get_milvus_client()
        return self._client

    def is_available(self) -> bool:
        """Check if vector service is available."""
        return self.client is not None

    def insert_vectors(
        self,
        collection_name: str,
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Insert vectors into collection."""
        if not self.is_available():
            logger.warning("Milvus not available, skipping vector insert")
            return {"insert_count": 0}
        
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
        if not self.is_available():
            logger.warning("Milvus not available, returning empty search results")
            return []
        
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
        if not self.is_available():
            logger.warning("Milvus not available, skipping vector delete")
            return {"delete_count": 0}
        
        result = self.client.delete(
            collection_name=collection_name,
            filter=filter_expr,
        )
        return {"delete_count": result}

    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics."""
        if not self.is_available():
            return {"row_count": 0}
        
        stats = self.client.get_collection_stats(collection_name)
        return stats


def get_vector_service() -> VectorService:
    """Get vector service instance (lazy initialization)."""
    return VectorService()


# Lazy-initialized global vector service
vector_service: Optional[VectorService] = None


def get_global_vector_service() -> VectorService:
    """Get global vector service with lazy initialization."""
    global vector_service
    if vector_service is None:
        vector_service = VectorService()
    return vector_service
