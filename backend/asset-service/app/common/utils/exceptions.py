"""
Custom Exceptions
=================

Exception classes for TARA system.
"""

from typing import Any, Dict, Optional


class TaraException(Exception):
    """Base exception for TARA system."""

    def __init__(
        self,
        message: str,
        code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "success": False,
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class NotFoundException(TaraException):
    """Resource not found exception."""

    def __init__(
        self,
        resource: str,
        resource_id: Any = None,
        message: Optional[str] = None,
    ):
        msg = message or f"{resource} not found"
        if resource_id:
            msg = f"{resource} with id {resource_id} not found"
        super().__init__(message=msg, code=404)
        self.resource = resource
        self.resource_id = resource_id


class ValidationException(TaraException):
    """Validation error exception."""

    def __init__(
        self,
        message: str = "Validation error",
        errors: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, code=400, details={"errors": errors or {}})
        self.errors = errors or {}


class AuthorizationException(TaraException):
    """Authorization error exception."""

    def __init__(
        self,
        message: str = "Unauthorized",
        required_permission: Optional[str] = None,
    ):
        super().__init__(message=message, code=403)
        self.required_permission = required_permission


class AuthenticationException(TaraException):
    """Authentication error exception."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message=message, code=401)


class ExternalServiceException(TaraException):
    """External service error exception."""

    def __init__(
        self,
        service: str,
        message: str,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(
            message=f"{service} error: {message}",
            code=502,
            details={
                "service": service,
                "original_error": str(original_error) if original_error else None,
            },
        )
        self.service = service
        self.original_error = original_error


class RateLimitException(TaraException):
    """Rate limit exceeded exception."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
    ):
        super().__init__(message=message, code=429)
        self.retry_after = retry_after


class ConflictException(TaraException):
    """Resource conflict exception."""

    def __init__(
        self,
        message: str = "Resource conflict",
        conflicting_resource: Optional[str] = None,
    ):
        super().__init__(message=message, code=409)
        self.conflicting_resource = conflicting_resource


class FileException(TaraException):
    """File operation exception."""

    def __init__(
        self,
        message: str,
        filename: Optional[str] = None,
        operation: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            code=400,
            details={"filename": filename, "operation": operation},
        )
        self.filename = filename
        self.operation = operation


class AIServiceException(TaraException):
    """AI service error exception."""

    def __init__(
        self,
        message: str,
        model: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(
            message=f"AI service error: {message}",
            code=503,
            details={"model": model},
        )
        self.model = model
        self.original_error = original_error
