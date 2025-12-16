"""
ElasticSearch Connection
========================

ElasticSearch client for full-text search.
"""

from typing import Any, Dict, List, Optional

from elasticsearch import Elasticsearch

from ..config import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ESClient:
    """ElasticSearch client wrapper."""

    _client: Optional[Elasticsearch] = None
    _connection_error: Optional[str] = None

    @classmethod
    def get_client(cls) -> Optional[Elasticsearch]:
        """Get ElasticSearch client instance (singleton)."""
        if cls._client is None and cls._connection_error is None:
            try:
                cls._client = Elasticsearch(
                    hosts=[settings.es_url],
                    basic_auth=(settings.es_user, settings.es_password),
                    verify_certs=False,
                    request_timeout=30,
                    max_retries=3,
                    retry_on_timeout=True,
                )
                # Test connection
                if cls._client.ping():
                    logger.info(f"Connected to ElasticSearch at {settings.es_url}")
                else:
                    raise Exception("Ping failed")
            except Exception as e:
                cls._connection_error = str(e)
                logger.warning(
                    f"Failed to connect to ElasticSearch: {e}. Search will be unavailable."
                )
                cls._client = None
        return cls._client

    @classmethod
    def is_available(cls) -> bool:
        """Check if ElasticSearch is available."""
        return cls.get_client() is not None

    @classmethod
    def close(cls) -> None:
        """Close ElasticSearch connection."""
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            cls._connection_error = None

    @classmethod
    def is_healthy(cls) -> bool:
        """Check if ElasticSearch is healthy."""
        client = cls.get_client()
        if client is None:
            return False
        try:
            return client.ping()
        except Exception as e:
            logger.error(f"ElasticSearch health check failed: {e}")
            return False


def get_es_client() -> Optional[Elasticsearch]:
    """Get ElasticSearch client for dependency injection."""
    return ESClient.get_client()


# Lazy-initialized global client
es_client: Optional[Elasticsearch] = None


def get_global_es_client() -> Optional[Elasticsearch]:
    """Get global ElasticSearch client with lazy initialization."""
    global es_client
    if es_client is None:
        es_client = ESClient.get_client()
    return es_client


class SearchService:
    """Service for search operations."""

    # Index mappings
    DOCUMENT_INDEX_MAPPING = {
        "mappings": {
            "properties": {
                "project_id": {"type": "keyword"},
                "document_id": {"type": "keyword"},
                "title": {"type": "text", "analyzer": "ik_max_word"},
                "content": {"type": "text", "analyzer": "ik_max_word"},
                "doc_type": {"type": "keyword"},
                "created_at": {"type": "date"},
            }
        }
    }

    THREAT_INDEX_MAPPING = {
        "mappings": {
            "properties": {
                "threat_id": {"type": "keyword"},
                "name": {"type": "text", "analyzer": "ik_max_word"},
                "description": {"type": "text", "analyzer": "ik_max_word"},
                "category": {"type": "keyword"},
                "stride_type": {"type": "keyword"},
                "severity": {"type": "keyword"},
            }
        }
    }

    def __init__(self, client: Elasticsearch = None):
        self._client = client
        self._lazy_client = client is None

    @property
    def client(self) -> Optional[Elasticsearch]:
        """Get client with lazy initialization."""
        if self._lazy_client and self._client is None:
            self._client = get_es_client()
        return self._client

    def is_available(self) -> bool:
        """Check if search service is available."""
        return self.client is not None

    def create_index(self, index_name: str, mapping: Dict[str, Any]) -> bool:
        """Create an index with mapping."""
        if not self.is_available():
            logger.warning("ElasticSearch not available, skipping index creation")
            return False
        try:
            if not self.client.indices.exists(index=index_name):
                self.client.indices.create(index=index_name, body=mapping)
                logger.info(f"Created index: {index_name}")
                return True
        except Exception as e:
            logger.warning(f"Failed to create index {index_name}: {e}")
        return False

    def init_indices(self) -> None:
        """Initialize all required indices."""
        if not self.is_available():
            logger.warning(
                "ElasticSearch not available, skipping indices initialization"
            )
            return
        self.create_index("tara_documents", self.DOCUMENT_INDEX_MAPPING)
        self.create_index("tara_threats", self.THREAT_INDEX_MAPPING)

    def index_document(
        self,
        index_name: str,
        doc_id: str,
        document: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Index a document."""
        if not self.is_available():
            logger.warning("ElasticSearch not available, skipping document indexing")
            return {}
        return self.client.index(
            index=index_name,
            id=doc_id,
            body=document,
            refresh=True,
        )

    def search(
        self,
        index_name: str,
        query: str,
        fields: List[str] = None,
        size: int = 10,
        filters: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """Full-text search."""
        if not self.is_available():
            logger.warning(
                "ElasticSearch not available, returning empty search results"
            )
            return []

        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": fields or ["*"],
                                "type": "best_fields",
                            }
                        }
                    ]
                }
            },
            "size": size,
        }

        if filters:
            body["query"]["bool"]["filter"] = [
                {"term": {k: v}} for k, v in filters.items()
            ]

        try:
            result = self.client.search(index=index_name, body=body)
            return [
                {
                    "id": hit["_id"],
                    "score": hit["_score"],
                    **hit["_source"],
                }
                for hit in result["hits"]["hits"]
            ]
        except Exception as e:
            logger.warning(f"Search failed: {e}")
            return []

    def delete_document(self, index_name: str, doc_id: str) -> bool:
        """Delete a document by ID."""
        if not self.is_available():
            return False
        try:
            self.client.delete(index=index_name, id=doc_id, refresh=True)
            return True
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False

    def bulk_index(
        self,
        index_name: str,
        documents: List[Dict[str, Any]],
        id_field: str = "id",
    ) -> Dict[str, Any]:
        """Bulk index documents."""
        if not self.is_available():
            logger.warning("ElasticSearch not available, skipping bulk indexing")
            return {"indexed": 0, "failed": len(documents)}
        from elasticsearch.helpers import bulk

        actions = [
            {
                "_index": index_name,
                "_id": doc.get(id_field),
                "_source": doc,
            }
            for doc in documents
        ]

        success, failed = bulk(self.client, actions, refresh=True)
        return {"success": success, "failed": len(failed)}


# Lazy-initialized global search service
search_service: Optional[SearchService] = None


def get_search_service() -> SearchService:
    """Get global search service with lazy initialization."""
    global search_service
    if search_service is None:
        search_service = SearchService()
    return search_service
