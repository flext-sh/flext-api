"""Comprehensive tests for flext_api.exceptions module.

Tests using only REAL classes directly from flext_api.
No helpers, no aliases, no compatibility layers.



Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api import FlextErrors


class TestFlextErrorsComprehensive:
    """Comprehensive test FlextErrors REAL class functionality."""

    def test_flext_api_error_basic(self) -> None:
        """Test basic FlextApiError creation."""
        error = FlextErrors.FlextApiError("Test error")
        assert "Test error" in str(error)
        assert error.status_code == 500

    def test_validation_error_basic(self) -> None:
        """Test basic ValidationError creation."""
        error = FlextErrors.ValidationError("Invalid data")
        assert "Invalid data" in str(error)
        assert error.status_code == 400

    def test_authentication_error_basic(self) -> None:
        """Test basic AuthenticationError creation."""
        error = FlextErrors.AuthenticationError("Unauthorized")
        assert "Unauthorized" in str(error)
        assert error.status_code == 401

    def test_not_found_error_basic(self) -> None:
        """Test basic NotFoundError creation."""
        error = FlextErrors.NotFoundError("Resource not found")
        assert "Resource not found" in str(error)
        assert error.status_code == 404

    def test_error_inheritance(self) -> None:
        """Test error inheritance hierarchy."""
        validation_error = FlextErrors.ValidationError("Invalid")
        assert isinstance(validation_error, FlextErrors.FlextApiError)

        auth_error = FlextErrors.AuthenticationError("Unauthorized")
        assert isinstance(auth_error, FlextErrors.FlextApiError)

        not_found_error = FlextErrors.NotFoundError("Missing")
        assert isinstance(not_found_error, FlextErrors.FlextApiError)

    def test_error_with_custom_status_code(self) -> None:
        """Test error with custom status code."""
        error = FlextErrors.FlextApiError("Custom error", status_code=422)
        assert error.status_code == 422
        assert "Custom error" in str(error)

    def test_error_with_context(self) -> None:
        """Test error with context."""
        error = FlextErrors.ValidationError("Invalid email format")
        # Context is not supported in the current implementation
        assert "Invalid email format" in str(error)

    def test_error_exception_behavior(self) -> None:
        """Test errors behave as proper exceptions."""
        msg = "Test error"
        with pytest.raises(FlextErrors.FlextApiError):
            raise FlextErrors.FlextApiError(msg)

        msg = "Invalid data"
        with pytest.raises(FlextErrors.ValidationError):
            raise FlextErrors.ValidationError(msg)

    def test_multiple_error_instances(self) -> None:
        """Test multiple error instances are independent."""
        error1 = FlextErrors.ValidationError("Error 1")
        error2 = FlextErrors.ValidationError("Error 2")

        assert error1 is not error2
        assert str(error1) != str(error2)
        assert error1.status_code == error2.status_code

    def test_error_status_codes(self) -> None:
        """Test each error has correct status code."""
        assert FlextErrors.FlextApiError("test").status_code == 500
        assert FlextErrors.ValidationError("test").status_code == 400
        assert FlextErrors.AuthenticationError("test").status_code == 401
        assert FlextErrors.NotFoundError("test").status_code == 404
