"""
Knowledge Base Service
======================

Business logic for knowledge base management.
Handles document processing, chunking, embedding, and hybrid search.
"""

import hashlib
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx
from app.common.config import settings
from app.common.database.elasticsearch import SearchService, get_search_service
from app.common.database.milvus import VectorService, get_global_vector_service
from app.common.utils import get_logger

logger = get_logger(__name__)

# Local storage path for knowledge documents
KNOWLEDGE_STORAGE_DIR = Path("/tmp/knowledge_base")
KNOWLEDGE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Index and collection names
ES_INDEX = "tara_knowledge"
MILVUS_COLLECTION = "knowledge_embeddings"

# Embedding dimension (Qwen3-Embedding)
EMBEDDING_DIM = 1024


class KnowledgeService:
    """Service for knowledge base operations."""

    def __init__(self):
        self.search_service = get_search_service()
        self.vector_service = get_global_vector_service()
        self._documents_cache: Dict[str, Dict] = {}

    def init_storage(self) -> None:
        """Initialize Elasticsearch index and Milvus collection."""
        # Initialize ES index
        if self.search_service.is_available():
            mapping = {
                "mappings": {
                    "properties": {
                        "document_id": {"type": "keyword"},
                        "chunk_id": {"type": "keyword"},
                        "project_id": {"type": "keyword"},
                        "filename": {"type": "text", "analyzer": "ik_max_word"},
                        "category": {"type": "keyword"},
                        "tags": {"type": "keyword"},
                        "content": {"type": "text", "analyzer": "ik_max_word"},
                        "chunk_index": {"type": "integer"},
                        "total_chunks": {"type": "integer"},
                        "created_at": {"type": "date"},
                    }
                }
            }
            self.search_service.create_index(ES_INDEX, mapping)
            logger.info(f"Initialized ES index: {ES_INDEX}")

        # Initialize Milvus collection
        if self.vector_service.is_available():
            try:
                client = self.vector_service.client
                if not client.has_collection(MILVUS_COLLECTION):
                    client.create_collection(
                        collection_name=MILVUS_COLLECTION,
                        dimension=EMBEDDING_DIM,
                        metric_type="COSINE",
                        auto_id=True,
                    )
                    logger.info(f"Created Milvus collection: {MILVUS_COLLECTION}")
            except Exception as e:
                logger.warning(f"Failed to initialize Milvus collection: {e}")

    async def upload_and_process(
        self,
        filename: str,
        content: bytes,
        content_type: str,
        project_id: Optional[int] = None,
        category: str = "general",
        tags: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload and process a document.
        
        Steps:
        1. Store document locally/MinIO
        2. Parse document content
        3. Chunk content into segments
        4. Generate embeddings for each chunk
        5. Store in ES and Milvus
        """
        document_id = str(uuid.uuid4())
        tags = tags or []
        
        # Store document
        file_path = KNOWLEDGE_STORAGE_DIR / document_id / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Stored document: {document_id} - {filename}")
        
        # Parse document
        text_content = await self._parse_document(content, filename, content_type)
        
        # Chunk content
        chunks = self._chunk_content(text_content)
        
        logger.info(f"Document {document_id} chunked into {len(chunks)} segments")
        
        # Generate embeddings and store
        successful_chunks = 0
        for i, chunk in enumerate(chunks):
            try:
                chunk_id = f"{document_id}_{i}"
                
                # Store in ES
                es_doc = {
                    "document_id": document_id,
                    "chunk_id": chunk_id,
                    "project_id": str(project_id) if project_id else None,
                    "filename": filename,
                    "category": category,
                    "tags": tags,
                    "content": chunk,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "created_at": datetime.now().isoformat(),
                }
                
                if self.search_service.is_available():
                    self.search_service.index_document(ES_INDEX, chunk_id, es_doc)
                
                # Generate embedding and store in Milvus
                embedding = await self._generate_embedding(chunk)
                if embedding and self.vector_service.is_available():
                    self.vector_service.insert_vectors(
                        MILVUS_COLLECTION,
                        [embedding],
                        [{"chunk_id": chunk_id, "document_id": document_id}],
                    )
                
                successful_chunks += 1
                
            except Exception as e:
                logger.error(f"Failed to process chunk {i}: {e}")
        
        # Cache document metadata
        doc_meta = {
            "document_id": document_id,
            "filename": filename,
            "file_path": str(file_path),
            "project_id": project_id,
            "category": category,
            "tags": tags,
            "total_chunks": len(chunks),
            "indexed_chunks": successful_chunks,
            "content_length": len(text_content),
            "created_at": datetime.now().isoformat(),
        }
        self._documents_cache[document_id] = doc_meta
        
        return doc_meta

    async def _parse_document(
        self,
        content: bytes,
        filename: str,
        content_type: str,
    ) -> str:
        """Parse document content to text."""
        ext = Path(filename).suffix.lower()
        
        try:
            if ext in [".txt", ".md", ".csv"]:
                return content.decode("utf-8", errors="ignore")
            
            elif ext == ".json":
                import json
                data = json.loads(content.decode("utf-8"))
                return json.dumps(data, ensure_ascii=False, indent=2)
            
            elif ext == ".pdf":
                # Try pypdf for PDF parsing
                try:
                    from pypdf import PdfReader
                    import io
                    reader = PdfReader(io.BytesIO(content))
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text
                except ImportError:
                    logger.warning("pypdf not installed, PDF parsing unavailable")
                    return f"[PDF文件: {filename}]"
            
            elif ext in [".docx", ".doc"]:
                # Try python-docx for Word documents
                try:
                    from docx import Document
                    import io
                    doc = Document(io.BytesIO(content))
                    text = "\n".join([p.text for p in doc.paragraphs])
                    return text
                except ImportError:
                    logger.warning("python-docx not installed, Word parsing unavailable")
                    return f"[Word文件: {filename}]"
            
            else:
                # Try to decode as text
                return content.decode("utf-8", errors="ignore")
                
        except Exception as e:
            logger.error(f"Failed to parse document: {e}")
            return f"[解析失败: {filename}]"

    def _chunk_content(
        self,
        content: str,
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> List[str]:
        """Split content into overlapping chunks."""
        if not content:
            return []
        
        # Clean content
        content = re.sub(r'\s+', ' ', content).strip()
        
        if len(content) <= chunk_size:
            return [content]
        
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(content):
                # Look for sentence ending
                for sep in ["。", ".", "!", "?", "\n"]:
                    last_sep = content[start:end].rfind(sep)
                    if last_sep > chunk_size // 2:
                        end = start + last_sep + 1
                        break
            
            chunk = content[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move forward with overlap
            start = end - overlap
        
        return chunks

    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using embedding service."""
        try:
            embedding_url = getattr(settings, 'embedding_url', 'http://localhost:8080')
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{embedding_url}/embeddings",
                    json={
                        "input": text[:2000],  # Limit input length
                        "model": "qwen3-embedding",
                    },
                    timeout=30.0,
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # Handle different response formats
                    if "data" in result and len(result["data"]) > 0:
                        return result["data"][0].get("embedding", [])
                    elif "embedding" in result:
                        return result["embedding"]
                        
        except Exception as e:
            logger.warning(f"Embedding generation failed: {e}")
        
        # Return zero vector as fallback
        return [0.0] * EMBEDDING_DIM

    async def search(
        self,
        query: str,
        search_type: str = "hybrid",
        project_id: Optional[int] = None,
        category: Optional[str] = None,
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search the knowledge base.
        
        search_type:
        - vector: Semantic similarity search
        - fulltext: Elasticsearch full-text search
        - hybrid: Combination of both
        """
        results = []
        
        if search_type in ["fulltext", "hybrid"]:
            # Full-text search via ES
            es_results = await self._fulltext_search(query, project_id, category, top_k)
            results.extend(es_results)
        
        if search_type in ["vector", "hybrid"]:
            # Vector search via Milvus
            vector_results = await self._vector_search(query, project_id, category, top_k)
            results.extend(vector_results)
        
        # Deduplicate and re-rank for hybrid search
        if search_type == "hybrid":
            results = self._dedupe_and_rerank(results, top_k)
        
        return results[:top_k]

    async def _fulltext_search(
        self,
        query: str,
        project_id: Optional[int],
        category: Optional[str],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """Full-text search via Elasticsearch."""
        if not self.search_service.is_available():
            return []
        
        filters = {}
        if project_id:
            filters["project_id"] = str(project_id)
        if category:
            filters["category"] = category
        
        results = self.search_service.search(
            index_name=ES_INDEX,
            query=query,
            fields=["content", "filename"],
            size=top_k,
            filters=filters if filters else None,
        )
        
        return [
            {
                "chunk_id": r.get("chunk_id", r.get("id")),
                "document_id": r.get("document_id"),
                "filename": r.get("filename"),
                "content": r.get("content", "")[:300] + "...",
                "score": r.get("score", 0),
                "search_type": "fulltext",
            }
            for r in results
        ]

    async def _vector_search(
        self,
        query: str,
        project_id: Optional[int],
        category: Optional[str],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """Vector similarity search via Milvus."""
        if not self.vector_service.is_available():
            return []
        
        # Generate query embedding
        query_embedding = await self._generate_embedding(query)
        if not query_embedding:
            return []
        
        # Search Milvus
        search_results = self.vector_service.search_vectors(
            collection_name=MILVUS_COLLECTION,
            query_vectors=[query_embedding],
            top_k=top_k,
        )
        
        results = []
        for hits in search_results:
            for hit in hits:
                chunk_id = hit.get("chunk_id") or hit.get("entity", {}).get("chunk_id")
                document_id = hit.get("document_id") or hit.get("entity", {}).get("document_id")
                
                # Fetch content from ES
                content = ""
                if self.search_service.is_available() and chunk_id:
                    try:
                        client = self.search_service.client
                        doc = client.get(index=ES_INDEX, id=chunk_id)
                        content = doc.get("_source", {}).get("content", "")
                    except Exception:
                        pass
                
                results.append({
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "content": content[:300] + "..." if len(content) > 300 else content,
                    "score": hit.get("distance", 0),
                    "search_type": "vector",
                })
        
        return results

    def _dedupe_and_rerank(
        self,
        results: List[Dict],
        top_k: int,
    ) -> List[Dict]:
        """Deduplicate and rerank hybrid search results."""
        seen = set()
        unique_results = []
        
        for r in results:
            chunk_id = r.get("chunk_id")
            if chunk_id and chunk_id not in seen:
                seen.add(chunk_id)
                # Boost score for results found in both searches
                r["hybrid_score"] = r.get("score", 0)
                unique_results.append(r)
            elif chunk_id in seen:
                # Found in both - boost the existing result
                for existing in unique_results:
                    if existing.get("chunk_id") == chunk_id:
                        existing["hybrid_score"] = existing.get("hybrid_score", 0) + r.get("score", 0)
                        existing["search_type"] = "hybrid"
                        break
        
        # Sort by hybrid score
        unique_results.sort(key=lambda x: x.get("hybrid_score", 0), reverse=True)
        
        return unique_results[:top_k]

    def list_documents(
        self,
        project_id: Optional[int] = None,
        category: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Dict], int]:
        """List documents in the knowledge base."""
        # For now, use in-memory cache
        # In production, this should query a database
        documents = list(self._documents_cache.values())
        
        # Filter
        if project_id:
            documents = [d for d in documents if d.get("project_id") == project_id]
        if category:
            documents = [d for d in documents if d.get("category") == category]
        
        total = len(documents)
        
        # Paginate
        start = (page - 1) * page_size
        end = start + page_size
        
        return documents[start:end], total

    def get_document(self, document_id: str) -> Optional[Dict]:
        """Get document details."""
        return self._documents_cache.get(document_id)

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from the knowledge base."""
        if document_id not in self._documents_cache:
            return False
        
        doc = self._documents_cache[document_id]
        
        # Delete from ES
        if self.search_service.is_available():
            for i in range(doc.get("total_chunks", 0)):
                chunk_id = f"{document_id}_{i}"
                self.search_service.delete_document(ES_INDEX, chunk_id)
        
        # Delete from Milvus
        if self.vector_service.is_available():
            try:
                self.vector_service.delete_vectors(
                    MILVUS_COLLECTION,
                    f'document_id == "{document_id}"',
                )
            except Exception as e:
                logger.warning(f"Failed to delete vectors: {e}")
        
        # Delete file
        file_path = Path(doc.get("file_path", ""))
        if file_path.exists():
            file_path.unlink()
            if file_path.parent.exists():
                try:
                    file_path.parent.rmdir()
                except OSError:
                    pass
        
        # Remove from cache
        del self._documents_cache[document_id]
        
        return True

    async def reindex_document(self, document_id: str) -> bool:
        """Re-process and re-index a document."""
        if document_id not in self._documents_cache:
            return False
        
        doc = self._documents_cache[document_id]
        file_path = Path(doc.get("file_path", ""))
        
        if not file_path.exists():
            return False
        
        # Read content and re-process
        with open(file_path, "rb") as f:
            content = f.read()
        
        # Delete existing chunks
        await self.delete_document(document_id)
        
        # Re-upload with same ID
        await self.upload_and_process(
            filename=doc.get("filename"),
            content=content,
            content_type="application/octet-stream",
            project_id=doc.get("project_id"),
            category=doc.get("category"),
            tags=doc.get("tags", []),
        )
        
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        stats = {
            "total_documents": len(self._documents_cache),
            "total_chunks": sum(d.get("total_chunks", 0) for d in self._documents_cache.values()),
            "categories": list(set(d.get("category") for d in self._documents_cache.values())),
            "es_available": self.search_service.is_available(),
            "milvus_available": self.vector_service.is_available(),
        }
        
        # Get ES stats
        if self.search_service.is_available():
            try:
                client = self.search_service.client
                if client.indices.exists(index=ES_INDEX):
                    index_stats = client.indices.stats(index=ES_INDEX)
                    stats["es_doc_count"] = index_stats.get("_all", {}).get("primaries", {}).get("docs", {}).get("count", 0)
            except Exception:
                pass
        
        # Get Milvus stats
        if self.vector_service.is_available():
            try:
                milvus_stats = self.vector_service.get_collection_stats(MILVUS_COLLECTION)
                stats["milvus_row_count"] = milvus_stats.get("row_count", 0)
            except Exception:
                pass
        
        return stats

    def list_categories(self) -> List[str]:
        """List all knowledge categories."""
        categories = set()
        for doc in self._documents_cache.values():
            cat = doc.get("category")
            if cat:
                categories.add(cat)
        
        # Add default categories
        default_categories = [
            "general",
            "threat_library",
            "control_library",
            "standard",
            "regulation",
            "best_practice",
        ]
        categories.update(default_categories)
        
        return sorted(list(categories))
