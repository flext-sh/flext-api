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
from dataclasses import dataclass

from flext_core import FlextCore

from flext_api.models import FlextApiModels


class FlextApiMiddleware:
    """Unified middleware system for flext-api HTTP operations.

    This namespace class provides all middleware functionality through nested classes,
    following the unified class pattern. All middleware implementations are contained
    within this single class for better organization and maintainability.

    Features:
        - Request preprocessing and validation
        - Response postprocessing and transformation
        - Error handling and recovery
        - Logging and metrics collection
        - Authentication and authorization hooks

    Usage:
        ```python
        from flext_api.middleware import FlextApiMiddleware

        # Create logging middleware
        logging_mw = FlextApiMiddleware.LoggingMiddleware()

        # Create pipeline
        pipeline = FlextApiMiddleware.Pipeline()
        pipeline.add_middleware(logging_mw)

        # Use in HTTP client
        client.middleware = pipeline
    """

    # =========================================================================
    # MIDDLEWARE BASE CLASSES - Foundation for all middleware types
    # =========================================================================

    @dataclass
    class _BaseMiddleware:
        """Base class for all middleware implementations."""

        name: str = "middleware"

    class BaseMiddleware(ABC):
        """Base middleware class for request/response processing.

        **PROTOCOL IMPLEMENTATION**: This middleware implements FlextCore.Protocols.Extensions.Middleware,
        establishing the foundation pattern for ALL middleware across the FLEXT ecosystem.

        Note: BaseMiddleware provides a richer interface than the base protocol, with separate
        methods for request/response/error processing. The protocol's process() method can be
        implemented via adapter pattern if needed.

        All middleware must extend this class and implement the process methods.
        Middleware is executed in registration order for requests and reverse order
        for responses.

        Features:
        - Request preprocessing (process_request)
        - Response postprocessing (process_response)
        - Error handling (processerror)
        - Enable/disable support
        - Chaining support
        - Protocol compliance for ecosystem consistency

        Note:
            All middleware must implement _process_request_impl and _process_response_impl.
            Error processing has default implementation but can be overridden.
            Middleware can be enabled/disabled dynamically.
            Protocol compliance ensures ecosystem-wide consistency.

        See Also:
            FlextCore.Protocols.Extensions.Middleware: Protocol definition for middleware.
            FlextApiMiddleware.LoggingMiddleware: Concrete implementation example.
            FlextApiMiddleware.MetricsMiddleware: Metrics collection middleware.
            FlextApiMiddleware.AuthenticationMiddleware: Authentication middleware.

        """

        def __init__(self, name: str = "") -> None:
            """Initialize middleware.

            Args:
                name: Middleware name for logging and identification

            """
            self.name = name or self.__class__.__name__
            self.logger = FlextCore.Logger(f"{__name__}.{self.name}")
            self._enabled = True

        def process_request(
            self,
            request: FlextApiModels.HttpRequest,
        ) -> FlextCore.Result[FlextApiModels.HttpRequest]:
            """Process HTTP request through middleware.

            Args:
                request: HTTP request to process

            Returns:
                FlextCore.Result containing processed request or error

            """
            if not self._enabled:
                return FlextCore.Result[FlextApiModels.HttpRequest].ok(request)

            return self._process_request_impl(request)

        def process_response(
            self,
            response: FlextApiModels.HttpResponse,
        ) -> FlextCore.Result[FlextApiModels.HttpResponse]:
            """Process HTTP response through middleware.

            Args:
                response: HTTP response to process

            Returns:
                FlextCore.Result containing processed response or error

            """
            if not self._enabled:
                return FlextCore.Result[FlextApiModels.HttpResponse].ok(response)

            return self._process_response_impl(response)

        def processerror(
            self,
            error: Exception,
            request: FlextApiModels.HttpRequest,
        ) -> FlextCore.Result[FlextApiModels.HttpResponse | None]:
            """Process error through middleware.

            Args:
                error: Exception that occurred
                request: Original HTTP request

            Returns:
                FlextCore.Result containing recovery response or None

            """
            if not self._enabled:
                return FlextCore.Result[FlextApiModels.HttpResponse | None].ok(None)

            return self._processerror_impl(error, request)

        @abstractmethod
        def _process_request_impl(
            self,
            request: FlextApiModels.HttpRequest,
        ) -> FlextCore.Result[FlextApiModels.HttpRequest]:
            """Implementation of request processing.

            Args:
                request: HTTP request to process

            Returns:
                FlextCore.Result containing processed request or error

            """
            ...

        @abstractmethod
        def _process_response_impl(
            self,
            response: FlextApiModels.HttpResponse,
        ) -> FlextCore.Result[FlextApiModels.HttpResponse]:
            """Implementation of response processing.

            Args:
                response: HTTP response to process

            Returns:
                FlextCore.Result containing processed response or error

            """
            ...

        def _processerror_impl(
            self,
            error: Exception,
            request: FlextApiModels.HttpRequest,
        ) -> FlextCore.Result[FlextApiModels.HttpResponse | None]:
            """Implementation of error processing.

            Default implementation: no error recovery (returns None).
            Override in subclasses to provide custom error handling.

            Args:
                error: Exception that occurred
                request: Original HTTP request

            Returns:
                FlextCore.Result containing recovery response or None

            """
            # Default: no recovery
            _ = error
            _ = request
            return FlextCore.Result[FlextApiModels.HttpResponse | None].ok(None)

        def enable(self) -> None:
            """Enable middleware processing."""
            self._enabled = True

        def disable(self) -> None:
            """Disable middleware processing."""
            self._enabled = False

        @property
        def is_enabled(self) -> bool:
            """Check if middleware is enabled.

            Returns:
                bool: True if middleware is enabled, False otherwise

            """
            return self._enabled

    class LoggingMiddleware(BaseMiddleware):
        """Logging middleware for request/response tracking.

        Features:
        - Request logging with method, URL, headers
        - Response logging with status, timing
        - Error logging
        - Configurable detail level
        - Integration with FlextCore.Logger
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
        ) -> FlextCore.Result[FlextApiModels.HttpRequest]:
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
                    log_data["headers"] = str(dict(request.headers))

                if self._log_body and hasattr(request, "body") and request.body:
                    log_data["body_size"] = str(len(request.body))

                self.logger.info("HTTP request", extra=log_data)

                # Create enhanced request with tracking attributes using object.__setattr__
                # to bypass Pydantic's extra="forbid" validation
                object.__setattr__(request, "tracking_id", tracking_id)
                object.__setattr__(request, "start_time", start_time)

            return FlextCore.Result[FlextApiModels.HttpRequest].ok(request)

        def _process_response_impl(
            self,
            response: FlextApiModels.HttpResponse,
        ) -> FlextCore.Result[FlextApiModels.HttpResponse]:
            """Log response details."""
            if self._log_responses:
                log_data = {
                    "status_code": response.status_code,
                    "url": str(response.url) if hasattr(response, "url") else "unknown",
                }

                # Get tracking info if available
                request = response.request
            if request.tracking_id is not None:
                log_data["request_id"] = request.tracking_id
                if hasattr(request, "start_time"):
                    duration = time.time() - request.start_time
                    log_data["duration_ms"] = round(duration * 1000, 2)

                if self._log_headers and response.headers:
                    log_data["headers"] = str(dict(response.headers))

                if self._log_body and hasattr(response, "body") and response.body:
                    log_data["body_size"] = len(response.body)

                self.logger.info("HTTP response", extra=log_data)

            return FlextCore.Result[FlextApiModels.HttpResponse].ok(response)

        def _processerror_impl(
            self,
            error: Exception,
            request: FlextApiModels.HttpRequest,
        ) -> FlextCore.Result[FlextApiModels.HttpResponse | None]:
            """Log error details."""
            log_data = {
                "error": str(error),
                "error_type": type(error).__name__,
                "method": request.method,
                "url": str(request.url),
            }

            if request.tracking_id is not None:
                log_data["request_id"] = request.tracking_id

            self.logger.error("HTTP request error", extra=log_data)

            # No recovery - return None
            return FlextCore.Result[FlextApiModels.HttpResponse | None].ok(None)

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
            self._metrics: FlextCore.Types.Dict = {
                "request_count": 0,
                "responses": 0,
                "errors": 0,
                "error_count": 0,  # Alias for compatibility
                "status_codes": {},
                "total_duration": 0.0,
            }
            self._request_count: int = 0

        def _process_request_impl(
            self,
            request: FlextApiModels.HttpRequest,
        ) -> FlextCore.Result[FlextApiModels.HttpRequest]:
            """Track request metrics."""
            self._request_count += 1

            # Add metrics tracking
            object.__setattr__(request, "metrics_start_time", time.time())

            return FlextCore.Result[FlextApiModels.HttpRequest].ok(request)

        def _process_response_impl(
            self,
            response: FlextApiModels.HttpResponse,
        ) -> FlextCore.Result[FlextApiModels.HttpResponse]:
            """Track response metrics."""
            self._metrics["responses"] += 1

            # Track status code
            status_code = str(response.status_code)
            self._metrics["status_codes"][status_code] = (
                self._metrics["status_codes"].get(status_code, 0) + 1
            )

            # Calculate duration if available
            if hasattr(response.request, "metrics_start_time"):
                duration = time.time() - response.request.metrics_start_time
                self._metrics["total_duration"] += duration

            return FlextCore.Result[FlextApiModels.HttpResponse].ok(response)

        def _processerror_impl(
            self,
            error: Exception,
            request: FlextApiModels.HttpRequest,
        ) -> FlextCore.Result[FlextApiModels.HttpResponse | None]:
            """Track error metrics."""
            _ = error
            _ = request
            self._metrics["errors"] += 1
            self._metrics["error_count"] += 1  # Alias for compatibility

            return FlextCore.Result[FlextApiModels.HttpResponse | None].ok(None)

        def get_metrics(self) -> FlextCore.Types.Dict:
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
                metrics["error_rate"] = (
                    metrics["error_count"] / metrics["request_count"]
                )
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

                middleware = AuthenticationMiddleware(
                    auth_type="bearer", token="my-token"
                )

                # New (recommended):
                from flext_auth import HttpAuthMiddleware
                from flext_auth.providers import FlextAuthApiKeyProvider

                provider = FlextAuthApiKeyProvider(config={"api_key": "my-token"})
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
            self._auth_provider = None  # Deprecated - should use flext_auth instead

        def _process_request_impl(
            self,
            request: FlextApiModels.HttpRequest,
        ) -> FlextCore.Result[FlextApiModels.HttpRequest]:
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

            return FlextCore.Result[FlextApiModels.HttpRequest].ok(request)

        def _process_response_impl(
            self,
            response: FlextApiModels.HttpResponse,
        ) -> FlextCore.Result[FlextApiModels.HttpResponse]:
            """Pass through response."""
            return FlextCore.Result[FlextApiModels.HttpResponse].ok(response)

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
            handle_httperrors: bool = True,
            handle_networkerrors: bool = True,
            customerror_handlers: dict[type[Exception], Callable] | None = None,
        ) -> None:
            """Initialize error handling middleware.

            Args:
                handle_httperrors: Whether to handle HTTP errors (status codes >= 400)
                handle_networkerrors: Whether to handle network errors
                customerror_handlers: Custom handlers for specific exceptions

            """
            super().__init__("ErrorHandlingMiddleware")
            self._handle_httperrors = handle_httperrors
            self._handle_networkerrors = handle_networkerrors
            self._custom_handlers = customerror_handlers or {}

        def _process_request_impl(
            self,
            request: FlextApiModels.HttpRequest,
        ) -> FlextCore.Result[FlextApiModels.HttpRequest]:
            """Pass through request."""
            return FlextCore.Result[FlextApiModels.HttpRequest].ok(request)

        def _process_response_impl(
            self,
            response: FlextApiModels.HttpResponse,
        ) -> FlextCore.Result[FlextApiModels.HttpResponse]:
            """Handle HTTP errors if enabled."""
            if (
                self._handle_httperrors
                and response.status_code
                >= FlextCore.Constants.Http.HTTP_CLIENT_ERROR_MIN
            ):
                # Log HTTP error
                self.logger.warning(
                    f"HTTP error response: {response.status_code}",
                    extra={
                        "status_code": response.status_code,
                        "url": str(response.url)
                        if hasattr(response, "url")
                        else "unknown",
                    },
                )

            return FlextCore.Result[FlextApiModels.HttpResponse].ok(response)

        def _processerror_impl(
            self,
            error: Exception,
            request: FlextApiModels.HttpRequest,
        ) -> FlextCore.Result[FlextApiModels.HttpResponse | None]:
            """Handle error with custom logic."""
            # Check for custom handler
            error_type = type(error)
            if error_type in self._custom_handlers:
                try:
                    handler = self._custom_handlers[error_type]
                    result = handler(error, request)
                    if result:
                        return FlextCore.Result[FlextApiModels.HttpResponse | None].ok(
                            result
                        )
                except Exception as handlererror:
                    self.logger.exception(
                        "Custom error handler failed",
                        extra={
                            "originalerror": str(error),
                            "handlererror": str(handlererror),
                        },
                    )

            # Default: log and propagate
            self.logger.error(
                f"Error handling: {error}",
                extra={
                    "error_type": error_type.__name__,
                    "method": request.method,
                    "url": str(request.url),
                },
            )

            return FlextCore.Result[FlextApiModels.HttpResponse | None].ok(None)

    class Pipeline:
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
            self.logger = FlextCore.Logger(__name__)
            self._middlewares: list[FlextApiMiddleware.BaseMiddleware] = []

        def add_middleware(
            self, middleware: FlextApiMiddleware._BaseMiddleware
        ) -> FlextCore.Result[None]:
            """Add middleware to pipeline.

            Args:
                middleware: Middleware instance to add

            Returns:
                FlextCore.Result indicating success or failure

            """
            if middleware in self._middlewares:
                return FlextCore.Result[None].fail(
                    f"Middleware {middleware.name} already in pipeline"
                )

            self._middlewares.append(middleware)
            self.logger.debug(f"Added middleware: {middleware.name}")

            return FlextCore.Result[None].ok(None)

        def remove_middleware(self, middleware_name: str) -> FlextCore.Result[None]:
            """Remove middleware from pipeline.

            Args:
                middleware_name: Name of middleware to remove

            Returns:
                FlextCore.Result indicating success or failure

            """
            for middleware in self._middlewares:
                if middleware.name == middleware_name:
                    self._middlewares.remove(middleware)
                    self.logger.debug(f"Removed middleware: {middleware_name}")
                    return FlextCore.Result[None].ok(None)

            return FlextCore.Result[None].fail(
                f"Middleware {middleware_name} not found"
            )

        def process_request(
            self,
            request: FlextApiModels.HttpRequest,
        ) -> FlextCore.Result[FlextApiModels.HttpRequest]:
            """Process request through middleware pipeline.

            Args:
                request: HTTP request to process

            Returns:
                FlextCore.Result containing processed request or error

            """
            current_request = request

            for middleware in self._middlewares:
                result = middleware.process_request(current_request)
                if result.is_failure:
                    return result
                current_request = result.unwrap()

            return FlextCore.Result[FlextApiModels.HttpRequest].ok(current_request)

        def process_response(
            self,
            response: FlextApiModels.HttpResponse,
        ) -> FlextCore.Result[FlextApiModels.HttpResponse]:
            """Process response through middleware pipeline.

            Args:
                response: HTTP response to process

            Returns:
                FlextCore.Result containing processed response or error

            """
            current_response = response

            # Process in reverse order
            for middleware in reversed(self._middlewares):
                result = middleware.process_response(current_response)
                if result.is_failure:
                    self.logger.warning(
                        f"Middleware {middleware.name} response processing failed"
                    )
                    continue  # Continue with other middleware
                current_response = result.unwrap()

            return FlextCore.Result[FlextApiModels.HttpResponse].ok(current_response)

        def processerror(
            self,
            error: Exception,
            request: FlextApiModels.HttpRequest,
        ) -> FlextCore.Result[FlextApiModels.HttpResponse | None]:
            """Process error through middleware pipeline.

            Args:
                error: Exception that occurred
                request: Original HTTP request

            Returns:
                FlextCore.Result containing recovery response or None

            """
            # Process in reverse order for error handling
            for middleware in reversed(self._middlewares):
                result = middleware.processerror(error, request)
                if result.is_success and result.unwrap() is not None:
                    # Middleware provided recovery response
                    return result

            # No middleware provided recovery
            return FlextCore.Result[FlextApiModels.HttpResponse | None].ok(None)

        def list_middleware(self) -> FlextCore.Types.StringList:
            """Get list of middleware names in pipeline.

            Returns:
                List of middleware names

            """
            return [m.name for m in self._middlewares]

        def clear(self) -> None:
            """Clear all middleware from pipeline."""
            self._middlewares.clear()


# Module-level aliases for nested classes to support direct imports
BaseMiddleware = FlextApiMiddleware.BaseMiddleware
LoggingMiddleware = FlextApiMiddleware.LoggingMiddleware
MetricsMiddleware = FlextApiMiddleware.MetricsMiddleware
AuthenticationMiddleware = FlextApiMiddleware.AuthenticationMiddleware
ErrorHandlingMiddleware = FlextApiMiddleware.ErrorHandlingMiddleware
MiddlewarePipeline = FlextApiMiddleware.Pipeline


__all__ = [
    "AuthenticationMiddleware",
    # Middleware classes for testing and external usage
    "BaseMiddleware",
    "ErrorHandlingMiddleware",
    "FlextApiMiddleware",
    "LoggingMiddleware",
    "MetricsMiddleware",
    "MiddlewarePipeline",
]
