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

    @classmethod
    def get_client(cls) -> Elasticsearch:
        """Get ElasticSearch client instance (singleton)."""
        if cls._client is None:
            cls._client = Elasticsearch(
                hosts=[settings.es_url],
                basic_auth=(settings.es_user, settings.es_password),
                verify_certs=False,
                request_timeout=30,
                max_retries=3,
                retry_on_timeout=True,
            )
        return cls._client

    @classmethod
    def close(cls) -> None:
        """Close ElasticSearch connection."""
        if cls._client is not None:
            cls._client.close()
            cls._client = None

    @classmethod
    def is_healthy(cls) -> bool:
        """Check if ElasticSearch is healthy."""
        try:
            return cls.get_client().ping()
        except Exception as e:
            logger.error(f"ElasticSearch health check failed: {e}")
            return False


# Global client instance
es_client = ESClient.get_client()


def get_es_client() -> Elasticsearch:
    """Get ElasticSearch client for dependency injection."""
    return ESClient.get_client()


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
        self.client = client or es_client

    def create_index(self, index_name: str, mapping: Dict[str, Any]) -> bool:
        """Create an index with mapping."""
        if not self.client.indices.exists(index=index_name):
            self.client.indices.create(index=index_name, body=mapping)
            logger.info(f"Created index: {index_name}")
            return True
        return False

    def init_indices(self) -> None:
        """Initialize all required indices."""
        self.create_index("tara_documents", self.DOCUMENT_INDEX_MAPPING)
        self.create_index("tara_threats", self.THREAT_INDEX_MAPPING)

    def index_document(
        self,
        index_name: str,
        doc_id: str,
        document: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Index a document."""
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

        result = self.client.search(index=index_name, body=body)
        return [
            {
                "id": hit["_id"],
                "score": hit["_score"],
                **hit["_source"],
            }
            for hit in result["hits"]["hits"]
        ]

    def delete_document(self, index_name: str, doc_id: str) -> bool:
        """Delete a document by ID."""
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


# Global search service
search_service = SearchService()
