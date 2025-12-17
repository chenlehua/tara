"""
Knowledge Base Endpoints
========================

REST API endpoints for knowledge base management.
Supports document upload, chunking, vector storage, and hybrid search.
"""

from typing import List, Optional

from fastapi import APIRouter, File, Form, Query, UploadFile, status
from tara_shared.utils import paginated_response, success_response
from tara_shared.utils.exceptions import NotFoundException, ValidationException

from ....services.knowledge_service import KnowledgeService

router = APIRouter()


def get_knowledge_service() -> KnowledgeService:
    return KnowledgeService()


@router.post("/documents/upload", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(..., description="上传的文档"),
    project_id: Optional[int] = Form(default=None, description="关联项目ID"),
    category: str = Form(default="general", description="知识分类"),
    tags: str = Form(default="", description="标签，逗号分隔"),
):
    """
    Upload a document to the knowledge base.
    
    The document will be:
    1. Stored in MinIO/local storage
    2. Parsed and chunked
    3. Indexed in Elasticsearch for full-text search
    4. Vectorized and stored in Milvus for semantic search
    """
    service = get_knowledge_service()
    
    if not file.filename:
        raise ValidationException("文件名不能为空")
    
    content = await file.read()
    if len(content) == 0:
        raise ValidationException("文件内容为空")
    
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    
    result = await service.upload_and_process(
        filename=file.filename,
        content=content,
        content_type=file.content_type,
        project_id=project_id,
        category=category,
        tags=tag_list,
    )
    
    return success_response(
        data=result,
        message="文档上传并处理成功",
    )


@router.get("/documents", response_model=dict)
async def list_documents(
    project_id: Optional[int] = Query(default=None, description="项目ID"),
    category: Optional[str] = Query(default=None, description="分类"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    """List documents in the knowledge base."""
    service = get_knowledge_service()
    
    documents, total = service.list_documents(
        project_id=project_id,
        category=category,
        page=page,
        page_size=page_size,
    )
    
    return paginated_response(
        items=documents,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/documents/{document_id}", response_model=dict)
async def get_document(document_id: str):
    """Get document details and chunks."""
    service = get_knowledge_service()
    
    document = service.get_document(document_id)
    if not document:
        raise NotFoundException("Knowledge Document", document_id)
    
    return success_response(data=document)


@router.delete("/documents/{document_id}", response_model=dict)
async def delete_document(document_id: str):
    """Delete a document from the knowledge base."""
    service = get_knowledge_service()
    
    success = await service.delete_document(document_id)
    if not success:
        raise NotFoundException("Knowledge Document", document_id)
    
    return success_response(message="文档删除成功")


@router.post("/search", response_model=dict)
async def search_knowledge(
    query: str = Query(..., min_length=1, description="搜索查询"),
    search_type: str = Query(default="hybrid", description="搜索类型: vector, fulltext, hybrid"),
    project_id: Optional[int] = Query(default=None, description="限定项目"),
    category: Optional[str] = Query(default=None, description="限定分类"),
    top_k: int = Query(default=10, ge=1, le=50, description="返回结果数"),
):
    """
    Search the knowledge base.
    
    Supports three search modes:
    - vector: Semantic similarity search using embeddings
    - fulltext: Traditional full-text search with keyword matching
    - hybrid: Combination of both for best results
    """
    service = get_knowledge_service()
    
    results = await service.search(
        query=query,
        search_type=search_type,
        project_id=project_id,
        category=category,
        top_k=top_k,
    )
    
    return success_response(
        data={
            "query": query,
            "search_type": search_type,
            "results": results,
            "total": len(results),
        }
    )


@router.post("/documents/{document_id}/reindex", response_model=dict)
async def reindex_document(document_id: str):
    """Re-process and re-index a document."""
    service = get_knowledge_service()
    
    success = await service.reindex_document(document_id)
    if not success:
        raise NotFoundException("Knowledge Document", document_id)
    
    return success_response(message="文档重新索引成功")


@router.get("/stats", response_model=dict)
async def get_stats():
    """Get knowledge base statistics."""
    service = get_knowledge_service()
    
    stats = service.get_stats()
    
    return success_response(data=stats)


@router.get("/categories", response_model=dict)
async def list_categories():
    """List all knowledge categories."""
    service = get_knowledge_service()
    
    categories = service.list_categories()
    
    return success_response(data={"categories": categories})
