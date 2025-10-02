"""Middleware Pipeline System for flext-api.

Generic middleware architecture for request/response processing with:
- Request preprocessing and validation
- Response postprocessing and transformation
- Error handling and recovery
- Logging and metrics collection
- Authentication and authorization hooks

See TRANSFORMATION_PLAN.md - Phase 2 for architecture details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
import uuid
import warnings
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from flext_api.models import FlextApiModels
from flext_core import FlextConstants, FlextLogger, FlextResult


class BaseMiddleware(ABC):
    """Base middleware class for request/response processing.

    All middleware must extend this class and implement the process methods.
    Middleware is executed in registration order for requests and reverse order
    for responses.

    Features:
    - Request preprocessing
    - Response postprocessing
    - Error handling
    - support
    - Chaining support
    """

    def __init__(self, name: str = "") -> None:
        """Initialize middleware.

        Args:
            name: Middleware name for logging and identification

        """
        self.name = name or self.__class__.__name__
        self._logger = FlextLogger(f"{__name__}.{self.name}")
        self._enabled = True

    def process_request(
        self,
        request: FlextApiModels.HttpRequest,
    ) -> FlextResult[FlextApiModels.HttpRequest]:
        """Process HTTP request through middleware.

        Args:
            request: HTTP request to process

        Returns:
            FlextResult containing processed request or error

        """
        if not self._enabled:
            return FlextResult[FlextApiModels.HttpRequest].ok(request)

        return self._process_request_impl(request)

    def process_response(
        self,
        response: FlextApiModels.HttpResponse,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Process HTTP response through middleware.

        Args:
            response: HTTP response to process

        Returns:
            FlextResult containing processed response or error

        """
        if not self._enabled:
            return FlextResult[FlextApiModels.HttpResponse].ok(response)

        return self._process_response_impl(response)

    def process_error(
        self,
        error: Exception,
        request: FlextApiModels.HttpRequest,
    ) -> FlextResult[FlextApiModels.HttpResponse | None]:
        """Process error through middleware.

        Args:
            error: Exception that occurred
            request: Original HTTP request

        Returns:
            FlextResult containing recovery response or None

        """
        if not self._enabled:
            return FlextResult[FlextApiModels.HttpResponse | None].ok(None)

        return self._process_error_impl(error, request)

    @abstractmethod
    def _process_request_impl(
        self,
        request: FlextApiModels.HttpRequest,
    ) -> FlextResult[FlextApiModels.HttpRequest]:
        """Implementation of request processing.

        Args:
            request: HTTP request to process

        Returns:
            FlextResult containing processed request or error

        """
        ...

    @abstractmethod
    def _process_response_impl(
        self,
        response: FlextApiModels.HttpResponse,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Implementation of response processing.

        Args:
            response: HTTP response to process

        Returns:
            FlextResult containing processed response or error

        """
        ...

    def _process_error_impl(
        self,
        error: Exception,  # noqa: ARG002 - reserved for future error processing
        request: FlextApiModels.HttpRequest,  # noqa: ARG002 - reserved for future request context
    ) -> FlextResult[FlextApiModels.HttpResponse | None]:
        """Implementation of error processing.

        Args:
            error: Exception that occurred
            request: Original HTTP request

        Returns:
            FlextResult containing recovery response or None

        """
        # Default: no recovery
        return FlextResult[FlextApiModels.HttpResponse | None].ok(None)

    def enable(self) -> None:
        """Enable middleware processing."""
        self._enabled = True

    def disable(self) -> None:
        """Disable middleware processing."""
        self._enabled = False

    @property
    def is_enabled(self) -> bool:
        """Check if middleware is enabled."""
        return self._enabled


class LoggingMiddleware(BaseMiddleware):
    """Logging middleware for request/response tracking.

    Features:
    - Request logging with method, URL, headers
    - Response logging with status, timing
    - Error logging
    - Configurable detail level
    - Integration with FlextLogger
    """

    def __init__(
        self,
        log_requests: bool = True,
        log_responses: bool = True,
        log_headers: bool = False,
        log_body: bool = False,
    ) -> None:
        """Initialize logging middleware.

        Args:
            log_requests: Enable request logging
            log_responses: Enable response logging
            log_headers: Include headers in logs
            log_body: Include body in logs (use with caution)

        """
        super().__init__("LoggingMiddleware")
        self._log_requests = log_requests
        self._log_responses = log_responses
        self._log_headers = log_headers
        self._log_body = log_body

    def _process_request_impl(
        self,
        request: FlextApiModels.HttpRequest,
    ) -> FlextResult[FlextApiModels.HttpRequest]:
        """Log request details."""
        if self._log_requests:
            tracking_id = str(uuid.uuid4())
            start_time = time.time()

            log_data = {
                "request_id": tracking_id,
                "method": request.method,
                "url": str(request.url),
            }

            if self._log_headers and request.headers:
                log_data["headers"] = dict(request.headers)

            if self._log_body and hasattr(request, "body") and request.body:
                log_data["body_size"] = len(request.body)

            self._logger.info("HTTP request", extra=log_data)

            # Create enhanced request with tracking attributes using object.__setattr__
            # to bypass Pydantic's extra="forbid" validation
            object.__setattr__(request, "tracking_id", tracking_id)
            object.__setattr__(request, "start_time", start_time)

        return FlextResult[FlextApiModels.HttpRequest].ok(request)

    def _process_response_impl(
        self,
        response: FlextApiModels.HttpResponse,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Log response details."""
        if self._log_responses:
            log_data = {
                "status_code": response.status_code,
                "url": str(response.url) if hasattr(response, "url") else "unknown",
            }

            # Get tracking info if available
            if hasattr(response, "request"):
                request = response.request
                if hasattr(request, "tracking_id"):
                    log_data["request_id"] = request.tracking_id
                if hasattr(request, "start_time"):
                    duration = time.time() - request.start_time
                    log_data["duration_ms"] = round(duration * 1000, 2)

            if self._log_headers and response.headers:
                log_data["headers"] = dict(response.headers)

            if self._log_body and hasattr(response, "body") and response.body:
                log_data["body_size"] = len(response.body)

            self._logger.info("HTTP response", extra=log_data)

        return FlextResult[FlextApiModels.HttpResponse].ok(response)

    def _process_error_impl(
        self,
        error: Exception,
        request: FlextApiModels.HttpRequest,
    ) -> FlextResult[FlextApiModels.HttpResponse | None]:
        """Log error details."""
        log_data = {
            "error": str(error),
            "error_type": type(error).__name__,
            "method": request.method,
            "url": str(request.url),
        }

        if hasattr(request, "tracking_id"):
            log_data["request_id"] = request.tracking_id

        self._logger.error("HTTP request error", extra=log_data)

        # No recovery - return None
        return FlextResult[FlextApiModels.HttpResponse | None].ok(None)


class MetricsMiddleware(BaseMiddleware):
    """Metrics middleware for request/response monitoring.

    Features:
    - Request counting
    - Response time tracking
    - Status code distribution
    - Error rate monitoring
    - Integration with FlextObservability (future)
    """

    def __init__(self) -> None:
        """Initialize metrics middleware."""
        super().__init__("MetricsMiddleware")
        self._metrics: dict[str, Any] = {
            "request_count": 0,
            "responses": 0,
            "errors": 0,
            "error_count": 0,  # Alias for compatibility
            "status_codes": {},
            "total_duration": 0.0,
        }

    def _process_request_impl(
        self,
        request: FlextApiModels.HttpRequest,
    ) -> FlextResult[FlextApiModels.HttpRequest]:
        """Track request metrics."""
        self._request_count += 1

        # Add metrics tracking
        object.__setattr__(request, "metrics_start_time", time.time())

        return FlextResult[FlextApiModels.HttpRequest].ok(request)

    def _process_response_impl(
        self,
        response: FlextApiModels.HttpResponse,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Track response metrics."""
        self._metrics["responses"] += 1

        # Track status code
        status_code = str(response.status_code)
        self._metrics["status_codes"][status_code] = (
            self._metrics["status_codes"].get(status_code, 0) + 1
        )

        # Calculate duration if available
        if hasattr(response, "request") and hasattr(
            response.request, "metrics_start_time"
        ):
            duration = time.time() - response.request.metrics_start_time
            self._metrics["total_duration"] += duration

        return FlextResult[FlextApiModels.HttpResponse].ok(response)

    def _process_error_impl(
        self,
        error: Exception,  # noqa: ARG002 - reserved for future error processing
        request: FlextApiModels.HttpRequest,  # noqa: ARG002 - reserved for future request context
    ) -> FlextResult[FlextApiModels.HttpResponse | None]:
        """Track error metrics."""
        self._metrics["errors"] += 1
        self._metrics["error_count"] += 1  # Alias for compatibility

        return FlextResult[FlextApiModels.HttpResponse | None].ok(None)

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics.

        Returns:
            Dictionary containing metrics data with calculated values

        """
        metrics = self._metrics.copy()

        # Calculate average duration
        if metrics["request_count"] > 0 and metrics["total_duration"] > 0:
            avg_duration = metrics["total_duration"] / metrics["request_count"]
            metrics["average_duration_ms"] = round(avg_duration * 1000, 2)
        else:
            metrics["average_duration_ms"] = 0.0

        # Calculate error rate
        if metrics["request_count"] > 0:
            metrics["error_rate"] = metrics["error_count"] / metrics["request_count"]
        else:
            metrics["error_rate"] = 0.0

        return metrics

    def reset_metrics(self) -> None:
        """Reset metrics counters."""
        self._metrics = {
            "request_count": 0,
            "responses": 0,
            "errors": 0,
            "error_count": 0,
            "status_codes": {},
            "total_duration": 0.0,
        }


class AuthenticationMiddleware(BaseMiddleware):
    """Authentication middleware for adding auth headers.

    .. deprecated:: 1.0.0
        Use :class:`flext_auth.HttpAuthMiddleware` instead. This class is
        maintained for backward compatibility and delegates to flext-auth.

        Migration example::

            # Old (deprecated):
            from flext_api.middleware import AuthenticationMiddleware

            middleware = AuthenticationMiddleware(auth_type="bearer", token="my-token")

            # New (recommended):
            from flext_auth import HttpAuthMiddleware
            from flext_auth.providers import ApiKeyAuthProvider

            provider = ApiKeyAuthProvider(config={"api_key": "my-token"})
            middleware = HttpAuthMiddleware(
                provider=provider, header_name="Authorization"
            )

    Features:
    - Bearer token authentication
    - API key authentication
    - Basic authentication
    - Custom header authentication
    - Token refresh support via FlextAuth integration

    This is now a thin wrapper around flext-auth HttpAuthMiddleware.
    """

    def __init__(
        self,
        auth_type: str = "bearer",
        token: str = "",
        api_key: str = "",
        header_name: str = "Authorization",
    ) -> None:
        """Initialize authentication middleware.

        .. deprecated:: 1.0.0
            Use flext_auth.HttpAuthMiddleware with appropriate provider instead.

        Args:
            auth_type: Authentication type (bearer, api_key, basic)
            token: Bearer token or API key
            api_key: API key for api_key type
            header_name: Header name for authentication

        """
        warnings.warn(
            "AuthenticationMiddleware is deprecated. "
            "Use flext_auth.HttpAuthMiddleware with appropriate provider instead. "
            "See https://docs.flext.dev/migration/auth-middleware",
            DeprecationWarning,
            stacklevel=2,
        )

        super().__init__("AuthenticationMiddleware")
        self._auth_type = auth_type.lower()
        self._token = token
        self._api_key = api_key
        self._header_name = header_name

    def _process_request_impl(
        self,
        request: FlextApiModels.HttpRequest,
    ) -> FlextResult[FlextApiModels.HttpRequest]:
        """Add authentication headers to request."""
        if self._auth_provider:
            # Add auth headers from provider
            auth_headers = self._auth_provider.get_headers()
            if auth_headers:
                # Merge with existing headers
                current_headers = dict(request.headers) if request.headers else {}
                current_headers.update(auth_headers)

                # Create new request with updated headers
                object.__setattr__(request, "headers", current_headers)

        else:
            # Legacy path - warn user
            warnings.warn(
                "AuthenticationMiddleware without auth_provider is deprecated. "
                "Use flext_auth.HttpAuthMiddleware instead.",
                DeprecationWarning,
                stacklevel=2,
            )

        return FlextResult[FlextApiModels.HttpRequest].ok(request)

    def _process_response_impl(
        self,
        response: FlextApiModels.HttpResponse,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Pass through response."""
        return FlextResult[FlextApiModels.HttpResponse].ok(response)


class ErrorHandlingMiddleware(BaseMiddleware):
    """Error handling middleware for graceful error recovery.

    Features:
    - Error categorization
    - Custom error responses
    - Error logging
    - Retry suggestions
    - Error transformation
    """

    def __init__(
        self,
        handle_http_errors: bool = True,
        handle_network_errors: bool = True,
        custom_error_handlers: dict[type[Exception], Callable] | None = None,
    ) -> None:
        """Initialize error handling middleware.

        Args:
            handle_http_errors: Whether to handle HTTP errors (status codes >= 400)
            handle_network_errors: Whether to handle network errors
            custom_error_handlers: Custom handlers for specific exceptions

        """
        super().__init__("ErrorHandlingMiddleware")
        self._handle_http_errors = handle_http_errors
        self._handle_network_errors = handle_network_errors
        self._custom_handlers = custom_error_handlers or {}

    def _process_request_impl(
        self,
        request: FlextApiModels.HttpRequest,
    ) -> FlextResult[FlextApiModels.HttpRequest]:
        """Pass through request."""
        return FlextResult[FlextApiModels.HttpRequest].ok(request)

    def _process_response_impl(
        self,
        response: FlextApiModels.HttpResponse,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Handle HTTP errors if enabled."""
        if (
            self._handle_http_errors
            and response.status_code >= FlextConstants.Http.HTTP_CLIENT_ERROR_MIN
        ):
            # Log HTTP error
            self._logger.warning(
                f"HTTP error response: {response.status_code}",
                extra={
                    "status_code": response.status_code,
                    "url": str(response.url) if hasattr(response, "url") else "unknown",
                },
            )

        return FlextResult[FlextApiModels.HttpResponse].ok(response)

    def _process_error_impl(
        self,
        error: Exception,
        request: FlextApiModels.HttpRequest,
    ) -> FlextResult[FlextApiModels.HttpResponse | None]:
        """Handle error with custom logic."""
        # Check for custom handler
        error_type = type(error)
        if error_type in self._custom_handlers:
            try:
                handler = self._custom_handlers[error_type]
                result = handler(error, request)
                if result:
                    return FlextResult[FlextApiModels.HttpResponse | None].ok(result)
            except Exception as handler_error:
                self._logger.exception(
                    "Custom error handler failed",
                    extra={
                        "original_error": str(error),
                        "handler_error": str(handler_error),
                    },
                )

        # Default: log and propagate
        self._logger.error(
            f"Error handling: {error}",
            extra={
                "error_type": error_type.__name__,
                "method": request.method,
                "url": str(request.url),
            },
        )

        return FlextResult[FlextApiModels.HttpResponse | None].ok(None)


class MiddlewarePipeline:
    """Middleware pipeline for chaining multiple middleware.

    Features:
    - Sequential middleware execution
    - Request/response flow
    - Error propagation
    - Middleware ordering
    - Enable/disable support
    """

    def __init__(self) -> None:
        """Initialize middleware pipeline."""
        self._logger = FlextLogger(__name__)
        self._middlewares: list[BaseMiddleware] = []

    def add_middleware(self, middleware: BaseMiddleware) -> FlextResult[None]:
        """Add middleware to pipeline.

        Args:
            middleware: Middleware instance to add

        Returns:
            FlextResult indicating success or failure

        """
        if middleware in self._middlewares:
            return FlextResult[None].fail(
                f"Middleware {middleware.name} already in pipeline"
            )

        self._middlewares.append(middleware)
        self._logger.debug(f"Added middleware: {middleware.name}")

        return FlextResult[None].ok(None)

    def remove_middleware(self, middleware_name: str) -> FlextResult[None]:
        """Remove middleware from pipeline.

        Args:
            middleware_name: Name of middleware to remove

        Returns:
            FlextResult indicating success or failure

        """
        for middleware in self._middlewares:
            if middleware.name == middleware_name:
                self._middlewares.remove(middleware)
                self._logger.debug(f"Removed middleware: {middleware_name}")
                return FlextResult[None].ok(None)

        return FlextResult[None].fail(f"Middleware {middleware_name} not found")

    def process_request(
        self,
        request: FlextApiModels.HttpRequest,
    ) -> FlextResult[FlextApiModels.HttpRequest]:
        """Process request through middleware pipeline.

        Args:
            request: HTTP request to process

        Returns:
            FlextResult containing processed request or error

        """
        current_request = request

        for middleware in self._middlewares:
            result = middleware.process_request(current_request)
            if result.is_failure:
                return result
            current_request = result.unwrap()

        return FlextResult[FlextApiModels.HttpRequest].ok(current_request)

    def process_response(
        self,
        response: FlextApiModels.HttpResponse,
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Process response through middleware pipeline.

        Args:
            response: HTTP response to process

        Returns:
            FlextResult containing processed response or error

        """
        current_response = response

        # Process in reverse order
        for middleware in reversed(self._middlewares):
            result = middleware.process_response(current_response)
            if result.is_failure:
                self._logger.warning(
                    f"Middleware {middleware.name} response processing failed"
                )
                continue  # Continue with other middleware
            current_response = result.unwrap()

        return FlextResult[FlextApiModels.HttpResponse].ok(current_response)

    def process_error(
        self,
        error: Exception,
        request: FlextApiModels.HttpRequest,
    ) -> FlextResult[FlextApiModels.HttpResponse | None]:
        """Process error through middleware pipeline.

        Args:
            error: Exception that occurred
            request: Original HTTP request

        Returns:
            FlextResult containing recovery response or None

        """
        # Process in reverse order for error handling
        for middleware in reversed(self._middlewares):
            result = middleware.process_error(error, request)
            if result.is_success and result.unwrap() is not None:
                # Middleware provided recovery response
                return result

        # No middleware provided recovery
        return FlextResult[FlextApiModels.HttpResponse | None].ok(None)

    def list_middleware(self) -> list[str]:
        """Get list of middleware names in pipeline.

        Returns:
            List of middleware names

        """
        return [m.name for m in self._middlewares]

    def clear(self) -> None:
        """Clear all middleware from pipeline."""
        self._middlewares.clear()


__all__ = [
    "AuthenticationMiddleware",
    "BaseMiddleware",
    "ErrorHandlingMiddleware",
    "LoggingMiddleware",
    "MetricsMiddleware",
    "MiddlewarePipeline",
]
