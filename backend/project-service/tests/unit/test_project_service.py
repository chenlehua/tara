"""Unit tests for project service business logic."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from app.services.project_service import ProjectService
from tara_shared.schemas import ProjectCreate, ProjectUpdate


class TestProjectService:
    """Tests for ProjectService."""

    @pytest.fixture
    def mock_repo(self):
        """Create mock repository."""
        repo = MagicMock()
        return repo

    @pytest.fixture
    def service(self, mock_repo):
        """Create service with mock repository."""
        return ProjectService(mock_repo)

    @pytest.mark.asyncio
    async def test_create_project(self, service, mock_repo):
        """Test project creation."""
        mock_repo.create.return_value = MagicMock(
            id=1,
            name="Test Project",
            vehicle_type="BEV",
        )

        data = ProjectCreate(
            name="Test Project",
            vehicle_type="BEV",
        )
        result = await service.create_project(data)

        assert result.id == 1
        assert result.name == "Test Project"
        mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_project(self, service, mock_repo):
        """Test getting a project."""
        mock_repo.get_by_id.return_value = MagicMock(
            id=1,
            name="Test Project",
        )

        result = await service.get_project(1)

        assert result.id == 1
        mock_repo.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_project_not_found(self, service, mock_repo):
        """Test getting non-existent project."""
        from tara_shared.utils.exceptions import NotFoundException

        mock_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await service.get_project(999)

    @pytest.mark.asyncio
    async def test_list_projects(self, service, mock_repo):
        """Test listing projects."""
        mock_repo.list_projects.return_value = (
            [MagicMock(id=1), MagicMock(id=2)],
            2,
        )

        projects, total = await service.list_projects()

        assert len(projects) == 2
        assert total == 2

    @pytest.mark.asyncio
    async def test_update_project(self, service, mock_repo):
        """Test updating a project."""
        existing_project = MagicMock(id=1, name="Old Name")
        mock_repo.get_by_id.return_value = existing_project
        mock_repo.update.return_value = MagicMock(id=1, name="New Name")

        data = ProjectUpdate(name="New Name")
        result = await service.update_project(1, data)

        assert result.name == "New Name"
        mock_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_project(self, service, mock_repo):
        """Test deleting a project."""
        existing_project = MagicMock(id=1)
        mock_repo.get_by_id.return_value = existing_project

        await service.delete_project(1)

        mock_repo.delete.assert_called_once_with(existing_project)

    @pytest.mark.asyncio
    async def test_update_project_status(self, service, mock_repo):
        """Test updating project status."""
        existing_project = MagicMock(id=1, status=0)
        mock_repo.get_by_id.return_value = existing_project
        mock_repo.update.return_value = MagicMock(id=1, status=1)

        result = await service.update_project_status(1, 1)

        assert result.status == 1

    @pytest.mark.asyncio
    async def test_clone_project(self, service, mock_repo):
        """Test cloning a project."""
        original = MagicMock(
            id=1,
            name="Original",
            description="Test",
            vehicle_type="BEV",
            standard="ISO/SAE 21434",
            config={},
            tags=[],
            documents=[],
            assets=[],
            threats=[],
        )
        mock_repo.get_by_id.return_value = original
        mock_repo.create.return_value = MagicMock(id=2, name="Cloned Project")

        result = await service.clone_project(1, "Cloned Project")

        assert result.id == 2
        assert result.name == "Cloned Project"
