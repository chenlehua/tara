"""
Response Utilities
==================

Standard response formatting utilities.
"""

from typing import Any, Dict, List, Optional, TypeVar

from fastapi import status
from fastapi.responses import JSONResponse

T = TypeVar("T")


def success_response(
    data: Any = None,
    message: str = "success",
    code: int = 200,
) -> Dict[str, Any]:
    """
    Create a standard success response.

    Args:
        data: Response data
        message: Success message
        code: HTTP status code

    Returns:
        Standard response dictionary
    """
    return {
        "success": True,
        "code": code,
        "message": message,
        "data": data,
    }


def error_response(
    message: str,
    code: int = 400,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a standard error response.

    Args:
        message: Error message
        code: HTTP status code
        details: Additional error details

    Returns:
        Standard error response dictionary
    """
    response = {
        "success": False,
        "code": code,
        "message": message,
        "data": None,
    }
    if details:
        response["details"] = details
    return response


def paginated_response(
    items: List[Any],
    total: int,
    page: int = 1,
    page_size: int = 20,
    message: str = "success",
) -> Dict[str, Any]:
    """
    Create a paginated response.

    Args:
        items: List of items
        total: Total number of items
        page: Current page number
        page_size: Items per page
        message: Success message

    Returns:
        Paginated response dictionary
    """
    pages = (total + page_size - 1) // page_size if page_size > 0 else 0

    return {
        "success": True,
        "code": 200,
        "message": message,
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        },
    }


def json_error_response(
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    details: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """
    Create a JSON error response.

    Args:
        message: Error message
        status_code: HTTP status code
        details: Additional error details

    Returns:
        FastAPI JSONResponse
    """
    content = error_response(message, status_code, details)
    return JSONResponse(status_code=status_code, content=content)


def json_success_response(
    data: Any = None,
    message: str = "success",
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """
    Create a JSON success response.

    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code

    Returns:
        FastAPI JSONResponse
    """
    content = success_response(data, message, status_code)
    return JSONResponse(status_code=status_code, content=content)
