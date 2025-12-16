"""
Helper Functions
================

Common utility functions.
"""

import hashlib
import mimetypes
import os
import uuid
from datetime import datetime
from typing import Any, Optional

import snowflake


# Snowflake ID generator (for distributed ID generation)
class SnowflakeGenerator:
    """Snowflake ID generator."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Worker ID from environment or default
            worker_id = int(os.environ.get("WORKER_ID", "1"))
            datacenter_id = int(os.environ.get("DATACENTER_ID", "1"))
            cls._instance.generator = snowflake.SnowflakeGenerator(
                worker_id % 32,  # 5 bits
                datacenter_id % 32,  # 5 bits
            )
        return cls._instance

    def next_id(self) -> int:
        """Generate next snowflake ID."""
        return next(self.generator)


def generate_id() -> int:
    """
    Generate a unique snowflake ID.

    Returns:
        Unique integer ID
    """
    try:
        return SnowflakeGenerator().next_id()
    except Exception:
        # Fallback to timestamp-based ID
        import time

        return int(time.time() * 1000000)


def generate_uuid() -> str:
    """
    Generate a UUID string.

    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.

    Args:
        filename: Original filename

    Returns:
        File extension (lowercase, without dot)
    """
    if not filename:
        return ""
    _, ext = os.path.splitext(filename)
    return ext.lower().lstrip(".")


def get_mime_type(filename: str) -> str:
    """
    Get MIME type from filename.

    Args:
        filename: Original filename

    Returns:
        MIME type string
    """
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"


def calculate_hash(data: bytes, algorithm: str = "sha256") -> str:
    """
    Calculate hash of data.

    Args:
        data: Bytes data
        algorithm: Hash algorithm (md5, sha1, sha256)

    Returns:
        Hex digest string
    """
    if algorithm == "md5":
        return hashlib.md5(data).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(data).hexdigest()
    else:
        return hashlib.sha256(data).hexdigest()


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.

    Args:
        text: Input string
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if not text or len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove path separators and dangerous characters
    dangerous_chars = ["/", "\\", "..", "<", ">", ":", '"', "|", "?", "*", "\0"]
    result = filename
    for char in dangerous_chars:
        result = result.replace(char, "_")
    return result.strip()


def generate_file_path(
    bucket: str,
    project_id: int,
    filename: str,
    subfolder: str = None,
) -> str:
    """
    Generate storage file path.

    Args:
        bucket: Storage bucket name
        project_id: Project ID
        filename: Original filename
        subfolder: Optional subfolder

    Returns:
        Storage path
    """
    # Generate date-based path
    date_path = datetime.now().strftime("%Y/%m/%d")

    # Generate unique filename
    unique_id = generate_uuid()[:8]
    ext = get_file_extension(filename)
    safe_name = sanitize_filename(filename)

    if len(safe_name) > 50:
        safe_name = safe_name[:50]

    new_filename = f"{unique_id}_{safe_name}"

    # Build path
    if subfolder:
        return f"projects/{project_id}/{subfolder}/{date_path}/{new_filename}"
    return f"projects/{project_id}/{date_path}/{new_filename}"


def parse_page_params(
    page: int = 1,
    page_size: int = 20,
    max_page_size: int = 100,
) -> tuple[int, int, int]:
    """
    Parse and validate pagination parameters.

    Args:
        page: Page number
        page_size: Page size
        max_page_size: Maximum allowed page size

    Returns:
        Tuple of (page, page_size, offset)
    """
    page = max(1, page)
    page_size = min(max(1, page_size), max_page_size)
    offset = (page - 1) * page_size
    return page, page_size, offset


def dict_to_snake_case(d: dict) -> dict:
    """
    Convert dictionary keys from camelCase to snake_case.

    Args:
        d: Input dictionary

    Returns:
        Dictionary with snake_case keys
    """
    import re

    def to_snake_case(name: str) -> str:
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    if isinstance(d, dict):
        return {to_snake_case(k): dict_to_snake_case(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [dict_to_snake_case(i) for i in d]
    return d


def deep_merge(base: dict, override: dict) -> dict:
    """
    Deep merge two dictionaries.

    Args:
        base: Base dictionary
        override: Override dictionary

    Returns:
        Merged dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result
