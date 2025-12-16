"""
Asset Repository
================

Data access layer for Asset entity.
"""

from typing import List, Optional, Tuple

from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from tara_shared.models import Asset


class AssetRepository:
    """Repository for Asset data access."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, asset: Asset) -> Asset:
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def get_by_id(self, asset_id: int) -> Optional[Asset]:
        return self.db.query(Asset).filter(Asset.id == asset_id).first()

    def get_all_by_project(self, project_id: int) -> List[Asset]:
        return self.db.query(Asset).filter(Asset.project_id == project_id).all()

    def list_assets(
        self,
        project_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
        asset_type: str = None,
        category: str = None,
        keyword: str = None,
    ) -> Tuple[List[Asset], int]:
        query = self.db.query(Asset)

        if project_id is not None:
            query = query.filter(Asset.project_id == project_id)

        if asset_type:
            query = query.filter(Asset.asset_type == asset_type)

        if category:
            query = query.filter(Asset.category == category)

        if keyword:
            query = query.filter(
                or_(
                    Asset.name.ilike(f"%{keyword}%"),
                    Asset.description.ilike(f"%{keyword}%"),
                )
            )

        total = query.count()
        offset = (page - 1) * page_size
        assets = (
            query.order_by(Asset.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return assets, total

    def update(self, asset: Asset) -> Asset:
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def delete(self, asset: Asset) -> None:
        self.db.delete(asset)
        self.db.commit()
