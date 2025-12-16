"""Unit tests for utility functions."""

import pytest
from tara_shared.utils.helpers import (calculate_hash, deep_merge,
                                       dict_to_snake_case, generate_uuid,
                                       get_file_extension, get_mime_type,
                                       parse_page_params, sanitize_filename,
                                       truncate_string)
from tara_shared.utils.response import (error_response, paginated_response,
                                        success_response)


class TestHelperFunctions:
    """Tests for helper utility functions."""

    def test_generate_uuid(self):
        """Test UUID generation."""
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()

        assert len(uuid1) == 36  # Standard UUID format
        assert uuid1 != uuid2  # Should be unique

    def test_get_file_extension(self):
        """Test file extension extraction."""
        assert get_file_extension("document.pdf") == "pdf"
        assert get_file_extension("image.PNG") == "png"
        assert get_file_extension("file.tar.gz") == "gz"
        assert get_file_extension("noextension") == ""

    def test_get_mime_type(self):
        """Test MIME type detection."""
        assert get_mime_type("document.pdf") == "application/pdf"
        assert get_mime_type("image.png") == "image/png"
        assert (
            get_mime_type("document.docx")
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    def test_calculate_hash(self):
        """Test content hash calculation."""
        content = b"test content"
        hash1 = calculate_hash(content)
        hash2 = calculate_hash(content)

        assert hash1 == hash2  # Same content = same hash
        assert len(hash1) == 64  # SHA256 hex length

    def test_truncate_string(self):
        """Test string truncation."""
        long_text = "This is a very long text that should be truncated"

        truncated = truncate_string(long_text, 20)
        assert len(truncated) <= 23  # 20 + "..."
        assert truncated.endswith("...")

        short_text = "Short"
        assert truncate_string(short_text, 20) == short_text

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert sanitize_filename("normal_file.pdf") == "normal_file.pdf"
        # Spaces are preserved, only dangerous characters are replaced
        assert sanitize_filename("file with spaces.pdf") == "file with spaces.pdf"
        assert sanitize_filename("file/with\\slashes.pdf") == "file_with_slashes.pdf"
        assert sanitize_filename("file<with>special.pdf") == "file_with_special.pdf"

    def test_parse_page_params(self):
        """Test pagination parameter parsing."""
        # Returns (page, page_size, offset)
        page, page_size, offset = parse_page_params(page=2, page_size=20)
        assert page == 2
        assert page_size == 20
        assert offset == 20

        page, page_size, offset = parse_page_params(page=1, page_size=10)
        assert page == 1
        assert page_size == 10
        assert offset == 0

    def test_dict_to_snake_case(self):
        """Test camelCase to snake_case conversion."""
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "emailAddress": "john@example.com",
        }
        result = dict_to_snake_case(data)

        assert "first_name" in result
        assert "last_name" in result
        assert "email_address" in result

    def test_deep_merge(self):
        """Test deep dictionary merge."""
        dict1 = {"a": 1, "b": {"c": 2, "d": 3}}
        dict2 = {"b": {"c": 4, "e": 5}, "f": 6}

        result = deep_merge(dict1, dict2)

        assert result["a"] == 1
        assert result["b"]["c"] == 4  # Overwritten
        assert result["b"]["d"] == 3  # Preserved
        assert result["b"]["e"] == 5  # Added
        assert result["f"] == 6  # Added


class TestResponseFunctions:
    """Tests for API response utility functions."""

    def test_success_response(self):
        """Test success response format."""
        data = {"id": 1, "name": "Test"}
        response = success_response(data)

        assert response["success"] is True
        assert response["code"] == 200
        assert response["data"] == data

    def test_success_response_with_message(self):
        """Test success response with custom message."""
        response = success_response(None, message="Operation completed")

        assert response["success"] is True
        assert response["message"] == "Operation completed"

    def test_error_response(self):
        """Test error response format."""
        response = error_response("Something went wrong", code=400)

        assert response["success"] is False
        assert response["code"] == 400
        assert response["message"] == "Something went wrong"
        assert response["data"] is None

    def test_paginated_response(self):
        """Test paginated response format."""
        items = [{"id": 1}, {"id": 2}]
        response = paginated_response(items, total=100, page=2, page_size=20)

        assert response["success"] is True
        assert response["data"]["items"] == items
        assert response["data"]["total"] == 100
        assert response["data"]["page"] == 2
        assert response["data"]["page_size"] == 20
        assert response["data"]["pages"] == 5
