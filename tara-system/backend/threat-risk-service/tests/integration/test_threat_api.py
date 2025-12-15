"""Integration tests for threat API endpoints."""
import pytest


class TestThreatAPI:
    """Integration tests for threat API."""

    def test_create_threat(self, client, test_project, sample_threat):
        """Test POST /threats creates a new threat."""
        data = {
            **sample_threat,
            "project_id": test_project.id,
        }
        
        response = client.post("/api/v1/threats", json=data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["data"]["threat_name"] == sample_threat["threat_name"]

    def test_list_threats(self, client, test_project):
        """Test GET /threats returns list of threats."""
        response = client.get(f"/api/v1/threats?project_id={test_project.id}")
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "items" in result["data"]

    def test_get_threat_detail(self, client, test_project, sample_threat):
        """Test GET /threats/{id} returns threat details."""
        # First create a threat
        data = {**sample_threat, "project_id": test_project.id}
        create_response = client.post("/api/v1/threats", json=data)
        threat_id = create_response.json()["data"]["id"]
        
        # Get the threat
        response = client.get(f"/api/v1/threats/{threat_id}")
        
        assert response.status_code == 200
        result = response.json()
        assert result["data"]["id"] == threat_id


class TestRiskAPI:
    """Integration tests for risk API."""

    def test_get_risk_matrix(self, client, test_project):
        """Test GET /risks/matrix returns risk matrix."""
        response = client.get(f"/api/v1/risks/matrix?project_id={test_project.id}")
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True

    def test_get_risk_summary(self, client, test_project):
        """Test GET /risks/summary returns risk summary."""
        response = client.get(f"/api/v1/risks/summary?project_id={test_project.id}")
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True


class TestAttackPathAPI:
    """Integration tests for attack path API."""

    def test_create_attack_path(self, client, test_project, sample_threat, sample_attack_path):
        """Test POST /attack-paths creates new attack path."""
        # First create a threat
        threat_data = {**sample_threat, "project_id": test_project.id}
        threat_response = client.post("/api/v1/threats", json=threat_data)
        threat_id = threat_response.json()["data"]["id"]
        
        # Create attack path
        path_data = {**sample_attack_path, "threat_risk_id": threat_id}
        response = client.post("/api/v1/attack-paths", json=path_data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["data"]["name"] == sample_attack_path["name"]
        assert result["data"]["attack_potential"] is not None
        assert result["data"]["feasibility_rating"] is not None

    def test_calculate_feasibility(self, client, test_project, sample_threat, sample_attack_path):
        """Test POST /attack-paths/{id}/calculate calculates feasibility."""
        # Create threat and attack path
        threat_data = {**sample_threat, "project_id": test_project.id}
        threat_response = client.post("/api/v1/threats", json=threat_data)
        threat_id = threat_response.json()["data"]["id"]
        
        path_data = {**sample_attack_path, "threat_risk_id": threat_id}
        path_response = client.post("/api/v1/attack-paths", json=path_data)
        path_id = path_response.json()["data"]["id"]
        
        # Calculate feasibility
        response = client.post(f"/api/v1/attack-paths/{path_id}/calculate")
        
        assert response.status_code == 200
        result = response.json()
        assert "attack_potential" in result["data"]
        assert "feasibility_rating" in result["data"]
