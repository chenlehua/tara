"""
Logging Configuration
=====================

Structured logging using structlog (with fallback to standard logging).
"""

import logging
import sys
from typing import Any, Union

# Try to import structlog, use standard logging as fallback
try:
    import structlog
    from structlog.types import Processor

    _STRUCTLOG_AVAILABLE = True
except ImportError:
    _STRUCTLOG_AVAILABLE = False
    structlog = None
    Processor = None

from ..config import settings

# Standard logger for fallback
_standard_loggers: dict = {}


def setup_logging() -> None:
    """Configure structured logging."""

    # Configure standard library logging
    log_level = getattr(logging, settings.app_log_level.upper(), logging.INFO)
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    if not _STRUCTLOG_AVAILABLE:
        return

    # Shared processors
    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if settings.app_env == "development":
        # Development: pretty console output
        structlog.configure(
            processors=shared_processors + [structlog.dev.ConsoleRenderer(colors=True)],
            wrapper_class=structlog.make_filtering_bound_logger(log_level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        # Production: JSON output
        structlog.configure(
            processors=shared_processors
            + [
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(log_level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )


def get_logger(name: str = None) -> Union["structlog.stdlib.BoundLogger", logging.Logger]:
    """
    Get a logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance (structlog if available, else standard logging)
    """
    logger_name = name or "tara"

    if _STRUCTLOG_AVAILABLE:
        return structlog.get_logger(logger_name)

    # Fallback to standard logging
    if logger_name not in _standard_loggers:
        logger = logging.getLogger(logger_name)
        _standard_loggers[logger_name] = logger
    return _standard_loggers[logger_name]


class LoggerMixin:
    """Mixin class to add logging capability."""

    @property
    def logger(self) -> Union["structlog.stdlib.BoundLogger", logging.Logger]:
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)


def log_request(
    method: str, path: str, status_code: int, duration_ms: float, **extra: Any
) -> None:
    """Log HTTP request."""
    logger = get_logger("http")
    msg = f"http_request method={method} path={path} status_code={status_code} duration_ms={round(duration_ms, 2)}"
    if extra:
        msg += " " + " ".join(f"{k}={v}" for k, v in extra.items())
    logger.info(msg)


def log_service_call(
    service: str, method: str, success: bool, duration_ms: float, **extra: Any
) -> None:
    """Log service method call."""
    logger = get_logger("service")
    msg = f"service_call service={service} method={method} success={success} duration_ms={round(duration_ms, 2)}"
    if extra:
        msg += " " + " ".join(f"{k}={v}" for k, v in extra.items())
    if success:
        logger.info(msg)
    else:
        logger.error(msg)
