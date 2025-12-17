"""
Document Endpoints
==================

REST API endpoints for document management and parsing.
"""

from typing import Optional

from fastapi import (APIRouter, BackgroundTasks, Depends, File, Form, Query,
                     UploadFile, status)
from sqlalchemy.orm import Session
from tara_shared.database import get_db
from tara_shared.schemas.document import (DocumentDetailResponse,
                                          DocumentResponse,
                                          DocumentUploadResponse, ParseRequest)
from tara_shared.utils import paginated_response, success_response
from tara_shared.utils.exceptions import NotFoundException, ValidationException

from ....services.document_service import DocumentService

router = APIRouter()


def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    return DocumentService(db)


@router.post("/upload", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_document(
    project_id: int = Form(..., description="项目ID"),
    file: UploadFile = File(..., description="上传的文件"),
    doc_type: Optional[str] = Form(default=None, description="文档类型"),
    service: DocumentService = Depends(get_document_service),
):
    """Upload a document file."""
    # Validate file
    if not file.filename:
        raise ValidationException("文件名不能为空")

    # Read file content
    content = await file.read()
    if len(content) == 0:
        raise ValidationException("文件内容为空")

    document = await service.upload_document(
        project_id=project_id,
        filename=file.filename,
        content=content,
        content_type=file.content_type,
        doc_type=doc_type,
    )

    return success_response(
        data=DocumentUploadResponse(
            document_id=document.id,
            filename=document.filename,
            file_path=document.file_path,
            file_size=document.file_size,
        ).model_dump(),
        message="文档上传成功",
    )


@router.post("/{document_id}/parse", response_model=dict)
async def parse_document(
    document_id: int,
    parse_request: ParseRequest,
    background_tasks: BackgroundTasks,
    service: DocumentService = Depends(get_document_service),
):
    """Parse a document (OCR + structure extraction)."""
    document = service.get_document(document_id)
    if not document:
        raise NotFoundException("Document", document_id)

    # Start parsing in background
    background_tasks.add_task(
        service.parse_document,
        document_id=document_id,
        enable_ocr=parse_request.enable_ocr,
        enable_structure=parse_request.enable_structure,
        enable_embedding=parse_request.enable_embedding,
    )

    return success_response(
        data={"document_id": document_id, "status": "parsing"},
        message="文档解析已开始",
    )


@router.get("", response_model=dict)
async def list_documents(
    project_id: int = Query(..., description="项目ID"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    doc_type: Optional[str] = Query(default=None),
    service: DocumentService = Depends(get_document_service),
):
    """List documents for a project."""
    documents, total = service.list_documents(
        project_id=project_id,
        page=page,
        page_size=page_size,
        doc_type=doc_type,
    )

    items = [DocumentResponse.model_validate(d).model_dump() for d in documents]
    return paginated_response(items=items, total=total, page=page, page_size=page_size)


@router.get("/{document_id}", response_model=dict)
async def get_document(
    document_id: int,
    include_content: bool = Query(default=False),
    service: DocumentService = Depends(get_document_service),
):
    """Get document details."""
    document = service.get_document(document_id)
    if not document:
        raise NotFoundException("Document", document_id)

    if include_content:
        response = DocumentDetailResponse.model_validate(document)
    else:
        response = DocumentResponse.model_validate(document)

    return success_response(data=response.model_dump())


@router.get("/{document_id}/content", response_model=dict)
async def get_document_content(
    document_id: int,
    service: DocumentService = Depends(get_document_service),
):
    """Get document parsed content."""
    document = service.get_document(document_id)
    if not document:
        raise NotFoundException("Document", document_id)

    return success_response(
        data={
            "document_id": document_id,
            "title": document.title,
            "content": document.content,
            "structure": document.structure,
            "metadata": document.metadata,
        }
    )


@router.delete("/{document_id}", response_model=dict)
async def delete_document(
    document_id: int,
    service: DocumentService = Depends(get_document_service),
):
    """Delete a document."""
    success = service.delete_document(document_id)
    if not success:
        raise NotFoundException("Document", document_id)

    return success_response(message="文档删除成功")


@router.post("/{document_id}/parse-extract", response_model=dict)
async def parse_and_extract(
    document_id: int,
    extract_assets: bool = Query(default=True, description="是否提取资产"),
    extract_threats: bool = Query(default=False, description="是否提取威胁"),
    background_tasks: BackgroundTasks = None,
    service: DocumentService = Depends(get_document_service),
):
    """
    Parse document and extract structured data for TARA analysis.
    
    This endpoint is the main entry for one-click report generation.
    It parses the document, extracts assets and threats, and stores them.
    """
    document = service.get_document(document_id)
    if not document:
        raise NotFoundException("Document", document_id)

    result = await service.parse_and_extract(
        document_id=document_id,
        extract_assets=extract_assets,
        extract_threats=extract_threats,
    )

    return success_response(
        data=result,
        message="文档解析和提取完成",
    )


@router.get("/{document_id}/parsed-content", response_model=dict)
async def get_parsed_content(
    document_id: int,
    service: DocumentService = Depends(get_document_service),
):
    """Get parsed content and extracted data for a document."""
    result = service.get_parsed_content(document_id)
    if not result:
        raise NotFoundException("Document", document_id)

    return success_response(data=result)


@router.get("/{document_id}/extracted-assets", response_model=dict)
async def get_extracted_assets(
    document_id: int,
    service: DocumentService = Depends(get_document_service),
):
    """Get extracted assets from a parsed document."""
    document = service.get_document(document_id)
    if not document:
        raise NotFoundException("Document", document_id)

    assets = service.get_extracted_assets(document_id)
    return success_response(
        data={"document_id": document_id, "assets": assets, "total": len(assets)}
    )
