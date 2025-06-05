"""
Middleware for the Widget CRUD API.

This module provides middleware for request validation, logging,
error tracking, and other cross-cutting concerns.
"""

import time
import uuid
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .logging_config import get_logger, log_request_info, log_response_info

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses with timing.

    This middleware adds request IDs, logs request/response information,
    and tracks request duration for monitoring and debugging.
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Process request and response with logging.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Add request ID to response headers
        start_time = time.time()

        # Extract client IP (handle proxy headers)
        client_ip = self._get_client_ip(request)

        # Log request information
        log_request_info(
            request_id=request_id,
            method=request.method,
            path=str(request.url.path),
            client_ip=client_ip,
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate request duration
            duration_ms = (time.time() - start_time) * 1000

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            # Log response information
            log_response_info(
                request_id=request_id,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

            return response

        except Exception:
            # Calculate duration even for errors
            duration_ms = (time.time() - start_time) * 1000

            # Log error response
            log_response_info(
                request_id=request_id, status_code=500, duration_ms=duration_ms
            )

            # Re-raise the exception to be handled by exception handlers
            raise

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request headers.

        Args:
            request: HTTP request

        Returns:
            Client IP address
        """
        # Check for proxy headers in order of preference
        headers_to_check = [
            "x-forwarded-for",
            "x-real-ip",
            "x-client-ip",
            "cf-connecting-ip",  # Cloudflare
        ]

        for header in headers_to_check:
            ip = request.headers.get(header)
            if ip:
                # X-Forwarded-For can contain multiple IPs, take the first one
                return ip.split(",")[0].strip()

        # Fall back to direct connection IP
        if request.client:
            return request.client.host

        return "unknown"


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for additional request validation beyond Pydantic.

    This middleware can perform custom validation checks that are
    not easily handled by Pydantic schemas.
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Validate request before processing.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response or validation error
        """
        # Perform custom validation
        validation_error = await self._validate_request(request)
        if validation_error:
            # Import here to avoid circular imports
            from .exceptions import ValidationException

            raise ValidationException(
                message=validation_error["message"],
                details=validation_error.get("details", {}),
            )

        # Continue processing
        return await call_next(request)

    async def _validate_request(self, request: Request) -> Optional[dict]:
        """
        Perform custom request validation.

        Args:
            request: HTTP request to validate

        Returns:
            Validation error dict if validation fails, None if valid
        """
        # Check request size (example validation)
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                max_size = 10 * 1024 * 1024  # 10MB
                if size > max_size:
                    return {
                        "message": "Request body too large",
                        "details": {
                            "max_size_bytes": max_size,
                            "received_size_bytes": size,
                        },
                    }
            except ValueError:
                return {
                    "message": "Invalid Content-Length header",
                    "details": {"content_length": content_length},
                }

        # Check for required headers for certain endpoints
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith("application/json"):
                # Allow form data and other content types for specific
                # endpoints
                path = str(request.url.path)
                if not any(
                    allowed in path for allowed in ["/docs", "/openapi"]
                ):
                    if (
                        request.method != "DELETE"
                    ):  # DELETE doesn't need content-type
                        return {
                            "message": "Content-Type must be application/json",
                            "details": {
                                "received_content_type": content_type,
                                "expected_content_type": "application/json",
                            },
                        }

        # Custom business validation can be added here
        # For example: API key validation, rate limiting, etc.

        return None  # No validation errors


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding security headers to responses.

    This middleware adds common security headers to all responses
    to improve application security posture.
    """

    def __init__(self, app):
        super().__init__(app)

        # Security headers to add
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https:; "
                "connect-src 'self';"
            ),
        }

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Add security headers to response.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response with security headers
        """
        response = await call_next(request)

        # Add security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value

        return response


class ErrorTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for tracking and monitoring errors.

    This middleware can be extended to integrate with external
    error tracking services like Sentry, Bugsnag, etc.
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Track errors and performance metrics.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response
        """
        try:
            response = await call_next(request)

            # Track successful requests (could send to monitoring service)
            if response.status_code >= 400:
                await self._track_error_response(request, response)

            return response

        except Exception as exc:
            # Track exceptions (could send to error tracking service)
            await self._track_exception(request, exc)

            # Re-raise the exception
            raise exc

    async def _track_error_response(
        self, request: Request, response: Response
    ) -> None:
        """
        Track error responses for monitoring.

        Args:
            request: HTTP request
            response: HTTP response with error status
        """
        # This is where you would integrate with external services
        # For now, we just log it
        logger.warning(
            f"Error response: {response.status_code} for "
            f"{request.method} {request.url.path}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "status_code": response.status_code,
                "method": request.method,
                "path": str(request.url.path),
            },
        )

    async def _track_exception(self, request: Request, exc: Exception) -> None:
        """
        Track exceptions for monitoring.

        Args:
            request: HTTP request
            exc: Exception that occurred
        """
        # This is where you would integrate with external services
        # For now, we just log it
        logger.error(
            f"Exception in {request.method} {request.url.path}: "
            f"{type(exc).__name__}: {str(exc)}",
            extra={
                "request_id": getattr(request.state, "request_id", None),
                "exception_type": type(exc).__name__,
                "method": request.method,
                "path": str(request.url.path),
            },
            exc_info=True,
        )
