"""
Document Repository
===================

Data access layer for Document entity.
"""

from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session
from tara_shared.models import Document


class DocumentRepository:
    """Repository for Document data access."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, document: Document) -> Document:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_by_id(self, document_id: int) -> Optional[Document]:
        return self.db.query(Document).filter(Document.id == document_id).first()

    def list_documents(
        self,
        project_id: int,
        page: int = 1,
        page_size: int = 20,
        doc_type: str = None,
    ) -> Tuple[List[Document], int]:
        query = self.db.query(Document).filter(Document.project_id == project_id)

        if doc_type:
            query = query.filter(Document.doc_type == doc_type)

        total = query.count()
        offset = (page - 1) * page_size
        documents = (
            query.order_by(Document.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return documents, total

    def update(self, document: Document) -> Document:
        self.db.commit()
        self.db.refresh(document)
        return document

    def delete(self, document: Document) -> None:
        self.db.delete(document)
        self.db.commit()
