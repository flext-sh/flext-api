"""FLEXT API Exceptions - Enhanced exception hierarchy following PEP8 standards.

Enhanced exception module providing API-specific exception hierarchy built on
FLEXT ecosystem error handling patterns. Includes comprehensive error context,
HTTP status code mapping, and structured error responses.

Architecture:
    FlextError (flext-core) → FlextApiError → Specific API Exceptions

Core Features:
    - Hierarchical exception structure with proper inheritance
    - HTTP status code mapping for REST API responses
    - Detailed error context with API-specific information
    - Structured error responses for API consistency

Design Patterns:
    - Exception Hierarchy: Clear inheritance from flext-core base classes
    - Context Preservation: Rich error context for debugging
    - Status Code Mapping: HTTP status code integration
    - Error Response Building: Consistent API error responses

Usage:
    from flext_api.api_exceptions import FlextApiValidationError

    # Raise with context
    raise FlextApiValidationError(
        "Invalid email format",
        field="email",
        value=email_value,
        endpoint="/api/users"
    )

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.exceptions import (
    FlextAuthenticationError,
    FlextConfigurationError,
    FlextConnectionError,
    FlextError,
    FlextProcessingError,
    FlextTimeoutError,
    FlextValidationError,
)

if TYPE_CHECKING:
    from flext_core import FlextTypes

# ==============================================================================
# BASE API ERROR
# ==============================================================================


class FlextApiError(FlextError):
    """Base API error inheriting from FlextError with HTTP status code support."""

    def __init__(
        self,
        message: str = "flext_api error",
        *,
        status_code: int = 500,
        error_code: str = "FLEXT_API_ERROR",
        **context: object,
    ) -> None:
        """Initialize with message, status code, and context."""
        self.status_code = status_code
        context["status_code"] = status_code
        super().__init__(message, error_code=error_code, context=context)

    def to_http_response(self) -> FlextTypes.Core.JsonDict:
        """Convert exception to HTTP response format."""
        return {
            "success": False,
            "error": {
                "code": self.error_code,
                "message": str(self),
                "status_code": self.status_code,
                "context": self.context,
            },
            "data": None,
        }


# ==============================================================================
# SPECIFIC API ERRORS - INHERIT FROM FLEXT-CORE BASE CLASSES
# ==============================================================================


class FlextApiValidationError(FlextValidationError):
    """Validation error in API with field-specific context."""

    def __init__(
        self,
        message: str = "API validation failed",
        *,
        field: str | None = None,
        value: object = None,
        endpoint: str | None = None,
        status_code: int = 400,
        **context: object,
    ) -> None:
        """Initialize validation error with field and value context."""
        self.status_code = status_code

        # Prepare validation details
        validation_details: dict[str, object] = {}
        if field is not None:
            validation_details["field"] = field
        if value is not None:
            # Truncate long values for security and readability
            str_value = str(value)
            validation_details["value"] = (
                str_value[:100] if len(str_value) > 100 else str_value
            )

        # Add endpoint to general context
        if endpoint is not None:
            context["endpoint"] = endpoint
            context["status_code"] = status_code

        super().__init__(
            message,
            validation_details=validation_details,
            context=context,
        )

    def to_http_response(self) -> FlextTypes.Core.JsonDict:
        """Convert to HTTP validation error response."""
        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": str(self),
                "status_code": self.status_code,
                "validation_details": getattr(self, "validation_details", {}),
                "context": self.context,
            },
            "data": None,
        }


class FlextApiAuthenticationError(FlextAuthenticationError):
    """Authentication error in API with auth method context."""

    def __init__(
        self,
        message: str = "flext_api authentication failed",
        *,
        auth_method: str | None = None,
        endpoint: str | None = None,
        token_type: str | None = None,
        status_code: int = 401,
        **context: object,
    ) -> None:
        """Initialize authentication error with auth method context."""
        self.status_code = status_code

        if auth_method is not None:
            context["auth_method"] = auth_method
        if endpoint is not None:
            context["endpoint"] = endpoint
        if token_type is not None:
            context["token_type"] = token_type
        context["status_code"] = status_code

        # Format message to include flext_api prefix for test compatibility
        formatted_message = (
            f"flext_api: {message}" if not message.startswith("flext_api:") else message
        )
        super().__init__(
            formatted_message,
            service="flext_api",
            user_id=None,
            **context,
        )

    def to_http_response(self) -> FlextTypes.Core.JsonDict:
        """Convert to HTTP authentication error response."""
        return {
            "success": False,
            "error": {
                "code": "AUTHENTICATION_ERROR",
                "message": str(self),
                "status_code": self.status_code,
                "context": self.context,
            },
            "data": None,
        }


class FlextApiAuthorizationError(FlextApiError):
    """Authorization error for insufficient permissions."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        *,
        required_permission: str | None = None,
        user_permissions: list[str] | None = None,
        endpoint: str | None = None,
        **context: object,
    ) -> None:
        """Initialize authorization error with permission context."""
        if required_permission is not None:
            context["required_permission"] = required_permission
        if user_permissions is not None:
            context["user_permissions"] = user_permissions
        if endpoint is not None:
            context["endpoint"] = endpoint

        super().__init__(
            f"Authorization: {message}",
            status_code=403,
            error_code="FLEXT_API_ERROR",
            **context,
        )


class FlextApiConfigurationError(FlextConfigurationError):
    """Configuration error in API with config key context."""

    def __init__(
        self,
        message: str = "API configuration error",
        *,
        config_key: str | None = None,
        expected_type: str | None = None,
        actual_value: object = None,
        status_code: int = 500,
        **context: object,
    ) -> None:
        """Initialize configuration error with config context."""
        self.status_code = status_code

        if expected_type is not None:
            context["expected_type"] = expected_type
        if actual_value is not None:
            context["actual_value"] = str(actual_value)
        context["status_code"] = status_code

        super().__init__(
            message,
            config_key=config_key,
            config_file=None,
            **context,
        )

        # Ensure config_key is in context for test compatibility
        if config_key is not None and "config_key" not in self.context:
            self.context["config_key"] = config_key

    def to_http_response(self) -> FlextTypes.Core.JsonDict:
        """Convert to HTTP configuration error response."""
        return {
            "success": False,
            "error": {
                "code": "CONFIGURATION_ERROR",
                "message": str(self),
                "status_code": self.status_code,
                "context": self.context,
            },
            "data": None,
        }


class FlextApiConnectionError(FlextConnectionError):
    """Connection error in API with network context."""

    def __init__(
        self,
        message: str = "API connection error",
        *,
        host: str | None = None,
        port: int | None = None,
        ssl_error: str | None = None,
        connection_timeout: float | None = None,
        status_code: int = 503,
        **context: object,
    ) -> None:
        """Initialize connection error with network context."""
        self.status_code = status_code

        if host is not None:
            context["host"] = host
        if port is not None:
            context["port"] = port
        if ssl_error is not None:
            context["ssl_error"] = ssl_error
        if connection_timeout is not None:
            context["connection_timeout"] = connection_timeout
        context["status_code"] = status_code

        super().__init__(
            message,
            service="flext_api_connection",
            endpoint=None,
            **context,
        )

    def to_http_response(self) -> FlextTypes.Core.JsonDict:
        """Convert to HTTP connection error response."""
        return {
            "success": False,
            "error": {
                "code": "CONNECTION_ERROR",
                "message": str(self),
                "status_code": self.status_code,
                "context": self.context,
            },
            "data": None,
        }


class FlextApiProcessingError(FlextProcessingError):
    """Processing error in API with operation context."""

    def __init__(
        self,
        message: str = "API processing error",
        *,
        operation: str | None = None,
        endpoint: str | None = None,
        processing_stage: str | None = None,
        status_code: int = 500,
        **context: object,
    ) -> None:
        """Initialize processing error with operation context."""
        self.status_code = status_code

        if operation is not None:
            context["operation"] = operation
        if endpoint is not None:
            context["endpoint"] = endpoint
        if processing_stage is not None:
            context["processing_stage"] = processing_stage
        context["status_code"] = status_code

        super().__init__(
            message,
            business_rule="flext_api_processing",
            operation=operation,
            **context,
        )

    def to_http_response(self) -> FlextTypes.Core.JsonDict:
        """Convert to HTTP processing error response."""
        return {
            "success": False,
            "error": {
                "code": "PROCESSING_ERROR",
                "message": str(self),
                "status_code": self.status_code,
                "context": self.context,
            },
            "data": None,
        }


class FlextApiTimeoutError(FlextTimeoutError):
    """Timeout error in API with timeout context."""

    def __init__(
        self,
        message: str = "API timeout error",
        *,
        endpoint: str | None = None,
        timeout_seconds: float | None = None,
        query_type: str | None = None,
        operation: str | None = None,
        status_code: int = 504,
        **context: object,
    ) -> None:
        """Initialize timeout error with timeout context."""
        self.status_code = status_code

        if endpoint is not None:
            context["endpoint"] = endpoint
        if timeout_seconds is not None:
            context["timeout_seconds"] = timeout_seconds
        if query_type is not None:
            context["query_type"] = query_type
        if operation is not None:
            context["operation"] = operation
        context["status_code"] = status_code

        super().__init__(
            message,
            service="flext_api_service",
            timeout_seconds=int(timeout_seconds) if timeout_seconds is not None else None,
            **context,
        )

    def to_http_response(self) -> FlextTypes.Core.JsonDict:
        """Convert to HTTP timeout error response."""
        return {
            "success": False,
            "error": {
                "code": "TIMEOUT_ERROR",
                "message": str(self),
                "status_code": self.status_code,
                "context": self.context,
            },
            "data": None,
        }


# ==============================================================================
# API-SPECIFIC ERRORS - INHERIT FROM BASE FlextApiError
# ==============================================================================


class FlextApiRequestError(FlextApiError):
    """API request errors with HTTP method and endpoint context."""

    def __init__(
        self,
        message: str = "API request error",
        *,
        method: str | None = None,
        endpoint: str | None = None,
        status_code: int = 400,
        request_id: str | None = None,
        **context: object,
    ) -> None:
        """Initialize with API request context."""
        if method is not None:
            context["method"] = method
        if endpoint is not None:
            context["endpoint"] = endpoint
        if request_id is not None:
            context["request_id"] = request_id

        super().__init__(
            f"API request: {message}",
            status_code=status_code,
            error_code="FLEXT_API_ERROR",
            **context,
        )


class FlextApiResponseError(FlextApiError):
    """API response errors with response context."""

    def __init__(
        self,
        message: str = "API response error",
        *,
        status_code: int = 502,
        response_body: str | None = None,
        content_type: str | None = None,
        **context: object,
    ) -> None:
        """Initialize with API response context."""
        if response_body is not None:
            # Limit response body size for security and readability
            context["response_body"] = str(response_body)[:200]
        if content_type is not None:
            context["content_type"] = content_type

        super().__init__(
            f"API response: {message}",
            status_code=status_code,
            error_code="FLEXT_API_ERROR",
            **context,
        )


class FlextApiStorageError(FlextApiError):
    """API storage errors with storage context."""

    def __init__(
        self,
        message: str = "API storage error",
        *,
        storage_type: str | None = None,
        operation: str | None = None,
        pool_size: int | None = None,
        active_connections: int | None = None,
        status_code: int = 500,
        **context: object,
    ) -> None:
        """Initialize with API storage context."""
        if storage_type is not None:
            context["storage_type"] = storage_type
        if operation is not None:
            context["operation"] = operation
        if pool_size is not None:
            context["pool_size"] = pool_size
        if active_connections is not None:
            context["active_connections"] = active_connections

        super().__init__(
            f"API storage: {message}",
            status_code=status_code,
            error_code="FLEXT_API_ERROR",
            **context,
        )


class FlextApiBuilderError(FlextApiError):
    """API builder errors with builder context."""

    def __init__(
        self,
        message: str = "API builder error",
        *,
        builder_step: str | None = None,
        expected_type: str | None = None,
        actual_value: str | None = None,
        builder_type: str | None = None,
        status_code: int = 400,
        **context: object,
    ) -> None:
        """Initialize with API builder context."""
        if builder_step is not None:
            context["builder_step"] = builder_step
        if expected_type is not None:
            context["expected_type"] = expected_type
        if actual_value is not None:
            context["actual_value"] = actual_value
        if builder_type is not None:
            context["builder_type"] = builder_type

        super().__init__(
            f"API builder: {message}",
            status_code=status_code,
            error_code="FLEXT_API_ERROR",
            **context,
        )


class FlextApiRateLimitError(FlextApiError):
    """API rate limiting errors."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        *,
        limit: int | None = None,
        window_seconds: int | None = None,
        retry_after: int | None = None,
        endpoint: str | None = None,
        **context: object,
    ) -> None:
        """Initialize with rate limiting context."""
        if limit is not None:
            context["limit"] = limit
        if window_seconds is not None:
            context["window_seconds"] = window_seconds
        if retry_after is not None:
            context["retry_after"] = retry_after
        if endpoint is not None:
            context["endpoint"] = endpoint

        super().__init__(
            f"Rate limit: {message}",
            status_code=429,
            error_code="FLEXT_API_ERROR",
            **context,
        )


class FlextApiNotFoundError(FlextApiError):
    """API resource not found errors."""

    def __init__(
        self,
        message: str = "Resource not found",
        *,
        resource_type: str | None = None,
        resource_id: str | None = None,
        endpoint: str | None = None,
        **context: object,
    ) -> None:
        """Initialize with resource context."""
        if resource_type is not None:
            context["resource_type"] = resource_type
        if resource_id is not None:
            context["resource_id"] = resource_id
        if endpoint is not None:
            context["endpoint"] = endpoint

        super().__init__(
            f"Not found: {message}",
            status_code=404,
            error_code="FLEXT_API_ERROR",
            **context,
        )


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================


def create_error_response(
    exception: FlextApiError,
    include_traceback: bool = False,
) -> FlextTypes.Core.JsonDict:
    """Create standardized error response from exception."""
    response = exception.to_http_response()

    if include_traceback:
        import traceback

        error_dict = response["error"]
        if isinstance(error_dict, dict):
            error_dict["traceback"] = traceback.format_exc()

    return response


def _get_specific_exception(
    status_code: int, message: str,
) -> (
    FlextApiError
    | FlextApiAuthenticationError
    | FlextApiProcessingError
    | FlextApiConnectionError
    | FlextApiTimeoutError
    | None
):
    """Get specific exception for known status codes."""
    specific_exceptions: dict[
        int,
        FlextApiError
        | FlextApiAuthenticationError
        | FlextApiProcessingError
        | FlextApiConnectionError
        | FlextApiTimeoutError,
    ] = {
        400: FlextApiRequestError(message or "Bad request", status_code=status_code),
        401: FlextApiAuthenticationError(message or "Unauthorized", status_code=status_code),
        403: FlextApiAuthorizationError(message or "Forbidden"),
        404: FlextApiNotFoundError(message or "Not found"),
        429: FlextApiRateLimitError(message or "Too many requests"),
        500: FlextApiProcessingError(message or "Internal server error", status_code=status_code),
        502: FlextApiResponseError(message or "Bad gateway", status_code=status_code),
        503: FlextApiConnectionError(message or "Service unavailable", status_code=status_code),
        504: FlextApiTimeoutError(message or "Gateway timeout", status_code=status_code),
    }
    return specific_exceptions.get(status_code)


def map_http_status_to_exception(
    status_code: int,
    message: str = "",
    **context: object,
) -> (
    FlextApiError
    | FlextApiAuthenticationError
    | FlextApiProcessingError
    | FlextApiConnectionError
    | FlextApiTimeoutError
):
    """Map HTTP status code to appropriate exception type."""
    # Try specific exception first
    specific_exception = _get_specific_exception(status_code, message)
    if specific_exception is not None:
        return specific_exception

    # Range-based fallbacks
    if 400 <= status_code < 500:
        return FlextApiRequestError(message or "Client error", status_code=status_code)

    if 500 <= status_code < 600:
        return FlextApiError(
            message or "Server error",
            status_code=status_code,
            error_code="FLEXT_API_ERROR",
            **context,
        )

    # Default fallback
    return FlextApiError(
        message or "Unknown error",
        status_code=status_code,
        error_code="FLEXT_API_ERROR",
        **context,
    )


# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    "FlextApiAuthenticationError",
    "FlextApiAuthorizationError",
    "FlextApiBuilderError",
    "FlextApiConfigurationError",
    "FlextApiConnectionError",
    # Base Error
    "FlextApiError",
    "FlextApiNotFoundError",
    "FlextApiProcessingError",
    "FlextApiRateLimitError",
    # Specific API Errors
    "FlextApiRequestError",
    "FlextApiResponseError",
    "FlextApiStorageError",
    "FlextApiTimeoutError",
    # Core API Errors
    "FlextApiValidationError",
    # Utility Functions
    "create_error_response",
    "map_http_status_to_exception",
]
