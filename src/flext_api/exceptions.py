"""FLEXT API Exceptions - Structured exception hierarchy for flext-api.

This module provides FlextApiExceptions, a namespace class containing structured
exception types with HTTP status codes and metadata for comprehensive error handling
in HTTP operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextExceptions


class FlextApiExceptions:
    """Structured exception hierarchy for flext-api HTTP operations.

    Architecture: Domain Layer (HTTP-Specific Exceptions)
    ===================================================
    Provides HTTP-specific exception types that extend flext-core exceptions
    with HTTP status codes and request/response context. All exceptions integrate
    with FlextResult error handling and structured logging.

    **HTTP Exception Hierarchy** (9 types):
    1. **FlextWebError**: HTTP base class with status codes and request context (500 default)
       - HTTP status code integration
       - Request/response metadata preservation
       - URL and method context tracking

    2. **ConfigurationError**: HTTP client configuration issues
       - Invalid timeout, retry, or connection settings
       - Base URL validation failures

    3. **ConnectionError**: Network connectivity problems
       - DNS resolution failures
       - TCP connection timeouts
       - SSL/TLS handshake errors

    4. **TimeoutError**: Request timeout scenarios
       - Read timeouts during response
       - Connection establishment timeouts
       - Overall request timeouts

    5. **ValidationError**: Request/response validation failures (400 default)
       - Invalid HTTP headers or body format
       - Schema validation errors
       - Content-Type mismatches

    6. **NotFoundError**: HTTP 404 and resource not found (404 default)
       - Endpoint doesn't exist
       - Resource deleted or moved
       - Invalid URL paths

    7. **AuthenticationError**: HTTP authentication failures (401 default)
       - Invalid credentials (401)
       - Missing authentication headers
       - Token expiration

    8. **AuthorizationError**: HTTP authorization failures (403 default)
       - Insufficient permissions (403)
       - Role-based access control violations
       - Scope limitations

    9. **RateLimitError**: HTTP rate limiting (429 default)
       - Too many requests, quota exceeded, throttling

    **Usage Patterns**:
    ```python
    # Railway pattern with HTTP exceptions
    result = client.request(request)
    if result.is_failure:
        if isinstance(result.error, FlextApiExceptions.ConnectionError):
            # Handle connection issues
            return FlextResult.fail("Network unavailable")
        elif isinstance(result.error, FlextApiExceptions.TimeoutError):
            # Handle timeout scenarios
            return FlextResult.fail("Request timed out")

    # Exception chaining for context
    try:
        response = client.get("/api/data")
    except FlextApiExceptions.ConnectionError as e:
        raise FlextApiExceptions.TimeoutError("Request failed") from e
    ```
    """

    class FlextWebError(FlextExceptions.BaseError):
        """Base exception for HTTP operations with status code support."""

        def __init__(
            self,
            message: str,
            status_code: int | None = 500,
            url: str | None = None,
            method: str | None = None,
            **metadata: object,
        ) -> None:
            """Initialize HTTP error with status code and metadata."""
            super().__init__(message, **metadata)
            self.status_code = status_code
            self.url = url
            self.method = method

        def to_dict(self) -> dict[str, object]:
            """Convert exception to dictionary with HTTP context."""
            base_dict = super().to_dict()
            base_dict.update({
                "status_code": self.status_code,
                "url": self.url,
                "method": self.method,
            })
            return base_dict

    class ConfigurationError(FlextWebError):
        """Exception raised for HTTP client configuration errors.

        Examples: Invalid timeout values, malformed URLs, invalid retry settings.
        """

    class ConnectionError(FlextWebError):
        """Exception raised for network connectivity problems.

        Examples: DNS failures, connection refused, network unreachable.
        """

    class TimeoutError(FlextWebError):
        """Exception raised for request timeout scenarios.

        Examples: Read timeouts, connection timeouts, overall request timeouts.
        """

    class ValidationError(FlextWebError):
        """Exception raised for request/response validation failures.

        Examples: Invalid headers, malformed JSON, schema validation errors.
        """

        def __init__(self, message: str, **kwargs: object) -> None:
            """Initialize validation error with 400 status code."""
            super().__init__(message, status_code=400, **kwargs)

    class NotFoundError(FlextWebError):
        """Exception raised for HTTP 404 and resource not found errors.

        Examples: Invalid endpoints, deleted resources, moved URLs.
        """

        def __init__(self, message: str, **kwargs: object) -> None:
            """Initialize not found error with 404 status code."""
            super().__init__(message, status_code=404, **kwargs)

    class AuthenticationError(FlextWebError):
        """Exception raised for HTTP authentication failures.

        Examples: Invalid credentials, missing tokens, expired authentication.
        """

        def __init__(self, message: str, **kwargs: object) -> None:
            """Initialize authentication error with 401 status code."""
            super().__init__(message, status_code=401, **kwargs)

    class AuthorizationError(FlextWebError):
        """Exception raised for HTTP authorization failures.

        Examples: Insufficient permissions, role violations, scope limitations.
        """

        def __init__(self, message: str, **kwargs: object) -> None:
            """Initialize authorization error with 403 status code."""
            super().__init__(message, status_code=403, **kwargs)

    class RateLimitError(FlextWebError):
        """Exception raised for HTTP rate limiting.

        Examples: Too many requests, quota exceeded, throttling.
        """

        def __init__(self, message: str, **kwargs: object) -> None:
            """Initialize rate limit error with 429 status code."""
            super().__init__(message, status_code=429, **kwargs)


__all__ = ["FlextApiExceptions"]
