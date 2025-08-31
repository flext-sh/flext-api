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

from flext_core import FlextExceptions

from flext_api.constants import FlextApiConstants


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
            error_code: str | None = None,  # noqa: ARG002
            context: dict[str, object] | None = None,
        ) -> None:
            super().__init__(message)
            self.status_code = status_code
            self.context = context or {}
            # error_code is handled by parent class

    class HttpError(FlextApiError):
        """Base class for HTTP protocol errors."""

        def __init__(
            self,
            message: str,
            status_code: int,
            url: str | None = None,
            method: str | None = None,
            headers: dict[str, str] | None = None,
            context: dict[str, object] | None = None,
        ) -> None:
            error_context = {
                "url": url,
                "method": method,
                "headers": headers,
                **(context or {}),
            }
            super().__init__(
                message, status_code, FlextApiConstants.HttpErrors.HTTP_ERROR, error_context
            )

    class ClientError(HttpError):
        """Base class for HTTP client errors (4xx status codes)."""

    class ServerError(HttpError):
        """Base class for HTTP server errors (5xx status codes)."""

    # Specific Client Errors (4xx)
    class BadRequestError(ClientError):
        """400 Bad Request error."""

        def __init__(
            self,
            message: str = "Bad Request",
            url: str | None = None,
            method: str | None = None,
            headers: dict[str, str] | None = None,
            context: dict[str, object] | None = None,
        ) -> None:
            super().__init__(message, FlextApiConstants.HttpStatus.BAD_REQUEST, url, method, headers, context)

    class UnauthorizedError(ClientError):
        """401 Unauthorized error."""

        def __init__(
            self,
            message: str = "Unauthorized",
            url: str | None = None,
            method: str | None = None,
            headers: dict[str, str] | None = None,
            context: dict[str, object] | None = None,
        ) -> None:
            super().__init__(message, FlextApiConstants.HttpStatus.UNAUTHORIZED, url, method, headers, context)

    class ForbiddenError(ClientError):
        """403 Forbidden error."""

        def __init__(
            self,
            message: str = "Forbidden",
            url: str | None = None,
            method: str | None = None,
            headers: dict[str, str] | None = None,
            context: dict[str, object] | None = None,
        ) -> None:
            super().__init__(message, FlextApiConstants.HttpStatus.FORBIDDEN, url, method, headers, context)

    class NotFoundError(ClientError):
        """404 Not Found error."""

        def __init__(
            self,
            message: str = "Not Found",
            url: str | None = None,
            method: str | None = None,
            headers: dict[str, str] | None = None,
            context: dict[str, object] | None = None,
        ) -> None:
            super().__init__(message, FlextApiConstants.HttpStatus.NOT_FOUND, url, method, headers, context)

    class RequestTimeoutError(ClientError):
        """Request timeout error."""

        def __init__(
            self,
            message: str = "Request timeout",
            timeout: float | None = None,
            url: str | None = None,
            method: str | None = None,
            headers: dict[str, str] | None = None,
            context: dict[str, object] | None = None,
        ) -> None:
            timeout_context: dict[str, object] = {"timeout": timeout}
            if context:
                timeout_context.update(context)
            super().__init__(
                message,
                FlextApiConstants.HttpStatus.GATEWAY_TIMEOUT,
                url,
                method,
                headers,
                timeout_context,
            )

    class RateLimitError(ClientError):
        """429 Too Many Requests error."""

        def __init__(
            self,
            message: str = "Rate limit exceeded",
            url: str | None = None,
            method: str | None = None,
            headers: dict[str, str] | None = None,
            context: dict[str, object] | None = None,
        ) -> None:
            super().__init__(
                message, FlextApiConstants.HttpStatus.TOO_MANY_REQUESTS, url, method, headers, context
            )

    # Specific Server Errors (5xx)
    class InternalServerError(ServerError):
        """500 Internal Server Error."""

        def __init__(
            self,
            message: str = "Internal Server Error",
            url: str | None = None,
            method: str | None = None,
            headers: dict[str, str] | None = None,
            context: dict[str, object] | None = None,
        ) -> None:
            super().__init__(
                message, FlextApiConstants.HttpStatus.INTERNAL_SERVER_ERROR, url, method, headers, context
            )

    class BadGatewayError(ServerError):
        """502 Bad Gateway error."""

        def __init__(
            self,
            message: str = "Bad Gateway",
            url: str | None = None,
            method: str | None = None,
            headers: dict[str, str] | None = None,
            context: dict[str, object] | None = None,
        ) -> None:
            super().__init__(message, FlextApiConstants.HttpStatus.BAD_GATEWAY, url, method, headers, context)

    class ServiceUnavailableError(ServerError):
        """503 Service Unavailable error."""

        def __init__(
            self,
            message: str = "Service Unavailable",
            url: str | None = None,
            method: str | None = None,
            headers: dict[str, str] | None = None,
            context: dict[str, object] | None = None,
        ) -> None:
            super().__init__(
                message, FlextApiConstants.HttpStatus.SERVICE_UNAVAILABLE, url, method, headers, context
            )

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
            message: str = "Validation error",
            field: str | None = None,
            value: object = None,
            url: str | None = None,
            method: str | None = None,
            headers: dict[str, str] | None = None,
            context: dict[str, object] | None = None,
        ) -> None:
            validation_context: dict[str, object] = {"field": field, "value": value}
            if url:
                validation_context["url"] = url
            if method:
                validation_context["method"] = method
            if headers:
                validation_context["headers"] = headers
            if context:
                validation_context.update(context)
            super().__init__(
                message,
                status_code=FlextApiConstants.HttpStatus.BAD_REQUEST,
                error_code=FlextApiConstants.HttpErrors.VALIDATION_ERROR,
                context=validation_context,
            )


__all__ = ["FlextApiExceptions"]
