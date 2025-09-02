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

    def test_flext_api_error_creation(self) -> None:
        """Test FlextApiError creation."""
        error = FlextErrors.FlextApiError("Test error message")

        assert "Test error message" in str(error)
        assert isinstance(error, Exception)

    def test_flext_api_error_with_code(self) -> None:
        """Test FlextApiError creation with error code."""
        error = FlextErrors.FlextApiError("Test error", code="TEST_001")

        assert "Test error" in str(error)
        assert error.code == "TEST_001"

    def test_flext_api_error_inheritance(self) -> None:
        """Test that FlextApiError inherits properly."""
        error = FlextErrors.FlextApiError("Test error")

        # Should inherit from base FlextError from flext-core
        assert hasattr(error, "message")
        assert error.message == "Test error"

    def test_error_context_data(self) -> None:
        """Test error context data."""
        context = {"user_id": 123, "action": "create_user"}
        error = FlextErrors.FlextApiError("Operation failed", context=context)

        assert error.context == context
        assert error.context["user_id"] == 123
        assert error.context["action"] == "create_user"

    def test_error_serialization(self) -> None:
        """Test error serialization to dict."""
        error = FlextErrors.FlextApiError(
            "Test error", code="TEST_001", context={"key": "value"}
        )

        error_dict = error.to_dict()

        assert error_dict["message"] == "Test error"
        assert error_dict["code"] == "TEST_001"
        assert error_dict["context"]["key"] == "value"

    def test_multiple_error_instances(self) -> None:
        """Test multiple error instances are independent."""
        error1 = FlextErrors.FlextApiError("Error 1", code="ERR_001")
        error2 = FlextErrors.FlextApiError("Error 2", code="ERR_002")

        assert str(error1) != str(error2)
        assert error1.code != error2.code

    def test_error_raising(self) -> None:
        """Test that errors can be raised properly."""
        msg = "Test error for raising"
        with pytest.raises(FlextErrors.FlextApiError) as exc_info:
            raise FlextErrors.FlextApiError(msg)

        assert "Test error for raising" in str(exc_info.value)

    def test_error_chaining(self) -> None:
        """Test error chaining with __cause__."""
        original_error = ValueError("Original error")

        def raise_chained_error() -> None:
            try:
                raise original_error
            except ValueError as e:
                msg = "Chained error"
                raise FlextErrors.FlextApiError(msg) from e

        with pytest.raises(FlextErrors.FlextApiError) as exc_info:
            raise_chained_error()

        chained_error = exc_info.value
        assert chained_error.__cause__ is original_error
