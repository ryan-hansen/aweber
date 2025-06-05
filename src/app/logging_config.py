"""
Logging configuration for the Widget CRUD API.

This module provides structured logging configuration with proper
formatters, handlers, and log levels for different environments.
"""

import logging
import logging.config
import sys
from typing import Any, Dict

from .config import get_settings

settings = get_settings()


def get_logging_config() -> Dict[str, Any]:
    """
    Get logging configuration based on environment settings.

    Returns:
        Dictionary containing logging configuration
    """
    # Determine log level from settings
    log_level = "DEBUG" if settings.debug else "INFO"

    # Define log format
    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "%(funcName)s:%(lineno)d - %(message)s"
    )

    # JSON format for structured logging (useful for production)
    json_format = (
        '{"timestamp": "%(asctime)s", "logger": "%(name)s", '
        '"level": "%(levelname)s", "function": "%(funcName)s", '
        '"line": %(lineno)d, "message": "%(message)s"}'
    )

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": log_format,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "format": json_format,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": (
                    "%(asctime)s - %(name)s - %(levelname)s - "
                    "%(pathname)s:%(lineno)d - %(funcName)s() - %(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "detailed",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
            "app": {
                "handlers": ["console", "file"],
                "level": log_level,
                "propagate": False,
            },
            "app.errors": {
                "handlers": ["console", "file", "error_file"],
                "level": "ERROR",
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": ["console"] if settings.debug else [],
                "level": "INFO" if settings.debug else "WARNING",
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console"] if settings.debug else [],
                "level": "INFO" if settings.debug else "WARNING",
                "propagate": False,
            },
        },
    }

    return config


def setup_logging() -> None:
    """Set up application logging configuration."""
    import os

    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Apply logging configuration
    config = get_logging_config()
    logging.config.dictConfig(config)

    # Get logger and log startup message
    logger = logging.getLogger("app")
    logger.info("Logging configuration initialized")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_request_info(
    request_id: str, method: str, path: str, client_ip: str = None
) -> None:
    """
    Log request information with structured data.

    Args:
        request_id: Unique request identifier
        method: HTTP method
        path: Request path
        client_ip: Client IP address
    """
    logger = get_logger("app.requests")

    extra_data = {
        "request_id": request_id,
        "method": method,
        "path": path,
    }

    if client_ip:
        extra_data["client_ip"] = client_ip

    logger.info(f"Request: {method} {path}", extra=extra_data)


def log_response_info(request_id: str, status_code: int, duration_ms: float) -> None:
    """
    Log response information with structured data.

    Args:
        request_id: Unique request identifier
        status_code: HTTP status code
        duration_ms: Request duration in milliseconds
    """
    logger = get_logger("app.requests")

    logger.info(
        f"Response: {status_code} ({duration_ms:.2f}ms)",
        extra={
            "request_id": request_id,
            "status_code": status_code,
            "duration_ms": duration_ms,
        },
    )


def log_error(
    error: Exception, request_id: str = None, context: Dict[str, Any] = None
) -> None:
    """
    Log error information with structured data.

    Args:
        error: Exception that occurred
        request_id: Unique request identifier
        context: Additional context information
    """
    logger = get_logger("app.errors")

    extra_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }

    if request_id:
        extra_data["request_id"] = request_id

    if context:
        extra_data.update(context)

    logger.error(
        f"Error occurred: {type(error).__name__}: {str(error)}",
        extra=extra_data,
        exc_info=True,
    )


def log_business_event(
    event_type: str, details: Dict[str, Any], request_id: str = None
) -> None:
    """
    Log business events with structured data.

    Args:
        event_type: Type of business event
        details: Event details
        request_id: Unique request identifier
    """
    logger = get_logger("app.business")

    extra_data = {
        "event_type": event_type,
        "details": details,
    }

    if request_id:
        extra_data["request_id"] = request_id

    logger.info(f"Business event: {event_type}", extra=extra_data)


def log_security_event(
    event_type: str,
    severity: str = "WARNING",
    details: Dict[str, Any] = None,
    request_id: str = None,
) -> None:
    """
    Log security events with structured data.

    Args:
        event_type: Type of security event
        severity: Event severity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        details: Event details
        request_id: Unique request identifier
    """
    logger = get_logger("app.security")

    extra_data = {
        "event_type": event_type,
        "severity": severity,
    }

    if details:
        extra_data["details"] = details

    if request_id:
        extra_data["request_id"] = request_id

    log_level = getattr(logging, severity.upper(), logging.WARNING)
    logger.log(log_level, f"Security event: {event_type}", extra=extra_data)
