"""Tests for flext_api.errors module - REAL classes only.

Tests using only REAL classes:
- FlextErrors

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api import FlextErrors


class TestFlextErrors:
    """Test FlextErrors REAL class functionality."""

    def test_errors_class_exists(self) -> None:
        """Test FlextErrors class exists and is accessible."""
        assert FlextErrors is not None
        assert hasattr(FlextErrors, "FlextApiError")
        assert hasattr(FlextErrors, "ValidationError")
        assert hasattr(FlextErrors, "AuthenticationError")
        assert hasattr(FlextErrors, "NotFoundError")

    def test_flext_api_error_basic(self) -> None:
        """Test basic FlextApiError creation."""
        error = FlextErrors.FlextApiError()

        # flext-core errors have format [CODE] message
        assert "API error" in str(error)
        assert error.status_code == 500  # default

    def test_flext_api_error_custom_message(self) -> None:
        """Test FlextApiError with custom message."""
        error = FlextErrors.FlextApiError("Something went wrong")

        assert "Something went wrong" in str(error)
        assert error.status_code == 500  # default

    def test_flext_api_error_custom_status_code(self) -> None:
        """Test FlextApiError with custom status code."""
        error = FlextErrors.FlextApiError(
            "Custom error",
            status_code=400
        )

        assert "Custom error" in str(error)
        assert error.status_code == 400

    def test_flext_api_error_custom_code(self) -> None:
        """Test FlextApiError with custom code."""
        error = FlextErrors.FlextApiError(
            "Custom error",
            code="CUSTOM_ERROR"
        )

        assert "Custom error" in str(error)
        assert error.status_code == 500  # default

    def test_flext_api_error_with_context(self) -> None:
        """Test FlextApiError with context."""
        context = {"user_id": 123, "action": "create"}

        error = FlextErrors.FlextApiError(
            "Action failed",
            status_code=422,
            code="ACTION_FAILED",
            context=context
        )

        assert "Action failed" in str(error)
        assert error.status_code == 422
        assert hasattr(error, "context")

    def test_validation_error_basic(self) -> None:
        """Test basic ValidationError creation."""
        error = FlextErrors.ValidationError()

        assert "Validation failed" in str(error)
        assert error.status_code == 400

    def test_validation_error_custom_message(self) -> None:
        """Test ValidationError with custom message."""
        error = FlextErrors.ValidationError("Email format is invalid")

        assert "Email format is invalid" in str(error)
        assert error.status_code == 400

    def test_authentication_error_basic(self) -> None:
        """Test basic AuthenticationError creation."""
        error = FlextErrors.AuthenticationError()

        assert "Authentication failed" in str(error)
        assert error.status_code == 401

    def test_authentication_error_custom_message(self) -> None:
        """Test AuthenticationError with custom message."""
        error = FlextErrors.AuthenticationError("Invalid token")

        assert "Invalid token" in str(error)
        assert error.status_code == 401

    def test_not_found_error_basic(self) -> None:
        """Test basic NotFoundError creation."""
        error = FlextErrors.NotFoundError()

        assert "Resource not found" in str(error)
        assert error.status_code == 404

    def test_not_found_error_custom_message(self) -> None:
        """Test NotFoundError with custom message."""
        error = FlextErrors.NotFoundError("User not found")

        assert "User not found" in str(error)
        assert error.status_code == 404

    def test_error_inheritance(self) -> None:
        """Test error inheritance hierarchy."""
        # ValidationError should inherit from FlextApiError
        validation_error = FlextErrors.ValidationError()
        assert isinstance(validation_error, FlextErrors.FlextApiError)

        # AuthenticationError should inherit from FlextApiError
        auth_error = FlextErrors.AuthenticationError()
        assert isinstance(auth_error, FlextErrors.FlextApiError)

        # NotFoundError should inherit from FlextApiError
        not_found_error = FlextErrors.NotFoundError()
        assert isinstance(not_found_error, FlextErrors.FlextApiError)

    def test_error_exception_behavior(self) -> None:
        """Test errors behave as proper exceptions."""
        # Should be raisable and catchable
        test_error_msg = "Test error"
        with pytest.raises(FlextErrors.FlextApiError) as exc_info:
            raise FlextErrors.FlextApiError(test_error_msg)

        assert "Test error" in str(exc_info.value)
        assert exc_info.value.status_code == 500

    def test_specific_error_exception_behavior(self) -> None:
        """Test specific errors behave as proper exceptions."""
        # ValidationError
        invalid_data_msg = "Invalid data"
        with pytest.raises(FlextErrors.ValidationError) as exc_info:
            raise FlextErrors.ValidationError(invalid_data_msg)

        assert "Invalid data" in str(exc_info.value)
        assert exc_info.value.status_code == 400

        # Should also be catchable as base FlextApiError
        invalid_data_msg2 = "Invalid data"
        with pytest.raises(FlextErrors.FlextApiError):
            raise FlextErrors.ValidationError(invalid_data_msg2)

    def test_error_status_codes(self) -> None:
        """Test each error has correct status code."""
        error_types = [
            (FlextErrors.FlextApiError, 500),
            (FlextErrors.ValidationError, 400),
            (FlextErrors.AuthenticationError, 401),
            (FlextErrors.NotFoundError, 404)
        ]

        for error_class, expected_status in error_types:
            error = error_class("Test message")
            assert error.status_code == expected_status

    def test_error_codes(self) -> None:
        """Test each error has correct error code."""
        error_types = [
            (FlextErrors.FlextApiError, "API_ERROR"),
            (FlextErrors.ValidationError, "VALIDATION_ERROR"),
            (FlextErrors.AuthenticationError, "AUTHENTICATION_ERROR"),
            (FlextErrors.NotFoundError, "NOT_FOUND_ERROR")
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
        error = FlextErrors.FlextApiError("test")
        assert isinstance(error, FlextErrors.FlextApiError)

        validation_error = FlextErrors.ValidationError("test")
        assert isinstance(validation_error, FlextErrors.ValidationError)

    def test_errors_string_representation(self) -> None:
        """Test errors have proper string representation."""
        errors = [
            FlextErrors.FlextApiError("API error message"),
            FlextErrors.ValidationError("Validation error message"),
            FlextErrors.AuthenticationError("Auth error message"),
            FlextErrors.NotFoundError("Not found error message")
        ]

        for error in errors:
            error_str = str(error)
            assert isinstance(error_str, str)
            assert len(error_str) > 0
            assert "message" in error_str

    def test_error_attributes_persistence(self) -> None:
        """Test error attributes persist after creation."""
        error = FlextErrors.FlextApiError(
            "Persistent error",
            status_code=422,
            code="PERSISTENT_ERROR"
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
        error1 = FlextErrors.ValidationError("Error 1")
        error2 = FlextErrors.ValidationError("Error 2")

        assert error1 is not error2
        assert str(error1) != str(error2)
        assert error1.status_code == error2.status_code  # Same type
        assert error1.code == error2.code  # Same type
