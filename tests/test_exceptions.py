"""
Tests for custom exception classes.

This module tests all custom exceptions to ensure they properly
format error responses, include correct status codes, and maintain
consistent error structures.
"""

from src.app.exceptions import (
    AuthenticationException,
    AuthorizationException,
    BaseAPIException,
    BusinessLogicException,
    DatabaseException,
    ExternalServiceException,
    RateLimitException,
    ResourceNotFoundException,
    ValidationException,
    WidgetDuplicateException,
    WidgetException,
    WidgetNotFoundException,
    WidgetValidationException,
)


class TestBaseAPIException:
    """Test BaseAPIException functionality."""

    def test_basic_initialization(self):
        """Test basic exception initialization."""
        exc = BaseAPIException(
            message="Test error", error_code="TEST_ERROR", status_code=400
        )

        assert exc.message == "Test error"
        assert exc.error_code == "TEST_ERROR"
        assert exc.status_code == 400
        assert exc.details == {}
        assert str(exc) == "Test error"

    def test_initialization_with_details(self):
        """Test exception initialization with details."""
        details = {"field": "value", "count": 123}
        exc = BaseAPIException(
            message="Test error",
            error_code="TEST_ERROR",
            status_code=400,
            details=details,
        )

        assert exc.details == details

    def test_to_dict_method(self):
        """Test to_dict method returns proper structure."""
        details = {"field": "value"}
        exc = BaseAPIException(
            message="Test error",
            error_code="TEST_ERROR",
            status_code=400,
            details=details,
        )

        result = exc.to_dict()
        expected = {
            "error": "TEST_ERROR",
            "message": "Test error",
            "details": details,
        }

        assert result == expected

    def test_default_status_code(self):
        """Test default status code is 500."""
        exc = BaseAPIException(message="Test error", error_code="TEST_ERROR")

        assert exc.status_code == 500


class TestValidationException:
    """Test ValidationException functionality."""

    def test_basic_initialization(self):
        """Test basic validation exception."""
        exc = ValidationException()

        assert exc.message == "Validation failed"
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.status_code == 400
        assert exc.details == {}

    def test_initialization_with_field_errors(self):
        """Test validation exception with field errors."""
        field_errors = {"name": "Required field", "count": "Must be positive"}
        exc = ValidationException(
            message="Custom validation error", field_errors=field_errors
        )

        assert exc.message == "Custom validation error"
        assert exc.details["field_errors"] == field_errors

    def test_initialization_with_additional_details(self):
        """Test validation exception with both field errors and details."""
        field_errors = {"name": "Required field"}
        additional_details = {"context": "user_registration"}

        exc = ValidationException(
            field_errors=field_errors, details=additional_details
        )

        assert exc.details["field_errors"] == field_errors
        assert exc.details["context"] == "user_registration"


class TestResourceNotFoundException:
    """Test ResourceNotFoundException functionality."""

    def test_basic_initialization(self):
        """Test basic resource not found exception."""
        exc = ResourceNotFoundException(
            resource_type="Widget", resource_id=123
        )

        assert exc.message == "Widget with ID 123 not found"
        assert exc.error_code == "RESOURCE_NOT_FOUND"
        assert exc.status_code == 404
        assert exc.details["resource_type"] == "Widget"
        assert exc.details["resource_id"] == "123"

    def test_custom_message(self):
        """Test resource not found with custom message."""
        exc = ResourceNotFoundException(
            resource_type="User",
            resource_id="test@example.com",
            message="User not found in system",
        )

        assert exc.message == "User not found in system"
        assert exc.details["resource_id"] == "test@example.com"

    def test_string_resource_id(self):
        """Test with string resource ID."""
        exc = ResourceNotFoundException(
            resource_type="User", resource_id="abc-123"
        )

        assert exc.details["resource_id"] == "abc-123"


class TestDatabaseException:
    """Test DatabaseException functionality."""

    def test_basic_initialization(self):
        """Test basic database exception."""
        exc = DatabaseException()

        assert exc.message == "Database operation failed"
        assert exc.error_code == "DATABASE_ERROR"
        assert exc.status_code == 500
        assert exc.details == {}

    def test_initialization_with_operation(self):
        """Test database exception with operation context."""
        exc = DatabaseException(
            message="Connection timeout", operation="create_widget"
        )

        assert exc.message == "Connection timeout"
        assert exc.details["operation"] == "create_widget"

    def test_initialization_with_details(self):
        """Test database exception with additional details."""
        details = {"table": "widgets", "constraint": "unique_name"}
        exc = DatabaseException(operation="insert", details=details)

        assert exc.details["operation"] == "insert"
        assert exc.details["table"] == "widgets"
        assert exc.details["constraint"] == "unique_name"


class TestBusinessLogicException:
    """Test BusinessLogicException functionality."""

    def test_basic_initialization(self):
        """Test basic business logic exception."""
        exc = BusinessLogicException(message="Business rule violated")

        assert exc.message == "Business rule violated"
        assert exc.error_code == "BUSINESS_LOGIC_ERROR"
        assert exc.status_code == 400

    def test_initialization_with_rule(self):
        """Test business logic exception with rule context."""
        exc = BusinessLogicException(
            message="Cannot delete widget with dependencies",
            rule="widget_deletion_policy",
        )

        assert exc.details["violated_rule"] == "widget_deletion_policy"


class TestAuthenticationException:
    """Test AuthenticationException functionality."""

    def test_basic_initialization(self):
        """Test basic authentication exception."""
        exc = AuthenticationException()

        assert exc.message == "Authentication required"
        assert exc.error_code == "AUTHENTICATION_ERROR"
        assert exc.status_code == 401

    def test_custom_message(self):
        """Test authentication exception with custom message."""
        exc = AuthenticationException(message="Invalid credentials")

        assert exc.message == "Invalid credentials"


class TestAuthorizationException:
    """Test AuthorizationException functionality."""

    def test_basic_initialization(self):
        """Test basic authorization exception."""
        exc = AuthorizationException()

        assert exc.message == "Insufficient permissions"
        assert exc.error_code == "AUTHORIZATION_ERROR"
        assert exc.status_code == 403

    def test_initialization_with_resource_and_action(self):
        """Test authorization exception with resource and action."""
        exc = AuthorizationException(
            message="Cannot access resource",
            resource="widget",
            action="delete",
        )

        assert exc.details["resource"] == "widget"
        assert exc.details["action"] == "delete"


class TestRateLimitException:
    """Test RateLimitException functionality."""

    def test_basic_initialization(self):
        """Test basic rate limit exception."""
        exc = RateLimitException()

        assert exc.message == "Rate limit exceeded"
        assert exc.error_code == "RATE_LIMIT_ERROR"
        assert exc.status_code == 429

    def test_initialization_with_retry_after(self):
        """Test rate limit exception with retry after."""
        exc = RateLimitException(message="Too many requests", retry_after=60)

        assert exc.message == "Too many requests"
        assert exc.details["retry_after"] == 60


class TestExternalServiceException:
    """Test ExternalServiceException functionality."""

    def test_basic_initialization(self):
        """Test basic external service exception."""
        exc = ExternalServiceException(service_name="payment_gateway")

        assert exc.message == "External service unavailable"
        assert exc.error_code == "EXTERNAL_SERVICE_ERROR"
        assert exc.status_code == 503
        assert exc.details["service_name"] == "payment_gateway"

    def test_custom_message(self):
        """Test external service exception with custom message."""
        exc = ExternalServiceException(
            service_name="email_service", message="Service temporarily down"
        )

        assert exc.message == "Service temporarily down"
        assert exc.details["service_name"] == "email_service"


class TestWidgetException:
    """Test WidgetException functionality."""

    def test_basic_initialization(self):
        """Test basic widget exception."""
        exc = WidgetException(
            message="Widget error", error_code="WIDGET_ERROR"
        )

        assert exc.message == "Widget error"
        assert exc.error_code == "WIDGET_ERROR"
        assert exc.status_code == 400
        assert exc.details == {}

    def test_initialization_with_widget_id(self):
        """Test widget exception with widget ID."""
        exc = WidgetException(
            message="Widget error", error_code="WIDGET_ERROR", widget_id=123
        )

        assert exc.details["widget_id"] == 123

    def test_custom_status_code(self):
        """Test widget exception with custom status code."""
        exc = WidgetException(
            message="Widget error", error_code="WIDGET_ERROR", status_code=422
        )

        assert exc.status_code == 422


class TestWidgetNotFoundException:
    """Test WidgetNotFoundException functionality."""

    def test_basic_initialization(self):
        """Test basic widget not found exception."""
        exc = WidgetNotFoundException(widget_id=123)

        assert exc.message == "Widget with ID 123 not found"
        assert exc.error_code == "WIDGET_NOT_FOUND"
        assert exc.status_code == 404
        assert exc.details["widget_id"] == 123

    def test_custom_message(self):
        """Test widget not found with custom message."""
        exc = WidgetNotFoundException(
            widget_id=456, message="Specified widget does not exist"
        )

        assert exc.message == "Specified widget does not exist"
        assert exc.details["widget_id"] == 456


class TestWidgetValidationException:
    """Test WidgetValidationException functionality."""

    def test_basic_initialization(self):
        """Test basic widget validation exception."""
        exc = WidgetValidationException(message="Invalid widget data")

        assert exc.message == "Invalid widget data"
        assert exc.error_code == "WIDGET_VALIDATION_ERROR"
        assert exc.status_code == 400

    def test_initialization_with_field_errors(self):
        """Test widget validation exception with field errors."""
        field_errors = {"name": "Too long", "parts": "Must be positive"}
        exc = WidgetValidationException(
            message="Widget validation failed",
            field_errors=field_errors,
            widget_id=123,
        )

        assert exc.details["field_errors"] == field_errors
        assert exc.details["widget_id"] == 123


class TestWidgetDuplicateException:
    """Test WidgetDuplicateException functionality."""

    def test_basic_initialization(self):
        """Test basic widget duplicate exception."""
        exc = WidgetDuplicateException(field="name", value="Test Widget")

        expected_message = "Widget with name 'Test Widget' already exists"
        assert exc.message == expected_message
        assert exc.error_code == "WIDGET_DUPLICATE_ERROR"
        assert exc.status_code == 409
        assert exc.details["duplicate_field"] == "name"
        assert exc.details["duplicate_value"] == "Test Widget"

    def test_custom_message(self):
        """Test widget duplicate exception with custom message."""
        exc = WidgetDuplicateException(
            field="email",
            value="test@example.com",
            message="Email address already registered",
        )

        assert exc.message == "Email address already registered"
        assert exc.details["duplicate_field"] == "email"
        assert exc.details["duplicate_value"] == "test@example.com"


class TestExceptionInheritance:
    """Test exception inheritance relationships."""

    def test_widget_exceptions_inherit_from_widget_exception(self):
        """Test widget-specific exceptions inherit from WidgetException."""
        not_found = WidgetNotFoundException(widget_id=1)
        validation = WidgetValidationException(message="test")
        duplicate = WidgetDuplicateException(field="name", value="test")

        assert isinstance(not_found, WidgetException)
        assert isinstance(validation, WidgetException)
        assert isinstance(duplicate, WidgetException)

    def test_all_exceptions_inherit_from_base(self):
        """Test all exceptions inherit from BaseAPIException."""
        exceptions = [
            ValidationException(),
            ResourceNotFoundException("Test", 1),
            DatabaseException(),
            BusinessLogicException("test"),
            AuthenticationException(),
            AuthorizationException(),
            RateLimitException(),
            ExternalServiceException("test"),
            WidgetException("test", "TEST"),
            WidgetNotFoundException(1),
            WidgetValidationException("test"),
            WidgetDuplicateException("name", "test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, BaseAPIException)
            assert hasattr(exc, "message")
            assert hasattr(exc, "error_code")
            assert hasattr(exc, "status_code")
            assert hasattr(exc, "details")
            assert hasattr(exc, "to_dict")
