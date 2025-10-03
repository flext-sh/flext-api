"""Exception definitions for flext-api domain.

All exception classes extend FlextExceptions from flext-core following FLEXT
ecosystem standards. HTTP-specific exception hierarchy with status codes,
error codes, and correlation tracking.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

from flext_core import FlextConstants, FlextExceptions


class FlextApiExceptions:
    """HTTP API exception classes extending FlextExceptions.

    All HTTP exceptions properly extend FlextExceptions.BaseError for
    structured error handling with error codes and correlation tracking.
    """

    class ApiError(FlextExceptions.BaseError):
        """Base HTTP API error with status code and request context."""

        @override
        def __init__(
            self,
            message: str,
            *,
            status_code: int = FlextConstants.Http.HTTP_INTERNAL_SERVER_ERROR,
            endpoint: str | None = None,
            method: str | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize HTTP API error with request context."""
            self.status_code = status_code
            self.endpoint = endpoint
            self.method = method

            # Extract common parameters
            base_context, correlation_id, error_code = self._extract_common_kwargs(
                kwargs
            )

            # Build context with HTTP-specific fields
            context = self._build_context(
                base_context,
                status_code=status_code,
                endpoint=endpoint,
                method=method,
            )

            super().__init__(
                message,
                code=error_code or f"HTTP_{status_code}",
                context=context,
                correlation_id=correlation_id,
            )

    class ValidationError(FlextExceptions.ValidationError):
        """HTTP validation error with status code - extends FlextExceptions."""

        @override
        def __init__(
            self,
            message: str,
            status_code: int = FlextConstants.Http.HTTP_BAD_REQUEST,
            **kwargs: object,
        ) -> None:
            """Initialize HTTP validation error."""
            self.status_code = status_code

            # Extract common parameters
            base_context, correlation_id, error_code = self._extract_common_kwargs(
                kwargs
            )

            # Build context with HTTP status
            context = self._build_context(
                base_context,
                status_code=status_code,
            )

            super().__init__(
                message,
                context=context,
                correlation_id=correlation_id,
                error_code=error_code or f"HTTP_{status_code}",
                **{
                    k: v
                    for k, v in kwargs.items()
                    if k not in {"context", "correlation_id", "error_code"}
                },
            )

    class AuthenticationError(ApiError):
        """HTTP authentication error (401) - extends ApiError."""

        @override
        def __init__(
            self,
            message: str,
            status_code: int = FlextConstants.Http.HTTP_UNAUTHORIZED,
            **kwargs: object,
        ) -> None:
            """Initialize HTTP authentication error."""
            super().__init__(message, status_code=status_code, **kwargs)

    class AuthorizationError(ApiError):
        """HTTP authorization error (403) - extends ApiError."""

        @override
        def __init__(
            self,
            message: str,
            status_code: int = FlextConstants.Http.HTTP_FORBIDDEN,
            **kwargs: object,
        ) -> None:
            """Initialize HTTP authorization error."""
            super().__init__(message, status_code=status_code, **kwargs)

    class NotFoundError(FlextExceptions.NotFoundError):
        """HTTP not found error (404) - extends FlextExceptions."""

        @override
        def __init__(
            self,
            message: str,
            status_code: int = FlextConstants.Http.HTTP_NOT_FOUND,
            **kwargs: object,
        ) -> None:
            """Initialize HTTP not found error."""
            self.status_code = status_code

            # Extract common parameters
            base_context, correlation_id, _ = self._extract_common_kwargs(kwargs)

            # Build context with HTTP status
            context = self._build_context(
                base_context,
                status_code=status_code,
            )

            super().__init__(
                message,
                context=context,
                correlation_id=correlation_id,
                **{
                    k: v
                    for k, v in kwargs.items()
                    if k not in {"context", "correlation_id", "error_code"}
                },
            )

    class ConflictError(ApiError):
        """HTTP conflict error (409) - extends ApiError."""

        @override
        def __init__(
            self, message: str, status_code: int = 409, **kwargs: object
        ) -> None:
            """Initialize HTTP conflict error."""
            super().__init__(message, status_code=status_code, **kwargs)

    class RateLimitError(ApiError):
        """HTTP rate limit error (429) - extends ApiError."""

        @override
        def __init__(
            self, message: str, status_code: int = 429, **kwargs: object
        ) -> None:
            """Initialize HTTP rate limit error."""
            super().__init__(message, status_code=status_code, **kwargs)

    class HttpError(ApiError):
        """General HTTP error - alias for ApiError."""

        @override
        def __init__(
            self,
            message: str,
            status_code: int = FlextConstants.Http.HTTP_INTERNAL_SERVER_ERROR,
            url: str | None = None,
            method: str | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize HTTP error with request context."""
            super().__init__(
                message, status_code=status_code, endpoint=url, method=method, **kwargs
            )

    class HttpTimeoutError(ApiError):
        """HTTP timeout error (408) - extends ApiError."""

        @override
        def __init__(
            self,
            message: str,
            status_code: int = 408,
            url: str | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize HTTP timeout error."""
            super().__init__(message, status_code=status_code, endpoint=url, **kwargs)

    class ClientError(ApiError):
        """HTTP client error (4xx status codes) - extends ApiError."""

        @override
        def __init__(
            self,
            message: str,
            status_code: int = FlextConstants.Http.HTTP_BAD_REQUEST,
            **kwargs: object,
        ) -> None:
            """Initialize HTTP client error."""
            if not (
                FlextConstants.Http.HTTP_CLIENT_ERROR_MIN
                <= status_code
                <= FlextConstants.Http.HTTP_CLIENT_ERROR_MAX
            ):
                msg = f"Client error status code must be 4xx, got {status_code}"
                raise ValueError(msg)
            super().__init__(message, status_code=status_code, **kwargs)

    class ServerError(ApiError):
        """HTTP server error (5xx status codes) - extends ApiError."""

        @override
        def __init__(
            self,
            message: str,
            status_code: int = FlextConstants.Http.HTTP_INTERNAL_SERVER_ERROR,
            **kwargs: object,
        ) -> None:
            """Initialize HTTP server error."""
            if not (
                FlextConstants.Http.HTTP_SERVER_ERROR_MIN
                <= status_code
                <= FlextConstants.Http.HTTP_SERVER_ERROR_MAX
            ):
                msg = f"Server error status code must be 5xx, got {status_code}"
                raise ValueError(msg)
            super().__init__(message, status_code=status_code, **kwargs)

    class BadRequestError(ClientError):
        """HTTP 400 Bad Request error - extends ClientError."""

        @override
        def __init__(self, message: str = "Bad Request", **kwargs: object) -> None:
            """Initialize HTTP 400 error."""
            super().__init__(
                message, status_code=FlextConstants.Http.HTTP_BAD_REQUEST, **kwargs
            )

    class UnauthorizedError(ClientError):
        """HTTP 401 Unauthorized error - extends ClientError."""

        @override
        def __init__(self, message: str = "Unauthorized", **kwargs: object) -> None:
            """Initialize HTTP 401 error."""
            super().__init__(
                message, status_code=FlextConstants.Http.HTTP_UNAUTHORIZED, **kwargs
            )

    class ForbiddenError(ClientError):
        """HTTP 403 Forbidden error - extends ClientError."""

        @override
        def __init__(self, message: str = "Forbidden", **kwargs: object) -> None:
            """Initialize HTTP 403 error."""
            super().__init__(
                message, status_code=FlextConstants.Http.HTTP_FORBIDDEN, **kwargs
            )

    class MethodNotAllowedError(ClientError):
        """HTTP 405 Method Not Allowed error - extends ClientError."""

        @override
        def __init__(
            self, message: str = "Method Not Allowed", **kwargs: object
        ) -> None:
            """Initialize HTTP 405 error."""
            super().__init__(message, status_code=405, **kwargs)

    class RequestTimeoutError(ClientError):
        """HTTP 408 Request Timeout error - extends ClientError."""

        @override
        def __init__(self, message: str = "Request Timeout", **kwargs: object) -> None:
            """Initialize HTTP 408 error."""
            super().__init__(message, status_code=408, **kwargs)

    class TooManyRequestsError(ClientError):
        """HTTP 429 Too Many Requests error - extends ClientError."""

        @override
        def __init__(
            self, message: str = "Too Many Requests", **kwargs: object
        ) -> None:
            """Initialize HTTP 429 error."""
            super().__init__(message, status_code=429, **kwargs)

    class InternalServerError(ServerError):
        """HTTP 500 Internal Server Error - extends ServerError."""

        @override
        def __init__(
            self, message: str = "Internal Server Error", **kwargs: object
        ) -> None:
            """Initialize HTTP 500 error."""
            super().__init__(
                message,
                status_code=FlextConstants.Http.HTTP_INTERNAL_SERVER_ERROR,
                **kwargs,
            )

    class BadGatewayError(ServerError):
        """HTTP 502 Bad Gateway error - extends ServerError."""

        @override
        def __init__(self, message: str = "Bad Gateway", **kwargs: object) -> None:
            """Initialize HTTP 502 error."""
            super().__init__(message, status_code=502, **kwargs)

    class ServiceUnavailableError(ServerError):
        """HTTP 503 Service Unavailable error - extends ServerError."""

        @override
        def __init__(
            self, message: str = "Service Unavailable", **kwargs: object
        ) -> None:
            """Initialize HTTP 503 error."""
            super().__init__(message, status_code=503, **kwargs)

    class GatewayTimeoutError(ServerError):
        """HTTP 504 Gateway Timeout error - extends ServerError."""

        @override
        def __init__(self, message: str = "Gateway Timeout", **kwargs: object) -> None:
            """Initialize HTTP 504 error."""
            super().__init__(message, status_code=504, **kwargs)


__all__ = ["FlextApiExceptions"]
