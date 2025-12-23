"""Unit tests for HTTP middleware functionality.

Tests FlextApiMiddleware with proper mocking and no fallbacks.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_api import FlextApiModels
from flext_api.middleware import FlextApiMiddleware


class TestFlextApiMiddleware:
    """Unit tests for HTTP middleware."""

    @pytest.fixture
    def sample_request(self) -> FlextApiModels.HttpRequest:
        """Create a sample HTTP request for testing."""
        return FlextApiModels.HttpRequest(
            method="GET",
            url="https://api.example.com/test",
            headers={"Content-Type": "application/json"},
            body=b'{"test": "data"}',
        )

    def test_apply_pipeline_empty_list(self, sample_request: FlextApiModels.HttpRequest) -> None:
        """Test applying empty middleware pipeline returns original request."""
        result = FlextApiMiddleware.apply_pipeline(sample_request, [])

        assert result is sample_request

    def test_apply_pipeline_single_middleware(self, sample_request: FlextApiModels.HttpRequest) -> None:
        """Test applying single middleware function."""
        def test_middleware(req: FlextApiModels.HttpRequest) -> FlextApiModels.HttpRequest:
            req.headers["X-Test"] = "modified"
            return req

        result = FlextApiMiddleware.apply_pipeline(sample_request, [test_middleware])

        assert result.headers["X-Test"] == "modified"
        assert result is sample_request  # Same object modified

    def test_apply_pipeline_multiple_middleware(self, sample_request: FlextApiModels.HttpRequest) -> None:
        """Test applying multiple middleware functions in order."""
        def middleware1(req: FlextApiModels.HttpRequest) -> FlextApiModels.HttpRequest:
            req.headers["X-Step"] = "1"
            return req

        def middleware2(req: FlextApiModels.HttpRequest) -> FlextApiModels.HttpRequest:
            req.headers["X-Step"] = req.headers.get("X-Step", "") + "2"
            return req

        result = FlextApiMiddleware.apply_pipeline(sample_request, [middleware1, middleware2])

        assert result.headers["X-Step"] == "12"

    def test_apply_pipeline_middleware_exception_handling(self, sample_request: FlextApiModels.HttpRequest) -> None:
        """Test that middleware exceptions are handled gracefully."""
        def failing_middleware(req: FlextApiModels.HttpRequest) -> FlextApiModels.HttpRequest:
            raise ValueError("Middleware failed")

        def working_middleware(req: FlextApiModels.HttpRequest) -> FlextApiModels.HttpRequest:
            req.headers["X-Success"] = "true"
            return req

        # Should not raise exception, should continue with next middleware
        result = FlextApiMiddleware.apply_pipeline(
            sample_request,
            [failing_middleware, working_middleware]
        )

        assert result.headers["X-Success"] == "true"

    def test_log_request_returns_same_request(self, sample_request: FlextApiModels.HttpRequest) -> None:
        """Test log_request middleware returns the same request."""
        result = FlextApiMiddleware.log_request(sample_request)

        assert result is sample_request

    def test_validate_request_returns_same_request(self, sample_request: FlextApiModels.HttpRequest) -> None:
        """Test validate_request middleware returns the same request."""
        result = FlextApiMiddleware.validate_request(sample_request)

        assert result is sample_request

    def test_middleware_functions_are_callable(self) -> None:
        """Test that all middleware methods are callable."""
        assert callable(FlextApiMiddleware.apply_pipeline)
        assert callable(FlextApiMiddleware.log_request)
        assert callable(FlextApiMiddleware.validate_request)
