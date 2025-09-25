"""Exception definitions for flext-api domain.

All exception classes are centralized here following FLEXT standards.
Only exception class definitions - no factory methods or utility functions.
"""

from .constants import FlextApiConstants
from .typings import FlextApiTypings

HttpStatusCode = FlextApiTypings.HttpStatusCode


class FlextApiExceptions:
    """HTTP API exception classes for flext-api domain."""

    class ValidationError(Exception):
        """HTTP validation error with status code."""

        def __init__(
            self, message: str, status_code: HttpStatusCode = 400, **_kwargs: object
        ) -> None:
            """Initialize HTTP validation error."""
            super().__init__(message)
            self.status_code = status_code

    class AuthenticationError(Exception):
        """HTTP authentication error with status code."""

        def __init__(
            self, message: str, status_code: HttpStatusCode = 401, **_kwargs: object
        ) -> None:
            """Initialize HTTP authentication error."""
            super().__init__(message)
            self.status_code = status_code

    class AuthorizationError(Exception):
        """HTTP authorization error with status code."""

        def __init__(
            self, message: str, status_code: HttpStatusCode = 403, **_kwargs: object
        ) -> None:
            """Initialize HTTP authorization error."""
            super().__init__(message)
            self.status_code = status_code

    class NotFoundError(Exception):
        """HTTP not found error with status code."""

        def __init__(
            self, message: str, status_code: HttpStatusCode = 404, **_kwargs: object
        ) -> None:
            """Initialize HTTP not found error."""
            super().__init__(message)
            self.status_code = status_code

    class ConflictError(Exception):
        """HTTP conflict error with status code."""

        def __init__(
            self, message: str, status_code: HttpStatusCode = 409, **_kwargs: object
        ) -> None:
            """Initialize HTTP conflict error."""
            super().__init__(message)
            self.status_code = status_code

    class RateLimitError(Exception):
        """HTTP rate limit error with status code."""

        def __init__(
            self, message: str, status_code: HttpStatusCode = 429, **_kwargs: object
        ) -> None:
            """Initialize HTTP rate limit error."""
            super().__init__(message)
            self.status_code = status_code

    class HttpError(Exception):
        """General HTTP error with status code and request context."""

        def __init__(
            self,
            message: str,
            status_code: HttpStatusCode = 500,
            url: str | None = None,
            method: str | None = None,
            **_kwargs: object,
        ) -> None:
            """Initialize HTTP error with request context."""
            super().__init__(message)
            self.status_code = status_code
            self.url = url
            self.method = method

    class HttpTimeoutError(Exception):
        """HTTP timeout error with status code."""

        def __init__(
            self,
            message: str,
            status_code: HttpStatusCode = 408,
            url: str | None = None,
            **_kwargs: object,
        ) -> None:
            """Initialize HTTP timeout error."""
            super().__init__(message)
            self.status_code = status_code
            self.url = url

    class ClientError(HttpError):
        """HTTP client error (4xx status codes)."""

        def __init__(
            self,
            message: str,
            status_code: HttpStatusCode = 400,
            **_kwargs: object,
        ) -> None:
            """Initialize HTTP client error."""
            if not (
                FlextApiConstants.HTTP_CLIENT_ERROR_MIN
                <= status_code
                <= FlextApiConstants.HTTP_CLIENT_ERROR_MAX
            ):
                msg = f"Client error status code must be 4xx, got {status_code}"
                raise ValueError(msg)
            super().__init__(message, status_code=status_code)

    class ServerError(HttpError):
        """HTTP server error (5xx status codes)."""

        def __init__(
            self,
            message: str,
            status_code: HttpStatusCode = 500,
            **_kwargs: object,
        ) -> None:
            """Initialize HTTP server error."""
            if not (
                FlextApiConstants.HTTP_SERVER_ERROR_MIN
                <= status_code
                <= FlextApiConstants.HTTP_SERVER_ERROR_MAX
            ):
                msg = f"Server error status code must be 5xx, got {status_code}"
                raise ValueError(msg)
            super().__init__(message, status_code=status_code)

    class BadRequestError(ClientError):
        """HTTP 400 Bad Request error."""

        def __init__(self, message: str = "Bad Request", **_kwargs: object) -> None:
            """Initialize HTTP 400 error."""
            super().__init__(message, status_code=400, **_kwargs)

    class UnauthorizedError(ClientError):
        """HTTP 401 Unauthorized error."""

        def __init__(self, message: str = "Unauthorized", **_kwargs: object) -> None:
            """Initialize HTTP 401 error."""
            super().__init__(message, status_code=401, **_kwargs)

    class ForbiddenError(ClientError):
        """HTTP 403 Forbidden error."""

        def __init__(self, message: str = "Forbidden", **_kwargs: object) -> None:
            """Initialize HTTP 403 error."""
            super().__init__(message, status_code=403, **_kwargs)

    class MethodNotAllowedError(ClientError):
        """HTTP 405 Method Not Allowed error."""

        def __init__(
            self, message: str = "Method Not Allowed", **_kwargs: object
        ) -> None:
            """Initialize HTTP 405 error."""
            super().__init__(message, status_code=405, **_kwargs)

    class RequestTimeoutError(ClientError):
        """HTTP 408 Request Timeout error."""

        def __init__(self, message: str = "Request Timeout", **_kwargs: object) -> None:
            """Initialize HTTP 408 error."""
            super().__init__(message, status_code=408, **_kwargs)

    class TooManyRequestsError(ClientError):
        """HTTP 429 Too Many Requests error."""

        def __init__(
            self, message: str = "Too Many Requests", **_kwargs: object
        ) -> None:
            """Initialize HTTP 429 error."""
            super().__init__(message, status_code=429, **_kwargs)

    class InternalServerError(ServerError):
        """HTTP 500 Internal Server Error."""

        def __init__(
            self, message: str = "Internal Server Error", **_kwargs: object
        ) -> None:
            """Initialize HTTP 500 error."""
            super().__init__(message, status_code=500, **_kwargs)

    class BadGatewayError(ServerError):
        """HTTP 502 Bad Gateway error."""

        def __init__(self, message: str = "Bad Gateway", **_kwargs: object) -> None:
            """Initialize HTTP 502 error."""
            super().__init__(message, status_code=502, **_kwargs)

    class ServiceUnavailableError(ServerError):
        """HTTP 503 Service Unavailable error."""

        def __init__(
            self, message: str = "Service Unavailable", **_kwargs: object
        ) -> None:
            """Initialize HTTP 503 error."""
            super().__init__(message, status_code=503, **_kwargs)

    class GatewayTimeoutError(ServerError):
        """HTTP 504 Gateway Timeout error."""

        def __init__(self, message: str = "Gateway Timeout", **_kwargs: object) -> None:
            """Initialize HTTP 504 error."""
            super().__init__(message, status_code=504, **_kwargs)


__all__ = ["FlextApiExceptions"]
