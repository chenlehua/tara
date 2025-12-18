"""Unit tests for asset service."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from app.services.asset_service import AssetService
from app.common.schemas import AssetCreate


class TestAssetService:
    """Tests for AssetService."""

    @pytest.fixture
    def mock_repo(self):
        """Create mock repository."""
        return MagicMock()

    @pytest.fixture
    def mock_graph(self):
        """Create mock graph service."""
        return MagicMock()

    @pytest.fixture
    def service(self, mock_repo, mock_graph):
        """Create service with mocks."""
        service = AssetService(mock_repo)
        service.graph_service = mock_graph
        return service

    @pytest.mark.asyncio
    async def test_create_asset(self, service, mock_repo, mock_graph):
        """Test asset creation."""
        mock_repo.create.return_value = MagicMock(
            id=1,
            name="Test ECU",
            asset_type="ecu",
        )
        mock_graph.create_node.return_value = "node-123"

        data = AssetCreate(
            project_id=1,
            name="Test ECU",
            asset_type="ecu",
        )
        result = await service.create_asset(data)

        assert result.id == 1
        mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_asset(self, service, mock_repo):
        """Test getting an asset."""
        mock_repo.get_by_id.return_value = MagicMock(id=1, name="Test ECU")

        result = await service.get_asset(1)

        assert result.id == 1
        mock_repo.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_asset_not_found(self, service, mock_repo):
        """Test getting non-existent asset."""
        from app.common.utils.exceptions import NotFoundException

        mock_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await service.get_asset(999)

    @pytest.mark.asyncio
    async def test_list_assets(self, service, mock_repo):
        """Test listing assets."""
        mock_repo.list_assets.return_value = (
            [MagicMock(id=1), MagicMock(id=2)],
            2,
        )

        assets, total = await service.list_assets(project_id=1)

        assert len(assets) == 2
        assert total == 2

    @pytest.mark.asyncio
    async def test_delete_asset(self, service, mock_repo, mock_graph):
        """Test deleting an asset."""
        mock_repo.get_by_id.return_value = MagicMock(id=1, neo4j_node_id="node-123")

        await service.delete_asset(1)

        mock_repo.delete.assert_called_once()
        mock_graph.delete_node.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_asset_relation(self, service, mock_graph):
        """Test adding asset relation."""
        mock_graph.create_relationship.return_value = True

        result = await service.add_asset_relation(
            source_id=1,
            target_id=2,
            relation_type="connects_to",
        )

        assert result is True
        mock_graph.create_relationship.assert_called_once()
