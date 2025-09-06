"""FLEXT API Exceptions - Hierarchical exception system for HTTP API functionality.

HTTP-specific exception system providing FlextApiExceptions class with structured
error handling, HTTP status codes, and comprehensive error context for debugging.

Module Role in Architecture:
    FlextApiExceptions serves as the HTTP API exception system, providing hierarchical
    exception classes with HTTP status codes, error context, and structured error
    handling following FlextResult patterns.

Classes and Methods:
    FlextApiExceptions:                     # Hierarchical HTTP API exception system
        # Base Exceptions:
        FlextApiError(FlextError)           # Base HTTP API exception
        HttpError(FlextApiError)            # HTTP protocol errors
        ClientError(FlextApiError)          # HTTP client errors
        ServerError(FlextApiError)          # HTTP server errors

        # Specific HTTP Exceptions:
        BadRequestError(ClientError)        # 400 Bad Request
        UnauthorizedError(ClientError)      # 401 Unauthorized
        ForbiddenError(ClientError)         # 403 Forbidden
        NotFoundError(ClientError)          # 404 Not Found
        TimeoutError(ClientError)           # Request timeout
        RateLimitError(ClientError)         # 429 Too Many Requests

        # Server Exceptions:
        InternalServerError(ServerError)    # 500 Internal Server Error
        BadGatewayError(ServerError)        # 502 Bad Gateway
        ServiceUnavailableError(ServerError) # 503 Service Unavailable

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, cast

from flext_core import FlextExceptions

from flext_api.constants import FlextApiConstants
from flext_api.utilities import HttpErrorConfig

if TYPE_CHECKING:
    from flext_api.utilities import ValidationConfig


class FlextApiExceptions(FlextExceptions):
    """Single hierarchical exception class for all FLEXT API exceptions.

    Organized by domain with HTTP status codes and comprehensive error context
    for debugging and structured error handling.
    """

    class FlextApiError(FlextExceptions.BaseError):
        """Base exception for all FLEXT API errors."""

        def __init__(
            self,
            message: str,
            status_code: int = 500,
            error_code: str | None = None,
            context: dict[str, object] | None = None,
        ) -> None:
            super().__init__(message, code=error_code, context=context)
            self.status_code = status_code
            self.context = context or {}
            # error_code is handled by parent class

    class HttpError(FlextApiError):
        """Base class for HTTP protocol errors."""

        def __init__(self, config: HttpErrorConfig) -> None:
            """Initialize from Pydantic configuration - zero parameter complexity."""
            error_context = config.context.copy()
            if config.url:
                error_context["url"] = config.url
            if config.method:
                error_context["method"] = config.method
            if config.headers:
                error_context["headers"] = config.headers

            super().__init__(
                config.message,
                config.status_code,
                FlextApiConstants.HttpErrors.HTTP_ERROR,
                error_context,
            )

    class ClientError(HttpError):
        """Base class for HTTP client errors (4xx status codes)."""

    class ServerError(HttpError):
        """Base class for HTTP server errors (5xx status codes)."""

    # Exception factory using Template Method Pattern - eliminates ALL duplication
    class _HttpExceptionFactory:
        """Factory for creating HTTP exception classes using advanced patterns."""

        @staticmethod
        def create_exception_class(
            name: str,
            base_class: type[FlextApiExceptions.HttpError],
            status_code: int,
            default_message: str,
            docstring: str,
        ) -> type[FlextApiExceptions.HttpError]:
            """Create exception class using Factory Pattern and Template Method."""

            def __init__(
                self: FlextApiExceptions.HttpError,
                message_or_config: str | HttpErrorConfig | None = None,
                url: str | None = None,
                method: str | None = None,
                headers: dict[str, str] | None = None,
                context: dict[str, object] | None = None,
                **deprecated_kwargs: object,
            ) -> None:
                """Initialize using legacy string or Pydantic configuration."""
                if isinstance(message_or_config, str):
                    # Legacy API: first parameter is message string
                    final_context: dict[str, object] = context or {}

                    # Add additional context from remaining kwargs
                    final_context.update(
                        {
                            key: value
                            for key, value in deprecated_kwargs.items()
                            if value is not None
                        },
                    )

                    config = HttpErrorConfig(
                        message=message_or_config,
                        status_code=status_code,
                        url=url,
                        method=method,
                        headers=headers,
                        context=final_context,
                    )
                elif isinstance(message_or_config, HttpErrorConfig):
                    # New API: first parameter is config object
                    config = message_or_config
                else:
                    # Default case: construct from kwargs or defaults
                    message = str(deprecated_kwargs.get("message", default_message))
                    url_from_kwargs = deprecated_kwargs.get("url")
                    method_from_kwargs = deprecated_kwargs.get("method")
                    url_final = str(url_from_kwargs) if url_from_kwargs else url
                    method_final = (
                        str(method_from_kwargs) if method_from_kwargs else method
                    )
                    headers_from_kwargs = deprecated_kwargs.get("headers")
                    context_from_kwargs = deprecated_kwargs.get("context", {})

                    # Build context from remaining kwargs with type safety
                    fallback_context: dict[str, object] = context or {}
                    if context_from_kwargs and isinstance(context_from_kwargs, dict):
                        fallback_context.update(context_from_kwargs)

                    # Dictionary comprehension for better performance
                    fallback_context.update(
                        {
                            key: value
                            for key, value in deprecated_kwargs.items()
                            if key
                            not in {"message", "url", "method", "headers", "context"}
                            and value is not None
                        },
                    )

                    # Type-safe header conversion
                    safe_headers = headers
                    if headers_from_kwargs and isinstance(headers_from_kwargs, dict):
                        safe_headers = {
                            str(k): str(v) for k, v in headers_from_kwargs.items()
                        }

                    config = HttpErrorConfig(
                        message=message,
                        status_code=status_code,
                        url=url_final,
                        method=method_final,
                        headers=safe_headers,
                        context=fallback_context,
                    )

                base_class.__init__(self, config)

            # Create dynamic class using type() with proper casting
            dynamic_class = type(
                name,
                (base_class,),
                {
                    "__init__": __init__,
                    "__doc__": docstring,
                    "__module__": __name__,
                },
            )
            return cast("type[FlextApiExceptions.HttpError]", dynamic_class)

    # HTTP Exception Specifications - using data-driven approach
    _HTTP_EXCEPTION_SPECS: ClassVar[list[tuple[str, type, int, str, str]]] = [
        # Client Errors (4xx)
        (
            "BadRequestError",
            ClientError,
            FlextApiConstants.HttpStatus.BAD_REQUEST,
            "Bad Request",
            "400 Bad Request error.",
        ),
        (
            "UnauthorizedError",
            ClientError,
            FlextApiConstants.HttpStatus.UNAUTHORIZED,
            "Unauthorized",
            "401 Unauthorized error.",
        ),
        (
            "ForbiddenError",
            ClientError,
            FlextApiConstants.HttpStatus.FORBIDDEN,
            "Forbidden",
            "403 Forbidden error.",
        ),
        (
            "NotFoundError",
            ClientError,
            FlextApiConstants.HttpStatus.NOT_FOUND,
            "Not Found",
            "404 Not Found error.",
        ),
        (
            "RequestTimeoutError",
            ClientError,
            FlextApiConstants.HttpStatus.GATEWAY_TIMEOUT,
            "Request timeout",
            "Request timeout error.",
        ),
        (
            "RateLimitError",
            ClientError,
            FlextApiConstants.HttpStatus.TOO_MANY_REQUESTS,
            "Rate limit exceeded",
            "429 Too Many Requests error.",
        ),
        # Server Errors (5xx)
        (
            "InternalServerError",
            ServerError,
            FlextApiConstants.HttpStatus.INTERNAL_SERVER_ERROR,
            "Internal Server Error",
            "500 Internal Server Error.",
        ),
        (
            "BadGatewayError",
            ServerError,
            FlextApiConstants.HttpStatus.BAD_GATEWAY,
            "Bad Gateway",
            "502 Bad Gateway error.",
        ),
        (
            "ServiceUnavailableError",
            ServerError,
            FlextApiConstants.HttpStatus.SERVICE_UNAVAILABLE,
            "Service Unavailable",
            "503 Service Unavailable error.",
        ),
    ]

    # Generate exception classes dynamically - ZERO duplication
    @classmethod
    def _generate_http_exceptions(cls) -> None:
        """Generate HTTP exception classes using Factory Pattern."""
        for spec in cls._HTTP_EXCEPTION_SPECS:
            name, base_class, status_code, default_message, docstring = spec
            exception_class = cls._HttpExceptionFactory.create_exception_class(
                name,
                base_class,
                status_code,
                default_message,
                docstring,
            )
            setattr(cls, name, exception_class)

    # Network-specific Errors
    class NetworkError(FlextApiError):
        """Network connectivity error."""

        def __init__(
            self,
            message: str = "Network error",
            url: str | None = None,
            method: str | None = None,
            headers: dict[str, str] | None = None,
            context: dict[str, object] | None = None,
        ) -> None:
            network_context: dict[str, object] = {}
            if url:
                network_context["url"] = url
            if method:
                network_context["method"] = method
            if headers:
                network_context["headers"] = headers
            if context:
                network_context.update(context)
            super().__init__(
                message,
                status_code=0,  # No HTTP status for network errors
                error_code=FlextApiConstants.HttpErrors.NETWORK_ERROR,
                context=network_context,
            )

    class RequestConnectionError(NetworkError):
        """Connection establishment error."""

        def __init__(
            self,
            message: str = "Connection error",
            url: str | None = None,
            method: str | None = None,
            headers: dict[str, str] | None = None,
            context: dict[str, object] | None = None,
        ) -> None:
            super().__init__(message, url, method, headers, context)

    # Validation Errors
    class ValidationError(FlextApiError):
        """Request/response validation error."""

        def __init__(
            self,
            config_or_message: ValidationConfig | str,
            field: str | None = None,
            value: object = None,
            url: str | None = None,
            method: str | None = None,
            headers: dict[str, str] | None = None,
            context: dict[str, object] | None = None,
        ) -> None:
            """Initialize from Pydantic ValidationConfig or legacy string message."""
            if isinstance(config_or_message, str):
                # Legacy API support - build config from parameters
                validation_context: dict[str, object] = context or {}
                if field:
                    validation_context["field"] = field
                if value is not None:
                    validation_context["value"] = value
                if url:
                    validation_context["url"] = url
                if method:
                    validation_context["method"] = method
                if headers:
                    validation_context["headers"] = headers

                super().__init__(
                    config_or_message,
                    status_code=FlextApiConstants.HttpStatus.BAD_REQUEST,
                    error_code=FlextApiConstants.HttpErrors.VALIDATION_ERROR,
                    context=validation_context,
                )
            else:
                # New config-based API
                config = config_or_message
                validation_context = config.context.copy()
                if config.field:
                    validation_context["field"] = config.field
                if config.value is not None:
                    validation_context["value"] = config.value
                if config.url:
                    validation_context["url"] = config.url
                if config.method:
                    validation_context["method"] = config.method
                if config.headers:
                    validation_context["headers"] = config.headers

                super().__init__(
                    config.message,
                    status_code=FlextApiConstants.HttpStatus.BAD_REQUEST,
                    error_code=FlextApiConstants.HttpErrors.VALIDATION_ERROR,
                    context=validation_context,
                )


# Generate exceptions when module loads
FlextApiExceptions._generate_http_exceptions()

# Backward compatibility aliases - add after generation
FlextApiExceptions.AuthenticationError = getattr(
    FlextApiExceptions, "UnauthorizedError"
)

# Main FlextErrors alias
FlextErrors = FlextApiExceptions

__all__ = ["FlextApiExceptions", "FlextErrors"]
