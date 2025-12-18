"""User scenario tests for TARA system."""
import pytest


class TestSecurityAnalystScenarios:
    """Test scenarios for security analyst users."""

    @pytest.mark.e2e
    def test_analyst_creates_new_assessment(
        self,
        project_client,
        asset_client,
        threat_client,
        test_project_data,
    ):
        """
        Scenario: Security analyst creates a new TARA assessment
        Given: Analyst has access to the system
        When: Analyst creates project, adds assets, identifies threats
        Then: System calculates risks and provides recommendations
        """
        # Create new project
        response = project_client("post", "/projects", json=test_project_data)
        assert response.status_code == 200
        project_id = response.json()["data"]["id"]
        
        # Add multiple assets
        assets = [
            {"name": "Gateway ECU", "asset_type": "gateway", "project_id": project_id},
            {"name": "Engine ECU", "asset_type": "ecu", "project_id": project_id},
            {"name": "CAN Bus", "asset_type": "bus", "project_id": project_id},
        ]
        
        asset_ids = []
        for asset in assets:
            response = asset_client("post", "/assets", json=asset)
            assert response.status_code == 200
            asset_ids.append(response.json()["data"]["id"])
        
        # Identify threats for each asset
        for asset_id in asset_ids:
            threat_data = {
                "project_id": project_id,
                "asset_id": asset_id,
                "threat_name": f"Threat for asset {asset_id}",
                "threat_type": "Tampering",
            }
            response = threat_client("post", "/threats", json=threat_data)
            assert response.status_code == 200
        
        # Get project overview
        response = project_client("get", f"/projects/{project_id}?include_stats=true")
        assert response.status_code == 200
        
        # Cleanup
        project_client("delete", f"/projects/{project_id}")

    @pytest.mark.e2e
    def test_analyst_reviews_existing_assessment(self, project_client):
        """
        Scenario: Analyst reviews an existing TARA assessment
        Given: A completed TARA project exists
        When: Analyst views project details
        Then: System shows all assets, threats, and risks
        """
        # List projects
        response = project_client("get", "/projects")
        assert response.status_code == 200
        
        projects = response.json()["data"]["items"]
        if projects:
            project_id = projects[0]["id"]
            
            # Get detailed project info
            response = project_client("get", f"/projects/{project_id}")
            assert response.status_code == 200


class TestProjectManagerScenarios:
    """Test scenarios for project manager users."""

    @pytest.mark.e2e
    def test_manager_monitors_project_status(self, project_client, test_project_data):
        """
        Scenario: Project manager monitors TARA project status
        Given: Multiple TARA projects exist
        When: Manager views project list
        Then: System shows status and progress of each project
        """
        # Create multiple projects
        project_ids = []
        for i in range(3):
            data = {**test_project_data, "name": f"Test Project {i}"}
            response = project_client("post", "/projects", json=data)
            project_ids.append(response.json()["data"]["id"])
        
        # List all projects
        response = project_client("get", "/projects")
        assert response.status_code == 200
        assert response.json()["data"]["total"] >= 3
        
        # Get stats for each project
        for project_id in project_ids:
            response = project_client("get", f"/projects/{project_id}/stats")
            assert response.status_code == 200
        
        # Cleanup
        for project_id in project_ids:
            project_client("delete", f"/projects/{project_id}")

    @pytest.mark.e2e
    def test_manager_clones_project_template(self, project_client, test_project_data):
        """
        Scenario: Manager clones an existing project as template
        Given: A completed project exists
        When: Manager clones the project
        Then: New project is created with same structure
        """
        # Create original project
        response = project_client("post", "/projects", json=test_project_data)
        original_id = response.json()["data"]["id"]
        
        # Clone the project
        clone_data = {"name": "Cloned Project"}
        response = project_client("post", f"/projects/{original_id}/clone", json=clone_data)
        assert response.status_code == 200
        cloned_id = response.json()["data"]["id"]
        
        assert cloned_id != original_id
        
        # Cleanup
        project_client("delete", f"/projects/{original_id}")
        project_client("delete", f"/projects/{cloned_id}")
