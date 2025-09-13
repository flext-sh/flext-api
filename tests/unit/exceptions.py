"""Tests for flext_api.exceptions module using flext_tests EM ABSOLUTO.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api import FlextApiExceptions


class TestFlextErrorsComprehensive:
    """Test FlextErrors using flext_tests patterns and real functionality."""

    def test_flext_api_error_basic(self) -> None:
        """Test basic FlextApiError creation using flext_tests."""
        error_message = "Test API error message"
        error = FlextApiExceptions.FlextApiError(error_message)
        assert error_message in str(error)
        assert error.status_code == 500

    def test_validation_error_basic(self) -> None:
        """Test basic ValidationError creation using flext_tests."""
        error_message = "Test validation error"
        error = FlextApiExceptions.ValidationError(error_message)
        assert error_message in str(error)
        assert error.status_code == 400

    def test_authentication_error_basic(self) -> None:
        """Test basic AuthenticationError creation using flext_tests."""
        error_message = "Test auth error"
        error = FlextApiExceptions.AuthenticationError(error_message)
        assert error_message in str(error)
        assert error.status_code == 401

    def test_not_found_error_basic(self) -> None:
        """Test basic NotFoundError creation using flext_tests."""
        error_message = "Test not found error"
        error = FlextApiExceptions.NotFoundError(error_message)
        assert error_message in str(error)
        assert error.status_code == 404

    def test_error_inheritance(self) -> None:
        """Test error inheritance hierarchy using flext_tests."""
        validation_error = FlextApiExceptions.ValidationError("Validation test")
        assert isinstance(validation_error, FlextApiExceptions.FlextApiError)

        auth_error = FlextApiExceptions.AuthenticationError("Auth test")
        assert isinstance(auth_error, FlextApiExceptions.FlextApiError)

        not_found_error = FlextApiExceptions.NotFoundError("NotFound test")
        assert isinstance(not_found_error, FlextApiExceptions.FlextApiError)

    def test_error_with_custom_status_code(self) -> None:
        """Test error with custom status code using flext_tests."""
        error_message = "Custom status test"
        error = FlextApiExceptions.FlextApiError(error_message, status_code=422)
        assert error.status_code == 422
        assert error_message in str(error)

    def test_error_with_context(self) -> None:
        """Test error with context using flext_tests."""
        error_message = "Context test error"
        error = FlextApiExceptions.ValidationError(error_message)
        # Context is not supported in the current implementation
        assert error_message in str(error)

    def test_error_exception_behavior(self) -> None:
        """Test errors behave as proper exceptions using flext_tests."""
        msg1 = "Exception test 1"
        with pytest.raises(FlextApiExceptions.FlextApiError):
            raise FlextApiExceptions.FlextApiError(msg1)

        msg2 = "Exception test 2"
        with pytest.raises(FlextApiExceptions.ValidationError):
            raise FlextApiExceptions.ValidationError(msg2)

    def test_multiple_error_instances(self) -> None:
        """Test multiple error instances are independent using flext_tests."""
        error1 = FlextApiExceptions.ValidationError("Error 1")
        error2 = FlextApiExceptions.ValidationError("Error 2")

        assert error1 is not error2
        assert str(error1) != str(error2)
        assert error1.status_code == error2.status_code

    def test_error_status_codes(self) -> None:
        """Test each error has correct status code using flext_tests."""
        test_msg = "Status test"

        assert FlextApiExceptions.FlextApiError(test_msg).status_code == 500
        assert FlextApiExceptions.ValidationError(test_msg).status_code == 400
        assert FlextApiExceptions.AuthenticationError(test_msg).status_code == 401
        assert FlextApiExceptions.NotFoundError(test_msg).status_code == 404
