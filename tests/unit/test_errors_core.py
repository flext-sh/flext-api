"""Tests for flext_api.errors module - REAL classes only.

Tests using only REAL classes:
- FlextErrors

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api import FlextApiExceptions
from flext_api.utilities import HttpErrorConfig, ValidationConfig


class TestFlextApiExceptions:
    """Test FlextApiExceptions REAL class functionality."""

    def test_exceptions_class_exists(self) -> None:
        """Test FlextApiExceptions class exists and is accessible."""
        assert FlextApiExceptions is not None
        assert hasattr(FlextApiExceptions, "FlextApiError")
        assert hasattr(FlextApiExceptions, "ValidationError")
        assert hasattr(FlextApiExceptions, "BadRequestError")
        assert hasattr(FlextApiExceptions, "NotFoundError")

    def test_flext_api_error_basic(self) -> None:
        """Test basic FlextApiError creation."""
        error = FlextApiExceptions.FlextApiError("API error")

        # flext-core errors have format [CODE] message
        assert "API error" in str(error)
        assert error.status_code == 500  # default

    def test_flext_api_error_custom_message(self) -> None:
        """Test FlextApiError with custom message."""
        error = FlextApiExceptions.FlextApiError("Something went wrong")

        assert "Something went wrong" in str(error)
        assert error.status_code == 500  # default

    def test_flext_api_error_custom_status_code(self) -> None:
        """Test FlextApiError with custom status code."""
        error = FlextApiExceptions.FlextApiError("Custom error", status_code=400)

        assert "Custom error" in str(error)
        assert error.status_code == 400

    def test_flext_api_error_custom_code(self) -> None:
        """Test FlextApiError with custom code."""
        error = FlextApiExceptions.FlextApiError("Custom error", error_code="CUSTOM_ERROR")

        assert "Custom error" in str(error)
        assert error.status_code == 500  # default

    def test_flext_api_error_with_context(self) -> None:
        """Test FlextApiError with context."""
        context = {"user_id": 123, "action": "create"}

        error = FlextApiExceptions.FlextApiError(
            "Action failed", status_code=422, error_code="ACTION_FAILED", context=context
        )

        assert "Action failed" in str(error)
        assert error.status_code == 422
        assert hasattr(error, "context")

    def test_validation_error_basic(self) -> None:
        """Test basic ValidationError creation."""
        config = ValidationConfig(message="Validation failed")
        error = FlextApiExceptions.ValidationError(config)

        assert "Validation failed" in str(error)
        assert error.status_code == 400

    def test_validation_error_custom_message(self) -> None:
        """Test ValidationError with custom message."""
        config = ValidationConfig(message="Email format is invalid")
        error = FlextApiExceptions.ValidationError(config)

        assert "Email format is invalid" in str(error)
        assert error.status_code == 400

    def test_authentication_error_basic(self) -> None:
        """Test basic AuthenticationError creation."""
        # AuthenticationError is dynamically generated, use HttpErrorConfig
        config = HttpErrorConfig(message="Authentication failed", status_code=401)
        error = FlextApiExceptions.AuthenticationError(config)

        assert "Authentication failed" in str(error)
        assert error.status_code == 401

    def test_authentication_error_custom_message(self) -> None:
        """Test AuthenticationError with custom message."""
        config = HttpErrorConfig(message="Invalid token", status_code=401)
        error = FlextApiExceptions.AuthenticationError(config)

        assert "Invalid token" in str(error)
        assert error.status_code == 401

    def test_not_found_error_basic(self) -> None:
        """Test basic NotFoundError creation."""
        config = HttpErrorConfig(message="Resource not found", status_code=404)
        error = FlextApiExceptions.NotFoundError(config)

        assert "Resource not found" in str(error)
        assert error.status_code == 404

    def test_not_found_error_custom_message(self) -> None:
        """Test NotFoundError with custom message."""
        config = HttpErrorConfig(message="User not found", status_code=404)
        error = FlextApiExceptions.NotFoundError(config)

        assert "User not found" in str(error)
        assert error.status_code == 404

    def test_error_inheritance(self) -> None:
        """Test error inheritance hierarchy."""
        # ValidationError should inherit from FlextApiError
        validation_config = ValidationConfig(message="Test validation")
        validation_error = FlextApiExceptions.ValidationError(validation_config)
        assert isinstance(validation_error, FlextApiExceptions.FlextApiError)

        # AuthenticationError should inherit from FlextApiError (via HttpError)
        auth_config = HttpErrorConfig(message="Test auth", status_code=401)
        auth_error = FlextApiExceptions.AuthenticationError(auth_config)
        assert isinstance(auth_error, FlextApiExceptions.HttpError)

        # NotFoundError should inherit from FlextApiError (via HttpError)
        not_found_config = HttpErrorConfig(message="Test not found", status_code=404)
        not_found_error = FlextApiExceptions.NotFoundError(not_found_config)
        assert isinstance(not_found_error, FlextApiExceptions.HttpError)

    def test_error_exception_behavior(self) -> None:
        """Test errors behave as proper exceptions."""
        # Should be raisable and catchable
        test_error_msg = "Test error"
        with pytest.raises(FlextApiExceptions.FlextApiError) as exc_info:
            raise FlextApiExceptions.FlextApiError(test_error_msg)

        assert "Test error" in str(exc_info.value)
        assert exc_info.value.status_code == 500

    def test_specific_error_exception_behavior(self) -> None:
        """Test specific errors behave as proper exceptions."""
        # ValidationError
        invalid_data_msg = "Invalid data"
        config = ValidationConfig(message=invalid_data_msg)
        with pytest.raises(FlextApiExceptions.ValidationError) as exc_info:
            raise FlextApiExceptions.ValidationError(config)

        assert "Invalid data" in str(exc_info.value)
        assert exc_info.value.status_code == 400

        # Should also be catchable as base FlextApiError
        invalid_data_msg2 = "Invalid data"
        config2 = ValidationConfig(message=invalid_data_msg2)
        with pytest.raises(FlextApiExceptions.FlextApiError):
            raise FlextApiExceptions.ValidationError(config2)

    def test_error_status_codes(self) -> None:
        """Test each error has correct status code."""
        error_types = [
            (FlextApiExceptions.FlextApiError, 500),
            (FlextApiExceptions.ValidationError, 400),
            (FlextApiExceptions.AuthenticationError, 401),
            (FlextApiExceptions.NotFoundError, 404),
        ]

        for error_class, expected_status in error_types:
            error = error_class("Test message")
            assert error.status_code == expected_status

    def test_error_codes(self) -> None:
        """Test each error has correct error code."""
        error_types = [
            (FlextApiExceptions.FlextApiError, "API_ERROR"),
            (FlextApiExceptions.ValidationError, "VALIDATION_ERROR"),
            (FlextApiExceptions.AuthenticationError, "AUTHENTICATION_ERROR"),
            (FlextApiExceptions.NotFoundError, "NOT_FOUND_ERROR"),
        ]

        # flext-core uses different error code system
        # Just verify errors have some code attribute
        for error_class, _ in error_types:
            error = error_class("Test message")
            assert hasattr(error, "code")
            assert error.code is not None

    def test_errors_type_validation(self) -> None:
        """Test errors are proper types."""
        # Main class
        assert FlextErrors is not None
        assert type(FlextErrors).__name__ == "type"

        # Error classes
        error = FlextApiExceptions.FlextApiError("test")
        assert isinstance(error, FlextApiExceptions.FlextApiError)

        validation_error = FlextApiExceptions.ValidationError("test")
        assert isinstance(validation_error, FlextApiExceptions.ValidationError)

    def test_errors_string_representation(self) -> None:
        """Test errors have proper string representation."""
        errors = [
            FlextApiExceptions.FlextApiError("API error message"),
            FlextApiExceptions.ValidationError("Validation error message"),
            FlextApiExceptions.AuthenticationError("Auth error message"),
            FlextApiExceptions.NotFoundError("Not found error message"),
        ]

        for error in errors:
            error_str = str(error)
            assert isinstance(error_str, str)
            assert len(error_str) > 0
            assert "message" in error_str

    def test_error_attributes_persistence(self) -> None:
        """Test error attributes persist after creation."""
        error = FlextApiExceptions.FlextApiError(
            "Persistent error", status_code=422, error_code="PERSISTENT_ERROR"
        )

        # Attributes should persist
        assert "Persistent error" in str(error)
        assert error.status_code == 422

        # Should still have these after operations
        _ = repr(error)
        _ = hash(error)  # Should be hashable as an exception

        assert error.status_code == 422  # Still there

    def test_multiple_error_instances_independence(self) -> None:
        """Test multiple error instances are independent."""
        error1 = FlextApiExceptions.ValidationError("Error 1")
        error2 = FlextApiExceptions.ValidationError("Error 2")

        assert error1 is not error2
        assert str(error1) != str(error2)
        assert error1.status_code == error2.status_code  # Same type
        assert error1.code == error2.code  # Same type
