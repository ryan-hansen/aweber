"""
Exception handlers for the Widget CRUD API.

This module provides comprehensive exception handlers that convert
various exception types to consistent JSON responses with proper
logging and error tracking.
"""

import time
import uuid
from typing import Union

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import get_settings
from .exceptions import BaseAPIException
from .logging_config import get_logger, log_error

settings = get_settings()
logger = get_logger(__name__)


def create_error_response(
    request_id: str,
    error_code: str,
    message: str,
    status_code: int,
    details: dict = None,
) -> JSONResponse:
    """
    Create a standardized error response.

    Args:
        request_id: Unique request identifier
        error_code: Error code for the error type
        message: Human-readable error message
        status_code: HTTP status code
        details: Additional error details

    Returns:
        JSONResponse with standardized error format
    """
    response_data = {
        "error": error_code,
        "message": message,
        "request_id": request_id,
        "timestamp": time.time(),
    }

    if details:
        response_data["details"] = details

    # Include stack trace in debug mode
    if settings.debug and "stack_trace" in (details or {}):
        response_data["stack_trace"] = details["stack_trace"]

    return JSONResponse(
        status_code=status_code,
        content=response_data,
    )


async def base_api_exception_handler(
    request: Request, exc: BaseAPIException
) -> JSONResponse:
    """
    Handler for custom BaseAPIException and its subclasses.

    Args:
        request: FastAPI request object
        exc: BaseAPIException instance

    Returns:
        JSONResponse with error details
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # Log the error
    log_error(
        exc,
        request_id=request_id,
        context={
            "path": str(request.url),
            "method": request.method,
            "error_code": exc.error_code,
        },
    )

    return create_error_response(
        request_id=request_id,
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handler for FastAPI request validation errors.

    Args:
        request: FastAPI request object
        exc: RequestValidationError instance

    Returns:
        JSONResponse with validation error details
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # Extract field errors from Pydantic validation error
    field_errors = {}
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"][1:])  # Skip 'body'
        field_errors[field_path] = error["msg"]

    # Log the validation error
    log_error(
        exc,
        request_id=request_id,
        context={
            "path": str(request.url),
            "method": request.method,
            "field_errors": field_errors,
        },
    )

    return create_error_response(
        request_id=request_id,
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={
            "field_errors": field_errors,
            "validation_errors": exc.errors() if settings.debug else None,
        },
    )


async def pydantic_validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """
    Handler for Pydantic validation errors.

    Args:
        request: FastAPI request object
        exc: ValidationError instance

    Returns:
        JSONResponse with validation error details
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # Extract field errors from Pydantic validation error
    field_errors = {}
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"])
        field_errors[field_path] = error["msg"]

    # Log the validation error
    log_error(
        exc,
        request_id=request_id,
        context={
            "path": str(request.url),
            "method": request.method,
            "field_errors": field_errors,
        },
    )

    return create_error_response(
        request_id=request_id,
        error_code="VALIDATION_ERROR",
        message="Data validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={
            "field_errors": field_errors,
            "validation_errors": exc.errors() if settings.debug else None,
        },
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """
    Handler for HTTP exceptions (404, 405, etc.).

    Args:
        request: FastAPI request object
        exc: StarletteHTTPException instance

    Returns:
        JSONResponse with HTTP error details
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # Map status codes to error codes
    error_code_map = {
        404: "RESOURCE_NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        406: "NOT_ACCEPTABLE",
        415: "UNSUPPORTED_MEDIA_TYPE",
        429: "RATE_LIMIT_ERROR",
    }

    error_code = error_code_map.get(exc.status_code, "HTTP_ERROR")

    # Log the HTTP error (but only if it's not a common 404)
    if exc.status_code != 404:
        log_error(
            exc,
            request_id=request_id,
            context={
                "path": str(request.url),
                "method": request.method,
                "status_code": exc.status_code,
            },
        )

    return create_error_response(
        request_id=request_id,
        error_code=error_code,
        message=exc.detail,
        status_code=exc.status_code,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for unhandled exceptions.

    Args:
        request: FastAPI request object
        exc: Exception instance

    Returns:
        JSONResponse with generic error response
    """
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    # Log the unexpected error with full context
    import traceback

    stack_trace = traceback.format_exc()

    log_error(
        exc,
        request_id=request_id,
        context={
            "path": str(request.url),
            "method": request.method,
            "stack_trace": stack_trace,
            "exception_type": type(exc).__name__,
        },
    )

    # Return generic error message (don't expose internal details)
    message = "An unexpected error occurred"
    details = {}

    # In debug mode, include more details
    if settings.debug:
        message = f"Internal server error: {str(exc)}"
        details = {
            "exception_type": type(exc).__name__,
            "stack_trace": stack_trace,
        }

    return create_error_response(
        request_id=request_id,
        error_code="INTERNAL_SERVER_ERROR",
        message=message,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details=details,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers with the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    # Custom application exceptions
    app.add_exception_handler(BaseAPIException, base_api_exception_handler)

    # Validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)

    # HTTP exceptions
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    # Generic exception handler (catch-all)
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Exception handlers registered successfully")
