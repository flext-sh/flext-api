"""FLEXT API Exceptions - Hierarchical exception system for HTTP API functionality.

HTTP-specific exception system providing FlextApiExceptions class with structured
error handling, HTTP status codes, and comprehensive error context for debugging.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.constants import FlextApiConstants
from flext_core import FlextExceptions


class FlextApiExceptions:
    """HTTP API exceptions using flext-core extensively - ZERO DUPLICATION."""

    # =============================================================================
    # HTTP-SPECIFIC EXCEPTIONS ONLY - ZERO TOLERANCE for re-exports
    # MANDATORY: Use FlextExceptions.BaseError directly instead of aliases
    # =============================================================================

    # HTTP-specific exception classes with status_code property
    class ValidationError(FlextExceptions._ValidationError):
        """Validation error with HTTP status code."""

        def __init__(self, message: str, **_kwargs: object) -> None:
            """Initialize validation error with HTTP status code."""
            super().__init__(message)
            self.status_code = 400

    class AuthenticationError(FlextExceptions._AuthenticationError):
        """Authentication error with HTTP status code."""

        def __init__(self, message: str, **_kwargs: object) -> None:
            """Initialize authentication error with HTTP status code."""
            super().__init__(message)
            self.status_code = 401

    class NotFoundError(FlextExceptions._NotFoundError):
        """Not found error with HTTP status code."""

        def __init__(self, message: str, **_kwargs: object) -> None:
            """Initialize not found error with HTTP status code."""
            super().__init__(message)
            self.status_code = 404

    # =============================================================================
    # HTTP-specific simple aliases - Use existing flext-core patterns

    # HTTP Error - Main HTTP exception class with status_code
    class HttpError(FlextExceptions._ConnectionError):
        """HTTP error with status code attribute."""

        def __init__(
            self, message: str, status_code: int = 500, **kwargs: object,
        ) -> None:
            """Initialize HTTP error with status code."""
            # Extract only the parameters the parent class accepts
            service_value = kwargs.get("service")
            endpoint_value = kwargs.get("endpoint")
            super().__init__(
                message,
                service=str(service_value) if service_value is not None else None,
                endpoint=str(endpoint_value) if endpoint_value is not None else None,
            )
            self.status_code = status_code

    # Compatibility alias removed - use HttpError directly

    @classmethod
    def http_error_class(cls) -> type[HttpError]:
        """Get HTTP error class."""
        return cls.HttpError

    # =============================================================================

    # HTTP errors using flext-core ConnectionError with HTTP-specific parameters
    @classmethod
    def http_error(
        cls,
        message: str,
        *,
        status_code: int = 500,
        url: str | None = None,
        method: str | None = None,
        **kwargs: object,
    ) -> FlextApiExceptions.HttpError:
        """Create HTTP error with status code."""
        enhanced_message = f"{message} (HTTP {status_code})"
        return cls.HttpError(
            message=enhanced_message,
            status_code=status_code,
            service="http_api",
            endpoint=f"{method} {url}" if method and url else url or "unknown",
            **kwargs,  # Pass through additional kwargs
        )

    @classmethod
    def timeout_error(
        cls, message: str = "HTTP request timeout", *, url: str | None = None,
    ) -> FlextExceptions.BaseError:
        """Create HTTP timeout error using flext-core TimeoutError."""
        enhanced_message = f"{message} for {url}" if url else message
        return FlextExceptions.TimeoutError(message=enhanced_message)

    @classmethod
    def validation_error(
        cls, message: str, *, field: str | None = None,
    ) -> FlextExceptions.BaseError:
        """Create HTTP validation error using flext-core ValidationError."""
        enhanced_message = f"{message} (field: {field})" if field else message
        return FlextExceptions.ValidationError(message=enhanced_message)

    @classmethod
    def auth_error(
        cls, message: str = "Authentication failed",
    ) -> FlextExceptions.BaseError:
        """Create HTTP auth error using flext-core AuthenticationError."""
        return FlextExceptions.AuthenticationError(message=message)

    # =============================================================================
    # HTTP Status Code Factory Methods - Streamlined for reduced bloat
    # =============================================================================

    @classmethod
    def bad_request(cls, message: str = "Bad Request") -> FlextExceptions.BaseError:
        """Create HTTP 400 Bad Request error."""
        return cls.http_error(message, status_code=400)

    @classmethod
    def unauthorized(cls, message: str = "Unauthorized") -> FlextExceptions.BaseError:
        """Create HTTP 401 Unauthorized error."""
        return cls.http_error(message, status_code=401)

    @classmethod
    def forbidden(cls, message: str = "Forbidden") -> FlextExceptions.BaseError:
        """Create HTTP 403 Forbidden error."""
        return cls.http_error(message, status_code=403)

    @classmethod
    def not_found(cls, message: str = "Not Found") -> FlextExceptions.BaseError:
        """Create HTTP 404 Not Found error."""
        return cls.http_error(message, status_code=404)

    @classmethod
    def request_timeout(
        cls, message: str = "Request Timeout",
    ) -> FlextExceptions.BaseError:
        """Create HTTP 408 Request Timeout error."""
        return cls.http_error(message, status_code=408)

    @classmethod
    def too_many_requests(
        cls, message: str = "Too Many Requests",
    ) -> FlextExceptions.BaseError:
        """Create HTTP 429 Too Many Requests error."""
        return cls.http_error(message, status_code=429)

    @classmethod
    def internal_server_error(
        cls, message: str = "Internal Server Error",
    ) -> FlextExceptions.BaseError:
        """Create HTTP 500 Internal Server Error."""
        return cls.http_error(message, status_code=500)

    # =============================================================================
    # Simple HTTP status code helpers - Use flext-core constants
    # =============================================================================

    @staticmethod
    def is_client_error(status_code: int) -> bool:
        """Check if status code is client error (4xx)."""
        return (
            FlextApiConstants.CLIENT_ERROR_START
            <= status_code
            < FlextApiConstants.SERVER_ERROR_START
        )

    @staticmethod
    def is_server_error(status_code: int) -> bool:
        """Check if status code is server error (5xx)."""
        return (
            FlextApiConstants.SERVER_ERROR_START
            <= status_code
            < FlextApiConstants.SERVER_ERROR_END
        )

    @staticmethod
    def is_success(status_code: int) -> bool:
        """Check if status code indicates success (2xx)."""
        return (
            FlextApiConstants.SUCCESS_START
            <= status_code
            < FlextApiConstants.SUCCESS_END
        )


__all__ = ["FlextApiExceptions"]
