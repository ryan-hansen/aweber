"""
Custom exceptions for the Widget CRUD API.

This module defines a comprehensive exception hierarchy for handling
various error conditions throughout the application with proper error
codes, messages, and context.
"""

from typing import Any, Dict, Optional


class BaseAPIException(Exception):
    """
    Base exception class for all API-related errors.

    This provides a consistent interface for all application exceptions
    with error codes, messages, and additional context.
    """

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize base API exception.

        Args:
            message: Human-readable error message
            error_code: Unique error code for this error type
            status_code: HTTP status code
            details: Additional context or details about the error
        """
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class ValidationException(BaseAPIException):
    """Exception for validation errors."""

    def __init__(
        self,
        message: str = "Validation failed",
        field_errors: Optional[Dict[str, str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize validation exception.

        Args:
            message: Error message
            field_errors: Dictionary of field-specific errors
            details: Additional context
        """
        error_details = details or {}
        if field_errors:
            error_details["field_errors"] = field_errors

        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=error_details,
        )


class ResourceNotFoundException(BaseAPIException):
    """Exception for when a requested resource is not found."""

    def __init__(
        self,
        resource_type: str,
        resource_id: Any,
        message: Optional[str] = None,
    ):
        """
        Initialize resource not found exception.

        Args:
            resource_type: Type of resource (e.g., 'Widget')
            resource_id: ID of the resource that was not found
            message: Custom error message
        """
        if message is None:
            message = f"{resource_type} with ID {resource_id} not found"

        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={
                "resource_type": resource_type,
                "resource_id": str(resource_id),
            },
        )


class DatabaseException(BaseAPIException):
    """Exception for database-related errors."""

    def __init__(
        self,
        message: str = "Database operation failed",
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize database exception.

        Args:
            message: Error message
            operation: Database operation that failed
            details: Additional context
        """
        error_details = details or {}
        if operation:
            error_details["operation"] = operation

        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
            details=error_details,
        )


class BusinessLogicException(BaseAPIException):
    """Exception for business logic violations."""

    def __init__(
        self,
        message: str,
        rule: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize business logic exception.

        Args:
            message: Error message
            rule: Business rule that was violated
            details: Additional context
        """
        error_details = details or {}
        if rule:
            error_details["violated_rule"] = rule

        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            status_code=400,
            details=error_details,
        )


class AuthenticationException(BaseAPIException):
    """Exception for authentication failures."""

    def __init__(
        self,
        message: str = "Authentication required",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize authentication exception.

        Args:
            message: Error message
            details: Additional context
        """
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details,
        )


class AuthorizationException(BaseAPIException):
    """Exception for authorization failures."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        resource: Optional[str] = None,
        action: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize authorization exception.

        Args:
            message: Error message
            resource: Resource being accessed
            action: Action being attempted
            details: Additional context
        """
        error_details = details or {}
        if resource:
            error_details["resource"] = resource
        if action:
            error_details["action"] = action

        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=error_details,
        )


class RateLimitException(BaseAPIException):
    """Exception for rate limiting violations."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize rate limit exception.

        Args:
            message: Error message
            retry_after: Seconds until retry is allowed
            details: Additional context
        """
        error_details = details or {}
        if retry_after:
            error_details["retry_after"] = retry_after

        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            status_code=429,
            details=error_details,
        )


class ExternalServiceException(BaseAPIException):
    """Exception for external service failures."""

    def __init__(
        self,
        service_name: str,
        message: str = "External service unavailable",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize external service exception.

        Args:
            service_name: Name of the external service
            message: Error message
            details: Additional context
        """
        error_details = details or {}
        error_details["service_name"] = service_name

        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=503,
            details=error_details,
        )


# Widget-specific exceptions
class WidgetException(BaseAPIException):
    """Base exception for widget-related errors."""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 400,
        widget_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize widget exception.

        Args:
            message: Error message
            error_code: Specific error code
            status_code: HTTP status code
            widget_id: ID of the widget involved
            details: Additional context
        """
        error_details = details or {}
        if widget_id is not None:
            error_details["widget_id"] = widget_id

        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=error_details,
        )


class WidgetNotFoundException(WidgetException):
    """Exception for when a widget is not found."""

    def __init__(
        self,
        widget_id: int,
        message: Optional[str] = None,
    ):
        """
        Initialize widget not found exception.

        Args:
            widget_id: ID of the widget that was not found
            message: Custom error message
        """
        if message is None:
            message = f"Widget with ID {widget_id} not found"

        super().__init__(
            message=message,
            error_code="WIDGET_NOT_FOUND",
            status_code=404,
            widget_id=widget_id,
        )


class WidgetValidationException(WidgetException):
    """Exception for widget validation errors."""

    def __init__(
        self,
        message: str,
        field_errors: Optional[Dict[str, str]] = None,
        widget_id: Optional[int] = None,
    ):
        """
        Initialize widget validation exception.

        Args:
            message: Error message
            field_errors: Dictionary of field-specific errors
            widget_id: ID of the widget being validated
        """
        details = {}
        if field_errors:
            details["field_errors"] = field_errors

        super().__init__(
            message=message,
            error_code="WIDGET_VALIDATION_ERROR",
            status_code=400,
            widget_id=widget_id,
            details=details,
        )


class WidgetDuplicateException(WidgetException):
    """Exception for duplicate widget errors."""

    def __init__(
        self,
        field: str,
        value: str,
        message: Optional[str] = None,
    ):
        """
        Initialize widget duplicate exception.

        Args:
            field: Field that has duplicate value
            value: Duplicate value
            message: Custom error message
        """
        if message is None:
            message = f"Widget with {field} '{value}' already exists"

        super().__init__(
            message=message,
            error_code="WIDGET_DUPLICATE_ERROR",
            status_code=409,
            details={
                "duplicate_field": field,
                "duplicate_value": value,
            },
        )
