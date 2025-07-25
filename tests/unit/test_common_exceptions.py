"""Tests for common exception utilities with 100% coverage.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from flext_core import FlextError

from flext_api.common.exceptions import ensure_service_available, handle_api_exceptions


class TestEnsureServiceAvailable:
    """Test ensure_service_available function."""

    def test_service_available_success(self) -> None:
        """Test that available service passes check."""
        service = "mock_service"
        service_name = "Test Service"

        # Should not raise exception
        ensure_service_available(service, service_name)

    def test_service_unavailable_raises_http_exception(self) -> None:
        """Test that None service raises HTTPException."""
        service = None
        service_name = "Test Service"

        with pytest.raises(HTTPException) as exc_info:
            ensure_service_available(service, service_name)

        assert exc_info.value.status_code == 503
        assert "Test Service not available - register implementation" in str(
            exc_info.value.detail,
        )

    def test_different_service_names(self) -> None:
        """Test with different service names."""
        with pytest.raises(HTTPException) as exc_info:
            ensure_service_available(None, "Plugin Manager")

        assert "Plugin Manager not available - register implementation" in str(
            exc_info.value.detail,
        )

        with pytest.raises(HTTPException) as exc_info:
            ensure_service_available(None, "Database Connection")

        assert "Database Connection not available - register implementation" in str(
            exc_info.value.detail,
        )


class TestHandleApiExceptions:
    """Test handle_api_exceptions decorator."""

    def test_successful_operation(self) -> None:
        """Test decorator with successful operation."""

        @handle_api_exceptions("test operation")
        async def successful_function() -> str:
            return "success"

        import asyncio

        result = asyncio.run(successful_function())
        assert result == "success"

    def test_http_exception_passthrough(self) -> None:
        """Test that HTTPException is re-raised as-is."""

        @handle_api_exceptions("test operation")
        async def http_exception_function() -> None:
            raise HTTPException(status_code=400, detail="Bad Request")

        import asyncio

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(http_exception_function())

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Bad Request"

    def test_generic_exception_conversion(self) -> None:
        """Test that generic Exception is converted to HTTPException."""

        @handle_api_exceptions("test operation")
        async def generic_exception_function() -> None:
            msg = "Something went wrong"
            raise ValueError(msg)

        import asyncio

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(generic_exception_function())

        assert exc_info.value.status_code == 500
        assert "Failed to test operation: Something went wrong" in str(
            exc_info.value.detail,
        )

    def test_operation_name_in_error_message(self) -> None:
        """Test that operation name appears in error message."""

        @handle_api_exceptions("install plugin")
        async def failing_function() -> None:
            msg = "Installation failed"
            raise FlextError(msg)

        import asyncio

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(failing_function())

        assert exc_info.value.status_code == 500
        assert "Failed to install plugin: Installation failed" in str(
            exc_info.value.detail,
        )

    def test_preserves_function_metadata(self) -> None:
        """Test that decorator preserves function metadata."""

        @handle_api_exceptions("test operation")
        async def documented_function() -> str:
            """A documented function."""
            return "result"

        assert documented_function.__name__ == "documented_function"
        assert "A documented function." in documented_function.__doc__

    def test_handles_async_functions(self) -> None:
        """Test decorator works with async functions."""

        @handle_api_exceptions("async operation")
        async def async_function() -> str:
            await asyncio.sleep(0.001)  # Simulate async work
            return "async_result"

        import asyncio

        result = asyncio.run(async_function())
        assert result == "async_result"

    def test_exception_chaining_preserved(self) -> None:
        """Test that exception chaining is preserved."""
        original_exception = ValueError("Original error")

        @handle_api_exceptions("chaining test")
        async def chaining_function() -> None:
            raise original_exception

        import asyncio

        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(chaining_function())

        assert exc_info.value.__cause__ is original_exception
