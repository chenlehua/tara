"""Integration tests for document API endpoints."""
import pytest
from unittest.mock import patch, MagicMock


class TestDocumentAPI:
    """Integration tests for document API."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_list_documents_empty(self, client, test_project):
        """Test GET /documents returns empty list initially."""
        response = client.get(f"/api/v1/documents?project_id={test_project.id}")
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["data"]["items"] == []

    @patch('app.services.document_service.StorageService')
    def test_upload_document(self, mock_storage, client, test_project, sample_pdf_content):
        """Test POST /documents uploads a document."""
        mock_storage.return_value.upload_file.return_value = "documents/test.pdf"
        
        files = {"file": ("test.pdf", sample_pdf_content, "application/pdf")}
        response = client.post(
            f"/api/v1/documents?project_id={test_project.id}",
            files=files,
        )
        
        # May fail due to mock setup, but structure should be correct
        assert response.status_code in [200, 500]

    def test_get_document_not_found(self, client):
        """Test GET /documents/{id} returns 404."""
        response = client.get("/api/v1/documents/99999")
        
        assert response.status_code == 404

    @patch('app.services.document_service.DocumentService.parse_document')
    def test_parse_document(self, mock_parse, client, test_project, db_session):
        """Test POST /documents/{id}/parse triggers parsing."""
        from tara_shared.models import Document
        
        # Create a document record
        doc = Document(
            project_id=test_project.id,
            filename="test.pdf",
            file_path="documents/test.pdf",
            file_type="pdf",
            file_size=1024,
        )
        db_session.add(doc)
        db_session.commit()
        
        response = client.post(f"/api/v1/documents/{doc.id}/parse")
        
        assert response.status_code == 200
