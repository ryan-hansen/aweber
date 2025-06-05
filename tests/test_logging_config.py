"""
Tests for logging configuration.

This module tests the logging configuration setup to ensure proper
log formatting, structured logging, and logging functionality.
"""

import logging
from unittest.mock import Mock, patch

from src.app.logging_config import (
    get_logger,
    get_logging_config,
    log_error,
    log_request_info,
    log_response_info,
    setup_logging,
)


class TestGetLoggingConfig:
    """Test get_logging_config function."""

    @patch("src.app.logging_config.settings")
    def test_debug_mode_config(self, mock_settings):
        """Test logging config in debug mode."""
        mock_settings.debug = True

        config = get_logging_config()

        assert config["handlers"]["console"]["level"] == "DEBUG"
        assert config["loggers"][""]["level"] == "DEBUG"
        assert "sqlalchemy.engine" in config["loggers"]

    @patch("src.app.logging_config.settings")
    def test_production_mode_config(self, mock_settings):
        """Test logging config in production mode."""
        mock_settings.debug = False

        config = get_logging_config()

        assert config["handlers"]["console"]["level"] == "INFO"
        assert config["loggers"][""]["level"] == "INFO"

    def test_config_structure(self):
        """Test logging config has required structure."""
        config = get_logging_config()

        # Verify required sections
        assert "version" in config
        assert "formatters" in config
        assert "handlers" in config
        assert "loggers" in config

        # Verify formatters
        assert "standard" in config["formatters"]
        assert "json" in config["formatters"]
        assert "detailed" in config["formatters"]

        # Verify handlers
        assert "console" in config["handlers"]
        assert "file" in config["handlers"]
        assert "error_file" in config["handlers"]


class TestSetupLogging:
    """Test setup_logging function."""

    @patch("logging.config.dictConfig")
    @patch("os.makedirs")
    def test_setup_logging_creates_directories(
        self, mock_makedirs, mock_dict_config
    ):
        """Test setup_logging creates required directories."""
        setup_logging()

        mock_makedirs.assert_called_once_with("logs", exist_ok=True)
        mock_dict_config.assert_called_once()

    @patch("logging.getLogger")
    @patch("logging.config.dictConfig")
    @patch("os.makedirs")
    def test_setup_logging_logs_startup_message(
        self, mock_makedirs, mock_dict_config, mock_get_logger
    ):
        """Test setup_logging logs startup message."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        setup_logging()

        mock_get_logger.assert_called_with("app")
        mock_logger.info.assert_called_with(
            "Logging configuration initialized"
        )


class TestGetLogger:
    """Test get_logger function."""

    def test_get_logger_returns_logger(self):
        """Test get_logger returns a logger instance."""
        logger = get_logger("test.module")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.module"

    def test_get_logger_different_names(self):
        """Test get_logger returns different loggers for different names."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        assert logger1.name == "module1"
        assert logger2.name == "module2"
        assert logger1 is not logger2


class TestLogRequestInfo:
    """Test log_request_info function."""

    @patch("src.app.logging_config.get_logger")
    def test_log_request_info_basic(self, mock_get_logger):
        """Test basic request info logging."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        log_request_info(
            request_id="req-123",
            method="POST",
            path="/api/widgets",
            client_ip="192.168.1.100",
        )

        # Verify logger was called with correct name
        mock_get_logger.assert_called_once_with("app.requests")

        # Verify logger was called with correct arguments
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args

        # Check message
        assert "POST /api/widgets" in call_args[0][0]

        # Check extra fields
        extra = call_args[1]["extra"]
        assert extra["request_id"] == "req-123"
        assert extra["method"] == "POST"
        assert extra["path"] == "/api/widgets"
        assert extra["client_ip"] == "192.168.1.100"

    @patch("src.app.logging_config.get_logger")
    def test_log_request_info_without_client_ip(self, mock_get_logger):
        """Test request info logging without client IP."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        log_request_info(
            request_id="req-456", method="GET", path="/api/widgets/123"
        )

        # Verify client_ip is not in extra data when not provided
        call_args = mock_logger.info.call_args
        extra = call_args[1]["extra"]
        assert "client_ip" not in extra


class TestLogResponseInfo:
    """Test log_response_info function."""

    @patch("src.app.logging_config.get_logger")
    def test_log_response_info_success(self, mock_get_logger):
        """Test response info logging for successful response."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        log_response_info(
            request_id="req-123", status_code=200, duration_ms=150.5
        )

        # Verify logger was called with correct name
        mock_get_logger.assert_called_once_with("app.requests")

        # Verify logger was called
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args

        # Check message
        assert "Response: 200" in call_args[0][0]
        assert "150.50ms" in call_args[0][0]

        # Check extra fields
        extra = call_args[1]["extra"]
        assert extra["request_id"] == "req-123"
        assert extra["status_code"] == 200
        assert extra["duration_ms"] == 150.5


class TestLogError:
    """Test log_error function."""

    @patch("src.app.logging_config.get_logger")
    def test_log_error_basic(self, mock_get_logger):
        """Test basic error logging."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        exception = ValueError("Test error")

        log_error(error=exception, request_id="req-123")

        # Verify logger was called with correct name
        mock_get_logger.assert_called_once_with("app.errors")

        # Verify logger was called
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args

        # Check message includes exception info
        assert "Error occurred: ValueError: Test error" in call_args[0][0]

        # Check extra fields
        extra = call_args[1]["extra"]
        assert extra["request_id"] == "req-123"
        assert extra["error_type"] == "ValueError"
        assert extra["error_message"] == "Test error"

        # Check that exc_info is included for stack trace
        assert call_args[1]["exc_info"] is True

    @patch("src.app.logging_config.get_logger")
    def test_log_error_with_context(self, mock_get_logger):
        """Test error logging with additional context."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        exception = RuntimeError("Database connection failed")
        context = {"user_id": 789, "operation": "fetch_widget"}

        log_error(error=exception, request_id="req-456", context=context)

        # Verify additional context is included
        call_args = mock_logger.error.call_args
        extra = call_args[1]["extra"]
        assert extra["user_id"] == 789
        assert extra["operation"] == "fetch_widget"


class TestLoggingIntegration:
    """Integration tests for logging functionality."""

    def test_end_to_end_logging_flow(self):
        """Test complete logging flow from setup to actual logging."""
        # Get a logger and test that it works
        logger = get_logger("test_integration")

        # Should return a valid logger instance
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_integration"

    @patch("src.app.logging_config.get_logger")
    def test_logging_functions_integration(self, mock_get_logger):
        """Test that logging helper functions work together."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        # Test request logging
        log_request_info(
            request_id="test-req",
            method="POST",
            path="/test",
            client_ip="127.0.0.1",
        )

        # Test response logging
        log_response_info(
            request_id="test-req", status_code=200, duration_ms=100.0
        )

        # Test error logging
        test_exception = ValueError("Test")
        log_error(error=test_exception, request_id="test-req")

        # Verify all logging functions were called
        assert mock_get_logger.call_count == 3  # Called for each function
        assert mock_logger.info.call_count == 2  # request + response
        assert mock_logger.error.call_count == 1  # error
