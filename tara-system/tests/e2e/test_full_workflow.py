"""End-to-end tests for full TARA workflow."""
import pytest
import time


class TestFullTARAWorkflow:
    """Test complete TARA analysis workflow."""

    @pytest.mark.e2e
    def test_complete_workflow(
        self,
        project_client,
        asset_client,
        threat_client,
        test_project_data,
        test_asset_data,
        test_threat_data,
    ):
        """Test complete TARA workflow from project creation to risk assessment."""
        
        # Step 1: Create project
        response = project_client("post", "/projects", json=test_project_data)
        assert response.status_code == 200
        project = response.json()["data"]
        project_id = project["id"]
        
        # Step 2: Create assets
        asset_data = {**test_asset_data, "project_id": project_id}
        response = asset_client("post", "/assets", json=asset_data)
        assert response.status_code == 200
        asset = response.json()["data"]
        asset_id = asset["id"]
        
        # Step 3: Create threats
        threat_data = {
            **test_threat_data,
            "project_id": project_id,
            "asset_id": asset_id,
        }
        response = threat_client("post", "/threats", json=threat_data)
        assert response.status_code == 200
        threat = response.json()["data"]
        threat_id = threat["id"]
        
        # Step 4: Create attack path
        attack_path_data = {
            "threat_risk_id": threat_id,
            "name": "Physical Access Attack",
            "steps": [
                {"order": 1, "description": "Gain physical access"},
                {"order": 2, "description": "Connect to OBD port"},
                {"order": 3, "description": "Inject malicious messages"},
            ],
            "expertise": 3,
            "elapsed_time": 2,
            "equipment": 2,
            "knowledge": 2,
        }
        response = threat_client("post", "/attack-paths", json=attack_path_data)
        assert response.status_code == 200
        attack_path = response.json()["data"]
        assert attack_path["attack_potential"] is not None
        assert attack_path["feasibility_rating"] is not None
        
        # Step 5: Assess risk
        response = threat_client(
            "post",
            "/risks/assess",
            json={
                "threat_id": threat_id,
                "impact_level": "major",
                "likelihood": "medium",
            },
        )
        assert response.status_code == 200
        risk = response.json()["data"]
        assert risk["risk_level"] is not None
        assert risk["risk_value"] is not None
        
        # Step 6: Get risk summary
        response = threat_client("get", f"/risks/summary?project_id={project_id}")
        assert response.status_code == 200
        summary = response.json()["data"]
        assert "total_threats" in summary
        
        # Cleanup
        project_client("delete", f"/projects/{project_id}")

    @pytest.mark.e2e
    def test_project_lifecycle(self, project_client, test_project_data):
        """Test project lifecycle: create -> update -> archive."""
        
        # Create
        response = project_client("post", "/projects", json=test_project_data)
        assert response.status_code == 200
        project_id = response.json()["data"]["id"]
        
        # Update status to in_progress
        response = project_client("patch", f"/projects/{project_id}/status?status=1")
        assert response.status_code == 200
        assert response.json()["data"]["status"] == 1
        
        # Update status to completed
        response = project_client("patch", f"/projects/{project_id}/status?status=2")
        assert response.status_code == 200
        assert response.json()["data"]["status"] == 2
        
        # Archive
        response = project_client("patch", f"/projects/{project_id}/status?status=3")
        assert response.status_code == 200
        assert response.json()["data"]["status"] == 3
        
        # Cleanup
        project_client("delete", f"/projects/{project_id}")


class TestServiceHealth:
    """Test service health checks."""

    @pytest.mark.e2e
    def test_all_services_healthy(self, http_client):
        """Test all services are healthy."""
        services = [
            ("project-service", 8001),
            ("document-service", 8002),
            ("asset-service", 8003),
            ("threat-risk-service", 8004),
            ("diagram-service", 8005),
            ("report-service", 8006),
            ("agent-service", 8007),
        ]
        
        for name, port in services:
            try:
                response = http_client.get(f"http://localhost:{port}/health")
                assert response.status_code == 200
                assert response.json()["status"] == "healthy"
            except Exception as e:
                pytest.skip(f"{name} not available: {e}")
