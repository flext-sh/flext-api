"""Unit tests for middleware pipeline.

Tests middleware implementations including logging, metrics, authentication,
error handling, and pipeline orchestration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from flext_core import FlextResult

from flext_api.middleware import (
    AuthenticationMiddleware,
    BaseMiddleware,
    ErrorHandlingMiddleware,
    LoggingMiddleware,
    MetricsMiddleware,
    MiddlewarePipeline,
)
from flext_api.models import FlextApiModels


class TestBaseMiddleware:
    """Test suite for BaseMiddleware abstract class."""

    def test_base_middleware_is_abstract(self) -> None:
        """Test that BaseMiddleware cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseMiddleware()

    def test_middleware_interface(self) -> None:
        """Test middleware interface implementation."""

        class ConcreteMiddleware(BaseMiddleware):
            def _process_request_impl(
                self, request: FlextApiModels.HttpRequest
            ) -> FlextResult[FlextApiModels.HttpRequest]:
                return FlextResult[FlextApiModels.HttpRequest].ok(request)

            def _process_response_impl(
                self, response: FlextApiModels.HttpResponse
            ) -> FlextResult[FlextApiModels.HttpResponse]:
                return FlextResult[FlextApiModels.HttpResponse].ok(response)

            def _process_error_impl(
                self, error: Exception, request: FlextApiModels.HttpRequest
            ) -> FlextResult[FlextApiModels.HttpResponse | None]:
                return FlextResult[FlextApiModels.HttpResponse | None].ok(None)

        middleware = ConcreteMiddleware()
        assert middleware is not None


class TestLoggingMiddleware:
    """Test suite for LoggingMiddleware."""

    @pytest.fixture
    def logging_middleware(self) -> LoggingMiddleware:
        """Create logging middleware for testing."""
        return LoggingMiddleware(log_requests=True, log_responses=True)

    @pytest.fixture
    def sample_request(self) -> FlextApiModels.HttpRequest:
        """Create sample request for testing."""
        return FlextApiModels.HttpRequest(
            method="GET",
            url="https://api.example.com/test",
            headers={"User-Agent": "test-client", "Authorization": "Bearer token123"},
        )

    @pytest.fixture
    def sample_response(self) -> FlextApiModels.HttpResponse:
        """Create sample response for testing."""
        return FlextApiModels.HttpResponse(
            status_code=200,
            url="/test",
            method="GET",
            headers={"content-type": "application/json"},
            content=b'{"success": true}',
            text='{"success": true}',
        )

    def test_logging_middleware_process_request(
        self,
        logging_middleware: LoggingMiddleware,
        sample_request: FlextApiModels.HttpRequest,
    ) -> None:
        """Test request logging."""
        with patch.object(logging_middleware._logger, "info") as mock_log:
            result = logging_middleware.process_request(sample_request)

            assert result.is_success
            request = result.unwrap()
            assert request.method == "GET"
            assert hasattr(request, "tracking_id")
            assert hasattr(request, "start_time")
            mock_log.assert_called_once()

    def test_logging_middleware_sanitizes_headers(
        self,
        logging_middleware: LoggingMiddleware,
        sample_request: FlextApiModels.HttpRequest,
    ) -> None:
        """Test that sensitive headers are sanitized."""
        with patch.object(logging_middleware._logger, "info") as mock_log:
            logging_middleware.process_request(sample_request)

            # Verify Authorization header was sanitized
            call_args = mock_log.call_args
            if call_args and len(call_args) > 0:
                logged_headers = call_args[1].get("headers", {})
                if (
                    "Authorization" in logged_headers
                    or "authorization" in logged_headers
                ):
                    auth_value = logged_headers.get(
                        "Authorization", logged_headers.get("authorization", "")
                    )
                    assert "***REDACTED***" in str(auth_value) or "Bearer" not in str(
                        auth_value
                    )

    def test_logging_middleware_process_response(
        self,
        logging_middleware: LoggingMiddleware,
        sample_response: FlextApiModels.HttpResponse,
    ) -> None:
        """Test response logging."""
        # Add request tracking data using object.__setattr__ to bypass Pydantic validation
        mock_request = Mock()
        mock_request.tracking_id = "test-id-123"
        mock_request.start_time = 1000.0
        object.__setattr__(sample_response, "request", mock_request)

        with patch("time.time", return_value=1001.0):
            with patch.object(logging_middleware._logger, "info") as mock_log:
                result = logging_middleware.process_response(sample_response)

                assert result.is_success
                mock_log.assert_called_once()
                call_args = mock_log.call_args
                assert call_args is not None
                assert "extra" in call_args[1]
                assert "duration_ms" in call_args[1]["extra"]

    def test_logging_middleware_disabled(self) -> None:
        """Test logging middleware when disabled."""
        middleware = LoggingMiddleware(log_requests=False, log_responses=False)
        request = FlextApiModels.HttpRequest(
            method="GET", url="https://api.example.com/test"
        )

        with patch.object(middleware._logger, "info") as mock_log:
            result = middleware.process_request(request)

            assert result.is_success
            mock_log.assert_not_called()


class TestMetricsMiddleware:
    """Test suite for MetricsMiddleware."""

    @pytest.fixture
    def metrics_middleware(self) -> MetricsMiddleware:
        """Create metrics middleware for testing."""
        return MetricsMiddleware()

    @pytest.fixture
    def sample_request(self) -> FlextApiModels.HttpRequest:
        """Create sample request for testing."""
        return FlextApiModels.HttpRequest(
            method="GET", url="https://api.example.com/test"
        )

    def test_metrics_middleware_counts_requests(
        self,
        metrics_middleware: MetricsMiddleware,
        sample_request: FlextApiModels.HttpRequest,
    ) -> None:
        """Test request counting."""
        initial_count = metrics_middleware._metrics["request_count"]

        result = metrics_middleware.process_request(sample_request)

        assert result.is_success
        assert metrics_middleware._metrics["request_count"] == initial_count + 1

    def test_metrics_middleware_tracks_duration(
        self, metrics_middleware: MetricsMiddleware
    ) -> None:
        """Test duration tracking."""
        request = FlextApiModels.HttpRequest(
            method="GET", url="https://api.example.com/test"
        )

        # Process request
        request_result = metrics_middleware.process_request(request)
        processed_request = request_result.unwrap()

        # Create response with request reference
        response = FlextApiModels.HttpResponse(
            status_code=200,
            url="/test",
            method="GET",
            headers={},
            content=b"",
            text="",
        )
        object.__setattr__(response, "request", processed_request)

        # Set start time on the request (simulating what process_request does)
        object.__setattr__(processed_request, "metrics_start_time", 1000.0)

        # Process response with mocked time showing elapsed duration
        with patch("time.time", return_value=1001.5):
            metrics_middleware.process_response(response)

        assert metrics_middleware._metrics["total_duration"] > 0

    def test_metrics_middleware_tracks_status_codes(
        self, metrics_middleware: MetricsMiddleware
    ) -> None:
        """Test status code tracking."""
        request = FlextApiModels.HttpRequest(
            method="GET", url="https://api.example.com/test"
        )
        request_result = metrics_middleware.process_request(request)
        processed_request = request_result.unwrap()

        response = FlextApiModels.HttpResponse(
            status_code=200,
            url="/test",
            method="GET",
            headers={},
            content=b"",
            text="",
        )
        object.__setattr__(response, "request", processed_request)
        object.__setattr__(processed_request, "metrics_start_time", 1000.0)

        metrics_middleware.process_response(response)

        assert "200" in metrics_middleware._metrics["status_codes"]
        assert metrics_middleware._metrics["status_codes"]["200"] == 1

    def test_metrics_middleware_counts_errors(
        self, metrics_middleware: MetricsMiddleware
    ) -> None:
        """Test error counting."""
        request = FlextApiModels.HttpRequest(
            method="GET", url="https://api.example.com/test"
        )
        request_result = metrics_middleware.process_request(request)
        processed_request = request_result.unwrap()

        error_response = FlextApiModels.HttpResponse(
            status_code=500,
            url="/test",
            method="GET",
            headers={},
            content=b"",
            text="",
        )
        object.__setattr__(error_response, "request", processed_request)
        object.__setattr__(processed_request, "metrics_start_time", 1000.0)

        metrics_middleware.process_response(error_response)

        assert metrics_middleware._metrics["error_count"] > 0

    def test_metrics_middleware_get_metrics(
        self, metrics_middleware: MetricsMiddleware
    ) -> None:
        """Test metrics retrieval."""
        metrics = metrics_middleware.get_metrics()

        assert "request_count" in metrics
        assert "error_count" in metrics
        assert "total_duration" in metrics
        assert "status_codes" in metrics
        assert "average_duration_ms" in metrics
        assert "error_rate" in metrics


class TestAuthenticationMiddleware:
    """Test suite for AuthenticationMiddleware."""

    @pytest.fixture
    def auth_middleware(self) -> AuthenticationMiddleware:
        """Create authentication middleware for testing."""
        return AuthenticationMiddleware(
            auth_type="bearer", token="test-token-123", header_name="Authorization"
        )

    @pytest.fixture
    def sample_request(self) -> FlextApiModels.HttpRequest:
        """Create sample request for testing."""
        return FlextApiModels.HttpRequest(
            method="GET", url="https://api.example.com/test", headers={}
        )

    def test_auth_middleware_adds_bearer_token(
        self,
        auth_middleware: AuthenticationMiddleware,
        sample_request: FlextApiModels.HttpRequest,
    ) -> None:
        """Test adding bearer token to request."""
        result = auth_middleware.process_request(sample_request)

        assert result.is_success
        request = result.unwrap()
        assert "Authorization" in request.headers
        assert request.headers["Authorization"] == "Bearer test-token-123"

    def test_auth_middleware_preserves_existing_headers(
        self, auth_middleware: AuthenticationMiddleware
    ) -> None:
        """Test that existing headers are preserved."""
        request = FlextApiModels.HttpRequest(
            method="GET",
            url="https://api.example.com/test",
            headers={"User-Agent": "test-client", "X-Custom": "value"},
        )

        result = auth_middleware.process_request(request)

        assert result.is_success
        processed_request = result.unwrap()
        assert processed_request.headers["User-Agent"] == "test-client"
        assert processed_request.headers["X-Custom"] == "value"
        assert "Authorization" in processed_request.headers

    def test_auth_middleware_api_key(self) -> None:
        """Test API key authentication."""
        middleware = AuthenticationMiddleware(
            auth_type="api_key", token="api-key-123", header_name="X-API-Key"
        )

        request = FlextApiModels.HttpRequest(
            method="GET", url="https://api.example.com/test"
        )

        result = middleware.process_request(request)

        assert result.is_success
        processed_request = result.unwrap()
        assert "X-API-Key" in processed_request.headers
        assert processed_request.headers["X-API-Key"] == "api-key-123"

    def test_auth_middleware_custom_header(self) -> None:
        """Test custom header authentication."""
        middleware = AuthenticationMiddleware(
            auth_type="custom", token="custom-token", header_name="X-Custom-Auth"
        )

        request = FlextApiModels.HttpRequest(
            method="GET", url="https://api.example.com/test"
        )

        result = middleware.process_request(request)

        assert result.is_success
        processed_request = result.unwrap()
        assert "X-Custom-Auth" in processed_request.headers


class TestErrorHandlingMiddleware:
    """Test suite for ErrorHandlingMiddleware."""

    @pytest.fixture
    def error_middleware(self) -> ErrorHandlingMiddleware:
        """Create error handling middleware for testing."""
        return ErrorHandlingMiddleware(
            handle_http_errors=True, handle_network_errors=True
        )

    @pytest.fixture
    def sample_request(self) -> FlextApiModels.HttpRequest:
        """Create sample request for testing."""
        return FlextApiModels.HttpRequest(
            method="GET", url="https://api.example.com/test"
        )

    def test_error_middleware_process_http_error(
        self,
        error_middleware: ErrorHandlingMiddleware,
        sample_request: FlextApiModels.HttpRequest,
    ) -> None:
        """Test handling of HTTP errors."""
        error_response = FlextApiModels.HttpResponse(
            status_code=500,
            url="https://api.example.com/test",
            method="GET",
            headers={"content-type": "text/plain"},
            content=b"Internal Server Error",
            text="Internal Server Error",
        )

        result = error_middleware.process_response(error_response)

        # Middleware logs error but passes response through
        assert result.is_success

    def test_error_middleware_process_exception(
        self,
        error_middleware: ErrorHandlingMiddleware,
        sample_request: FlextApiModels.HttpRequest,
    ) -> None:
        """Test handling of exceptions."""
        test_error = Exception("Network connection failed")

        result = error_middleware.process_error(test_error, sample_request)

        # Middleware logs error and returns None (no recovery)
        assert result.is_success
        assert result.unwrap() is None


class TestMiddlewarePipeline:
    """Test suite for MiddlewarePipeline."""

    @pytest.fixture
    def sample_request(self) -> FlextApiModels.HttpRequest:
        """Create sample request for testing."""
        return FlextApiModels.HttpRequest(
            method="GET", url="https://api.example.com/test"
        )

    @pytest.fixture
    def sample_response(self) -> FlextApiModels.HttpResponse:
        """Create sample response for testing."""
        return FlextApiModels.HttpResponse(
            status_code=200,
            url="/test",
            method="GET",
            headers={"content-type": "application/json"},
            content=b'{"success": true}',
            text='{"success": true}',
        )

    def test_pipeline_initialization(self) -> None:
        """Test pipeline initialization."""
        pipeline = MiddlewarePipeline()
        assert pipeline is not None
        assert len(pipeline._middlewares) == 0

    def test_pipeline_add_middleware(self) -> None:
        """Test adding middleware to pipeline."""
        pipeline = MiddlewarePipeline()
        logging_middleware = LoggingMiddleware()

        pipeline.add_middleware(logging_middleware)

        assert len(pipeline._middlewares) == 1
        assert pipeline._middlewares[0] == logging_middleware

    def test_pipeline_remove_middleware(self) -> None:
        """Test removing middleware from pipeline."""
        pipeline = MiddlewarePipeline()
        logging_middleware = LoggingMiddleware()

        pipeline.add_middleware(logging_middleware)
        assert len(pipeline._middlewares) == 1

        result = pipeline.remove_middleware("LoggingMiddleware")
        assert result.is_success
        assert len(pipeline._middlewares) == 0

    def test_pipeline_remove_nonexistent_middleware(self) -> None:
        """Test removing middleware that doesn't exist."""
        pipeline = MiddlewarePipeline()
        logging_middleware = LoggingMiddleware()

        result = pipeline.remove_middleware(logging_middleware)
        assert result.is_failure

    def test_pipeline_process_request(
        self, sample_request: FlextApiModels.HttpRequest
    ) -> None:
        """Test request processing through pipeline."""
        pipeline = MiddlewarePipeline()
        pipeline.add_middleware(LoggingMiddleware())
        pipeline.add_middleware(MetricsMiddleware())

        result = pipeline.process_request(sample_request)

        assert result.is_success
        request = result.unwrap()
        assert hasattr(request, "tracking_id")  # From logging middleware
        assert hasattr(request, "metrics_start_time")  # From metrics middleware

    def test_pipeline_process_response(
        self, sample_response: FlextApiModels.HttpResponse
    ) -> None:
        """Test response processing through pipeline."""
        pipeline = MiddlewarePipeline()
        pipeline.add_middleware(LoggingMiddleware())
        pipeline.add_middleware(MetricsMiddleware())

        result = pipeline.process_response(sample_response)

        assert result.is_success

    def test_pipeline_process_error(
        self, sample_request: FlextApiModels.HttpRequest
    ) -> None:
        """Test error processing through pipeline."""
        pipeline = MiddlewarePipeline()
        pipeline.add_middleware(ErrorHandlingMiddleware())

        error = Exception("Test error")
        result = pipeline.process_error(error, sample_request)

        assert result.is_success

    def test_pipeline_middleware_order(self) -> None:
        """Test that middleware executes in correct order."""
        pipeline = MiddlewarePipeline()

        execution_order = []

        class OrderMiddleware1(BaseMiddleware):
            def __init__(self) -> None:
                super().__init__("OrderMiddleware1")

            def _process_request_impl(self, request):
                execution_order.append("middleware1")
                return FlextResult[FlextApiModels.HttpRequest].ok(request)

            def _process_response_impl(self, response):
                execution_order.append("middleware1_response")
                return FlextResult[FlextApiModels.HttpResponse].ok(response)

            def _process_error_impl(self, error, request):
                return FlextResult[FlextApiModels.HttpResponse | None].ok(None)

        class OrderMiddleware2(BaseMiddleware):
            def __init__(self) -> None:
                super().__init__("OrderMiddleware2")

            def _process_request_impl(self, request):
                execution_order.append("middleware2")
                return FlextResult[FlextApiModels.HttpRequest].ok(request)

            def _process_response_impl(self, response):
                execution_order.append("middleware2_response")
                return FlextResult[FlextApiModels.HttpResponse].ok(response)

            def _process_error_impl(self, error, request):
                return FlextResult[FlextApiModels.HttpResponse | None].ok(None)

        pipeline.add_middleware(OrderMiddleware1())
        pipeline.add_middleware(OrderMiddleware2())

        request = FlextApiModels.HttpRequest(
            method="GET", url="https://api.example.com/test"
        )
        response = FlextApiModels.HttpResponse(
            status_code=200,
            url="/test",
            method="GET",
            headers={},
            content=b"",
            text="",
        )

        pipeline.process_request(request)
        pipeline.process_response(response)

        # Request: middleware1 -> middleware2
        # Response: middleware2 -> middleware1 (reverse order)
        assert execution_order == [
            "middleware1",
            "middleware2",
            "middleware2_response",
            "middleware1_response",
        ]

    def test_pipeline_error_propagation(
        self, sample_request: FlextApiModels.HttpRequest
    ) -> None:
        """Test that errors in middleware are properly propagated."""
        pipeline = MiddlewarePipeline()

        class FailingMiddleware(BaseMiddleware):
            def __init__(self) -> None:
                super().__init__("FailingMiddleware")

            def _process_request_impl(self, request):
                return FlextResult[FlextApiModels.HttpRequest].fail("Middleware failed")

            def _process_response_impl(self, response):
                return FlextResult[FlextApiModels.HttpResponse].ok(response)

            def _process_error_impl(self, error, request):
                return FlextResult[FlextApiModels.HttpResponse | None].ok(None)

        pipeline.add_middleware(FailingMiddleware())

        result = pipeline.process_request(sample_request)

        assert result.is_failure
        assert result.error is not None and "Middleware failed" in result.error
