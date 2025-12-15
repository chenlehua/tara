"""Security tests for injection attacks."""
import pytest
import httpx


class TestSQLInjection:
    """SQL injection security tests."""

    @pytest.fixture
    def client(self):
        """HTTP client."""
        return httpx.Client(timeout=10.0)

    def test_sql_injection_in_search(self, client):
        """Test SQL injection in search parameter."""
        payloads = [
            "'; DROP TABLE projects; --",
            "1' OR '1'='1",
            "1; SELECT * FROM users",
            "' UNION SELECT * FROM projects --",
        ]
        
        for payload in payloads:
            response = client.get(
                "http://localhost:8001/api/v1/projects",
                params={"keyword": payload},
            )
            # Should not return 500 (database error)
            assert response.status_code != 500
            # Should not expose database errors
            if response.status_code != 200:
                assert "sql" not in response.text.lower()
                assert "database" not in response.text.lower()

    def test_sql_injection_in_id(self, client):
        """Test SQL injection in ID parameter."""
        payloads = [
            "1 OR 1=1",
            "1; DROP TABLE projects",
            "1' AND '1'='1",
        ]
        
        for payload in payloads:
            response = client.get(f"http://localhost:8001/api/v1/projects/{payload}")
            # Should return 422 (validation error) or 404
            assert response.status_code in [404, 422, 400]


class TestXSSInjection:
    """Cross-site scripting security tests."""

    @pytest.fixture
    def client(self):
        """HTTP client."""
        return httpx.Client(timeout=10.0)

    def test_xss_in_project_name(self, client):
        """Test XSS injection in project name."""
        xss_payload = "<script>alert('xss')</script>"
        
        response = client.post(
            "http://localhost:8001/api/v1/projects",
            json={
                "name": xss_payload,
                "vehicle_type": "BEV",
            },
        )
        
        if response.status_code == 200:
            data = response.json()
            # Script should be escaped or sanitized
            assert "<script>" not in str(data)

    def test_xss_in_description(self, client):
        """Test XSS injection in description field."""
        payloads = [
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
            "javascript:alert('xss')",
        ]
        
        for payload in payloads:
            response = client.post(
                "http://localhost:8001/api/v1/projects",
                json={
                    "name": "Test Project",
                    "description": payload,
                    "vehicle_type": "BEV",
                },
            )
            # Should accept but sanitize


class TestPathTraversal:
    """Path traversal security tests."""

    @pytest.fixture
    def client(self):
        """HTTP client."""
        return httpx.Client(timeout=10.0)

    def test_path_traversal_in_file_upload(self, client):
        """Test path traversal in file upload."""
        # When file upload is implemented
        malicious_filename = "../../../etc/passwd"
        # Should reject or sanitize filename

    def test_path_traversal_in_report_download(self, client):
        """Test path traversal in report download."""
        payloads = [
            "../../../etc/passwd",
            "....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2fetc/passwd",
        ]
        
        for payload in payloads:
            response = client.get(
                f"http://localhost:8006/api/v1/reports/{payload}/download"
            )
            # Should return 404 or 400, not expose system files
            assert response.status_code in [400, 404, 422]


class TestCommandInjection:
    """Command injection security tests."""

    @pytest.fixture
    def client(self):
        """HTTP client."""
        return httpx.Client(timeout=10.0)

    def test_command_injection_in_name(self, client):
        """Test command injection in name field."""
        payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "$(whoami)",
            "`id`",
        ]
        
        for payload in payloads:
            response = client.post(
                "http://localhost:8001/api/v1/projects",
                json={
                    "name": payload,
                    "vehicle_type": "BEV",
                },
            )
            # Should not execute commands
            if response.status_code == 200:
                data = response.json()
                # Should not contain command output
                assert "root:" not in str(data)
                assert "uid=" not in str(data)
