"""Tests for FlextAPI middleware."""

from __future__ import annotations

from flext_api.middleware import FlextApiMiddleware


class TestFlextApiMiddleware:
    """Test FlextApiMiddleware functionality."""

    def test_apply_pipeline_empty_middleware_list(self) -> None:
        """Test apply_pipeline with empty middleware list."""
        request = {"method": "GET", "path": "/api/test"}
        result = FlextApiMiddleware.apply_pipeline(request, [])
        assert result == request

    def test_apply_pipeline_single_middleware(self) -> None:
        """Test apply_pipeline with single middleware function."""
        request = {"method": "GET", "path": "/api/test"}

        def add_header(req: dict) -> dict:
            req["headers"] = {"Content-Type": "application/json"}
            return req

        result = FlextApiMiddleware.apply_pipeline(request, [add_header])
        assert result["headers"] == {"Content-Type": "application/json"}

    def test_apply_pipeline_multiple_middleware(self) -> None:
        """Test apply_pipeline with multiple middleware functions."""
        request = {"method": "GET", "path": "/api/test"}

        def add_header(req: dict) -> dict:
            req["headers"] = {"Content-Type": "application/json"}
            return req

        def add_auth(req: dict) -> dict:
            req["headers"]["Authorization"] = "Bearer token"
            return req

        result = FlextApiMiddleware.apply_pipeline(request, [add_header, add_auth])
        assert result["headers"]["Content-Type"] == "application/json"
        assert result["headers"]["Authorization"] == "Bearer token"

    def test_apply_pipeline_with_exception(self) -> None:
        """Test apply_pipeline continues after middleware exception."""
        request = {"method": "GET", "path": "/api/test"}

        def failing_middleware(req: dict) -> dict:
            msg = "Middleware failed"
            raise ValueError(msg)

        def successful_middleware(req: dict) -> dict:
            req["processed"] = True
            return req

        # Should continue despite exception
        result = FlextApiMiddleware.apply_pipeline(
            request, [failing_middleware, successful_middleware]
        )
        assert result.get("processed") is True

    def test_log_request_returns_request(self) -> None:
        """Test log_request returns the request unchanged."""
        request = {"method": "GET", "path": "/api/test", "headers": {}}
        result = FlextApiMiddleware.log_request(request)
        assert result == request

    def test_validate_request_returns_request(self) -> None:
        """Test validate_request returns the request unchanged."""
        request = {"method": "POST", "path": "/api/test", "body": {"key": "value"}}
        result = FlextApiMiddleware.validate_request(request)
        assert result == request

    def test_apply_pipeline_modifies_request_sequentially(self) -> None:
        """Test that middleware runs sequentially and each modifies request."""
        request = {"count": 0}

        def increment_middleware_1(req: dict) -> dict:
            req["count"] += 1
            return req

        def increment_middleware_2(req: dict) -> dict:
            req["count"] += 1
            return req

        def increment_middleware_3(req: dict) -> dict:
            req["count"] += 1
            return req

        result = FlextApiMiddleware.apply_pipeline(
            request, [increment_middleware_1, increment_middleware_2, increment_middleware_3]
        )
        assert result["count"] == 3

    def test_apply_pipeline_with_complex_request(self) -> None:
        """Test apply_pipeline with complex request object."""
        request = {
            "method": "POST",
            "path": "/api/users",
            "headers": {"Content-Type": "application/json"},
            "body": {"name": "John", "email": "john@example.com"},
            "query_params": {},
        }

        def add_request_id(req: dict) -> dict:
            req["request_id"] = "12345"
            return req

        def add_timestamp(req: dict) -> dict:
            req["timestamp"] = "2025-01-22T00:00:00Z"
            return req

        result = FlextApiMiddleware.apply_pipeline(request, [add_request_id, add_timestamp])
        assert result["request_id"] == "12345"
        assert result["timestamp"] == "2025-01-22T00:00:00Z"
        assert result["body"]["name"] == "John"
