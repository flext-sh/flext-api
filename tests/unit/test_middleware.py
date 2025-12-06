"""Comprehensive tests for FlextApiMiddleware.

Tests validate middleware pipeline processing using real functions.
No mocks - uses actual middleware functions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api.middleware import FlextApiMiddleware


class TestFlextApiMiddleware:
    """Test HTTP middleware functionality."""

    def test_apply_pipeline_empty_list(self) -> None:
        """Test applying empty middleware pipeline."""
        request = {"method": "GET", "url": "/test"}

        result = FlextApiMiddleware.apply_pipeline(request, [])

        assert result is request

    def test_apply_pipeline_single_middleware(self) -> None:
        """Test applying single middleware."""
        request = {"method": "GET", "url": "/test"}

        def add_header(req: dict[str, str]) -> dict[str, str]:
            req["headers"] = {"User-Agent": "Test"}
            return req

        result = FlextApiMiddleware.apply_pipeline(request, [add_header])

        assert result is request
        assert "headers" in result
        assert result["headers"]["User-Agent"] == "Test"

    def test_apply_pipeline_multiple_middleware(self) -> None:
        """Test applying multiple middleware."""
        request = {"method": "GET", "url": "/test"}

        def add_method(req: dict[str, str]) -> dict[str, str]:
            req["method"] = req.get("method", "GET").upper()
            return req

        def add_url(req: dict[str, str]) -> dict[str, str]:
            req["full_url"] = f"http://example.com{req.get('url', '')}"
            return req

        result = FlextApiMiddleware.apply_pipeline(request, [add_method, add_url])

        assert result is request
        assert result["method"] == "GET"
        assert result["full_url"] == "http://example.com/test"

    def test_apply_pipeline_middleware_exception(self) -> None:
        """Test middleware that raises exception continues pipeline."""
        request = {"method": "GET", "url": "/test"}

        def failing_middleware(req: dict[str, str]) -> dict[str, str]:
            msg = "Test failure"
            raise ValueError(msg)

        def succeeding_middleware(req: dict[str, str]) -> dict[str, str]:
            req["success"] = True
            return req

        result = FlextApiMiddleware.apply_pipeline(
            request,
            [failing_middleware, succeeding_middleware],
        )

        assert result is request
        assert result.get("success") is True

    def test_log_request(self) -> None:
        """Test request logging middleware."""
        request = {"method": "GET", "url": "/test"}

        result = FlextApiMiddleware.log_request(request)

        assert result is request

    def test_validate_request(self) -> None:
        """Test request validation middleware."""
        request = {"method": "GET", "url": "/test"}

        result = FlextApiMiddleware.validate_request(request)

        assert result is request
