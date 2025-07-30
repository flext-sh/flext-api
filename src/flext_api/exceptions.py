"""API service exception hierarchy using flext-core patterns.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

Domain-specific exceptions for API service operations inheriting from flext-core.
"""

from __future__ import annotations

from flext_core.exceptions import (
    FlextAuthenticationError,
    FlextConfigurationError,
    FlextConnectionError,
    FlextError,
    FlextProcessingError,
    FlextTimeoutError,
    FlextValidationError,
)


class FlextApiError(FlextError):
    """Base exception for API service operations."""

    def __init__(
        self,
        message: str = "API service error",
        endpoint: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize API service error with context."""
        context = kwargs.copy()
        if endpoint is not None:
            context["endpoint"] = endpoint

        super().__init__(message, error_code="API_SERVICE_ERROR", context=context)


class FlextApiValidationError(FlextValidationError):
    """API service validation errors."""

    def __init__(
        self,
        message: str = "API validation failed",
        field: str | None = None,
        value: object = None,
        endpoint: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize API validation error with context."""
        validation_details: dict[str, object] = {}
        if field is not None:
            validation_details["field"] = field
        if value is not None:
            validation_details["value"] = str(value)[:100]  # Truncate long values

        context = kwargs.copy()
        if endpoint is not None:
            context["endpoint"] = endpoint

        super().__init__(
            f"API validation: {message}",
            validation_details=validation_details,
            context=context,
        )


class FlextApiAuthenticationError(FlextAuthenticationError):
    """API service authentication errors."""

    def __init__(
        self,
        message: str = "API authentication failed",
        auth_method: str | None = None,
        endpoint: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize API authentication error with context."""
        context = kwargs.copy()
        if auth_method is not None:
            context["auth_method"] = auth_method
        if endpoint is not None:
            context["endpoint"] = endpoint

        super().__init__(f"API auth: {message}", **context)


class FlextApiConfigurationError(FlextConfigurationError):
    """API service configuration errors."""

    def __init__(
        self,
        message: str = "API configuration error",
        config_key: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize API configuration error with context."""
        context = kwargs.copy()
        if config_key is not None:
            context["config_key"] = config_key

        super().__init__(f"API config: {message}", **context)


class FlextApiConnectionError(FlextConnectionError):
    """API service connection errors."""

    def __init__(
        self,
        message: str = "API connection failed",
        host: str | None = None,
        port: int | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize API connection error with context."""
        context = kwargs.copy()
        if host is not None:
            context["host"] = host
        if port is not None:
            context["port"] = port

        super().__init__(f"API connection: {message}", **context)


class FlextApiProcessingError(FlextProcessingError):
    """API service processing errors."""

    def __init__(
        self,
        message: str = "API processing failed",
        operation: str | None = None,
        endpoint: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize API processing error with context."""
        context = kwargs.copy()
        if operation is not None:
            context["operation"] = operation
        if endpoint is not None:
            context["endpoint"] = endpoint

        super().__init__(f"API processing: {message}", **context)


class FlextApiTimeoutError(FlextTimeoutError):
    """API service timeout errors."""

    def __init__(
        self,
        message: str = "API operation timed out",
        endpoint: str | None = None,
        timeout_seconds: float | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize API timeout error with context."""
        context = kwargs.copy()
        if endpoint is not None:
            context["endpoint"] = endpoint
        if timeout_seconds is not None:
            context["timeout_seconds"] = timeout_seconds

        super().__init__(f"API timeout: {message}", **context)


class FlextApiRequestError(FlextApiError):
    """API service request errors."""

    def __init__(
        self,
        message: str = "API request error",
        method: str | None = None,
        endpoint: str | None = None,
        status_code: int | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize API request error with context."""
        context = kwargs.copy()
        if method is not None:
            context["method"] = method
        if status_code is not None:
            context["status_code"] = status_code

        super().__init__(f"API request: {message}", endpoint=endpoint, **context)


class FlextApiResponseError(FlextApiError):
    """API service response errors."""

    def __init__(
        self,
        message: str = "API response error",
        status_code: int | None = None,
        response_body: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize API response error with context."""
        context = kwargs.copy()
        if status_code is not None:
            context["status_code"] = status_code
        if response_body is not None:
            context["response_body"] = response_body[:200]  # Truncate long responses

        super().__init__(f"API response: {message}", context=context)


class FlextApiStorageError(FlextApiError):
    """API service storage errors."""

    def __init__(
        self,
        message: str = "API storage error",
        storage_type: str | None = None,
        operation: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize API storage error with context."""
        context = kwargs.copy()
        if storage_type is not None:
            context["storage_type"] = storage_type
        if operation is not None:
            context["operation"] = operation

        super().__init__(f"API storage: {message}", context=context)


class FlextApiBuilderError(FlextApiError):
    """API service builder errors."""

    def __init__(
        self,
        message: str = "API builder error",
        builder_step: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize API builder error with context."""
        context = kwargs.copy()
        if builder_step is not None:
            context["builder_step"] = builder_step

        super().__init__(f"API builder: {message}", context=context)


__all__ = [
    "FlextApiAuthenticationError",
    "FlextApiBuilderError",
    "FlextApiConfigurationError",
    "FlextApiConnectionError",
    "FlextApiError",
    "FlextApiProcessingError",
    "FlextApiRequestError",
    "FlextApiResponseError",
    "FlextApiStorageError",
    "FlextApiTimeoutError",
    "FlextApiValidationError",
]
