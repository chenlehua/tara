"""Integration tests for project API endpoints."""

import pytest


class TestProjectAPI:
    """Integration tests for project API."""

    def test_create_project(self, client, sample_project):
        """Test POST /projects creates a new project."""
        response = client.post("/api/v1/projects", json=sample_project)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == sample_project["name"]
        assert data["data"]["vehicle_type"] == sample_project["vehicle_type"]
        assert data["data"]["id"] is not None

    def test_create_project_missing_name(self, client):
        """Test POST /projects fails without required name."""
        response = client.post("/api/v1/projects", json={"description": "test"})

        assert response.status_code == 422  # Validation error

    def test_get_project(self, client, created_project):
        """Test GET /projects/{id} returns project."""
        project_id = created_project["id"]

        response = client.get(f"/api/v1/projects/{project_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == project_id

    def test_get_project_not_found(self, client):
        """Test GET /projects/{id} returns 404 for non-existent project."""
        response = client.get("/api/v1/projects/99999")

        assert response.status_code == 404

    def test_list_projects(self, client, created_project):
        """Test GET /projects returns list of projects."""
        response = client.get("/api/v1/projects")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "items" in data["data"]
        assert "total" in data["data"]

    def test_list_projects_with_pagination(self, client, created_project):
        """Test GET /projects with pagination parameters."""
        response = client.get("/api/v1/projects?page=1&page_size=10")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["page"] == 1
        assert data["data"]["page_size"] == 10

    def test_update_project(self, client, created_project):
        """Test PUT /projects/{id} updates project."""
        project_id = created_project["id"]
        update_data = {"name": "Updated Project Name"}

        response = client.put(f"/api/v1/projects/{project_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "Updated Project Name"

    def test_delete_project(self, client, created_project):
        """Test DELETE /projects/{id} deletes project."""
        project_id = created_project["id"]

        response = client.delete(f"/api/v1/projects/{project_id}")

        assert response.status_code == 200

        # Verify it's deleted
        get_response = client.get(f"/api/v1/projects/{project_id}")
        assert get_response.status_code == 404

    def test_update_project_status(self, client, created_project):
        """Test PATCH /projects/{id}/status updates status."""
        project_id = created_project["id"]

        response = client.patch(f"/api/v1/projects/{project_id}/status?status=1")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == 1

    def test_clone_project(self, client, created_project):
        """Test POST /projects/{id}/clone clones project."""
        project_id = created_project["id"]
        clone_data = {"name": "Cloned Project"}

        response = client.post(f"/api/v1/projects/{project_id}/clone", json=clone_data)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "Cloned Project"
        assert data["data"]["id"] != project_id

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
