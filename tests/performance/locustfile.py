"""Locust load testing for TARA System."""
from locust import HttpUser, task, between, tag
import json
import random


class TaraUser(HttpUser):
    """Simulated TARA system user."""
    
    wait_time = between(1, 3)
    host = "http://localhost:8001"
    
    def on_start(self):
        """Initialize user session."""
        self.project_ids = []
        self.asset_ids = []
        self.threat_ids = []
        
        # Create a test project
        response = self.client.post(
            "/api/v1/projects",
            json={
                "name": f"Load Test Project {random.randint(1000, 9999)}",
                "vehicle_type": "BEV",
                "standard": "ISO/SAE 21434",
            },
        )
        if response.status_code == 200:
            self.project_ids.append(response.json()["data"]["id"])

    def on_stop(self):
        """Cleanup test data."""
        for project_id in self.project_ids:
            self.client.delete(f"/api/v1/projects/{project_id}")

    @tag("projects")
    @task(10)
    def list_projects(self):
        """List all projects."""
        self.client.get("/api/v1/projects")

    @tag("projects")
    @task(5)
    def get_project(self):
        """Get project details."""
        if self.project_ids:
            project_id = random.choice(self.project_ids)
            self.client.get(f"/api/v1/projects/{project_id}")

    @tag("projects")
    @task(2)
    def create_project(self):
        """Create a new project."""
        response = self.client.post(
            "/api/v1/projects",
            json={
                "name": f"Load Test Project {random.randint(1000, 9999)}",
                "vehicle_type": random.choice(["BEV", "HEV", "ICE"]),
                "standard": "ISO/SAE 21434",
            },
        )
        if response.status_code == 200:
            self.project_ids.append(response.json()["data"]["id"])


class AssetServiceUser(HttpUser):
    """User for asset service load testing."""
    
    wait_time = between(1, 3)
    host = "http://localhost:8003"
    
    def on_start(self):
        """Initialize with a project."""
        self.project_id = 1  # Assume project exists
        self.asset_ids = []

    @tag("assets")
    @task(10)
    def list_assets(self):
        """List assets for a project."""
        self.client.get(f"/api/v1/assets?project_id={self.project_id}")

    @tag("assets")
    @task(3)
    def create_asset(self):
        """Create a new asset."""
        asset_types = ["ecu", "gateway", "bus", "sensor", "actuator"]
        response = self.client.post(
            "/api/v1/assets",
            json={
                "project_id": self.project_id,
                "name": f"Test Asset {random.randint(1000, 9999)}",
                "asset_type": random.choice(asset_types),
            },
        )
        if response.status_code == 200:
            self.asset_ids.append(response.json()["data"]["id"])


class ThreatServiceUser(HttpUser):
    """User for threat service load testing."""
    
    wait_time = between(1, 3)
    host = "http://localhost:8004"
    
    def on_start(self):
        """Initialize with a project."""
        self.project_id = 1
        self.threat_ids = []

    @tag("threats")
    @task(10)
    def list_threats(self):
        """List threats for a project."""
        self.client.get(f"/api/v1/threats?project_id={self.project_id}")

    @tag("threats")
    @task(5)
    def get_risk_matrix(self):
        """Get risk matrix."""
        self.client.get(f"/api/v1/risks/matrix?project_id={self.project_id}")

    @tag("threats")
    @task(3)
    def create_threat(self):
        """Create a new threat."""
        threat_types = [
            "Spoofing",
            "Tampering",
            "Repudiation",
            "Information Disclosure",
            "Denial of Service",
            "Elevation of Privilege",
        ]
        response = self.client.post(
            "/api/v1/threats",
            json={
                "project_id": self.project_id,
                "threat_name": f"Test Threat {random.randint(1000, 9999)}",
                "threat_type": random.choice(threat_types),
            },
        )
        if response.status_code == 200:
            self.threat_ids.append(response.json()["data"]["id"])
