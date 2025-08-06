"""API-specific exception classes.

Exception hierarchy extending flext-core exceptions with API-specific context.
Uses factory pattern to create standard exception classes and provides
specialized exceptions for requests, responses, storage, and builder operations.

Main exception classes:
    - FlextApiError: Base API exception
    - FlextApiValidationError: Input validation errors
    - FlextApiConnectionError: HTTP connection errors
    - FlextApiTimeoutError: Request timeout errors
    - FlextApiRequestError: Request-specific errors with HTTP context
    - FlextApiResponseError: Response-specific errors with status codes
    - FlextApiStorageError: Storage operation errors
    - FlextApiBuilderError: Query/response builder errors

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from dataclasses import dataclass

from flext_core.exceptions import (
    FlextAuthenticationError,
    FlextConfigurationError,
    FlextConnectionError,
    FlextError,
    FlextProcessingError,
    FlextTimeoutError,
    FlextValidationError,
)

# FLEXT API Exception Hierarchy - Following flext-core patterns
# SOLID REFACTORING: Proper inheritance with specific error codes


class FlextApiError(FlextError):
    """Base API error with proper error code."""

    def __init__(
        self,
        message: str = "flext_api error",
        **kwargs: object,
    ) -> None:
        """Initialize API error with specific error code."""
        super().__init__(
            message,
            error_code="FLEXT_API_ERROR",
            context=kwargs,
        )


class FlextApiValidationError(FlextValidationError):
    """API validation error with API-specific context."""

    def __init__(
        self,
        message: str = "API validation failed",
        *,
        field: str | None = None,
        value: object = None,
        rules: list[str] | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize API validation error following flext-core pattern."""
        # Build validation_details for flext-core FlextValidationError
        validation_details: dict[str, object] = {}
        if field is not None:
            validation_details["field"] = field
        if value is not None:
            validation_details["value"] = value
        if rules is not None:
            validation_details["rules"] = rules

        # Pass validation_details to parent FlextValidationError
        super().__init__(
            message=message,
            validation_details=validation_details,
            context=kwargs,
        )

        # Store validation_details as instance attribute for test compatibility
        # Match the base class behavior - values are stored as strings in context
        self.validation_details: dict[str, object] = {}
        if field is not None:
            self.validation_details["field"] = field
        if value is not None:
            self.validation_details["value"] = str(value)[
                :100
            ]  # Match flext-core behavior
        if rules is not None:
            self.validation_details["rules"] = rules


class FlextApiConfigurationError(FlextConfigurationError):
    """API configuration error with API-specific context."""

    def __init__(
        self,
        message: str = "API configuration error",
        **kwargs: object,
    ) -> None:
        """Initialize API configuration error."""
        super().__init__(message, **kwargs)


class FlextApiConnectionError(FlextConnectionError):
    """API connection error with API-specific context."""

    def __init__(
        self,
        message: str = "API connection error",
        **kwargs: object,
    ) -> None:
        """Initialize API connection error."""
        super().__init__(message, **kwargs)


class FlextApiProcessingError(FlextProcessingError):
    """API processing error with API-specific context."""

    def __init__(
        self,
        message: str = "API processing error",
        **kwargs: object,
    ) -> None:
        """Initialize API processing error."""
        super().__init__(message, **kwargs)


class FlextApiAuthenticationError(FlextAuthenticationError):
    """API authentication error with API-specific context."""

    def __init__(
        self,
        message: str = "flext_api authentication failed",
        **kwargs: object,
    ) -> None:
        """Initialize API authentication error."""
        super().__init__(f"flext_api: {message}", **kwargs)


class FlextApiTimeoutError(FlextTimeoutError):
    """API timeout error with API-specific context."""

    def __init__(
        self,
        message: str = "API timeout error",
        **kwargs: object,
    ) -> None:
        """Initialize API timeout error."""
        super().__init__(message, **kwargs)


# Domain-specific exceptions using DRY patterns - eliminates 18-line duplication
# SOLID REFACTORING: Simplified approach using Parameter Object pattern


@dataclass
class ApiErrorContext:
    """Parameter Object: API error context - eliminates 6-parameter constructor.

    SOLID refactoring: Reduces parameter explosion by encapsulating all API error
    context parameters in a single object with type safety.
    """

    method: str | None = None
    endpoint: str | None = None
    status_code: int | None = None
    extra_context: dict[str, object] | None = None

    def to_context_dict(self) -> dict[str, object]:
        """Convert to context dictionary for exception handling."""
        context: dict[str, object] = (
            self.extra_context.copy() if self.extra_context else {}
        )

        if self.method is not None:
            context["method"] = self.method
        if self.endpoint is not None:
            context["endpoint"] = self.endpoint
        if self.status_code is not None:
            context["status_code"] = self.status_code

        return context


class FlextApiRequestError(FlextApiError):
    """API request errors with automatic context building."""

    def __init__(
        self,
        message: str = "API request error",
        *,
        context: ApiErrorContext | None = None,
        # Backward compatibility parameters
        method: str | None = None,
        endpoint: str | None = None,
        status_code: int | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize with API request context using Parameter Object pattern."""
        if context is not None:
            # Use Parameter Object (preferred)
            context_dict = context.to_context_dict()
        else:
            # Backward compatibility: create context from individual parameters
            context = ApiErrorContext(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                extra_context=kwargs,
            )
            context_dict = context.to_context_dict()

        super().__init__(f"API request: {message}", **context_dict)


class FlextApiResponseError(FlextApiError):
    """API response errors with automatic context building."""

    def __init__(
        self,
        message: str = "API response error",
        *,
        status_code: int | None = None,
        response_body: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize with API response context."""
        context: dict[str, object] = dict(kwargs)
        if status_code is not None:
            context["status_code"] = status_code
        if response_body is not None:
            context["response_body"] = str(response_body)[:200]  # Limit size
        super().__init__(f"API response: {message}", **context)


class FlextApiStorageError(FlextApiError):
    """API storage errors with automatic context building."""

    def __init__(
        self,
        message: str = "API storage error",
        *,
        storage_type: str | None = None,
        operation: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize with API storage context."""
        context: dict[str, object] = dict(kwargs)
        if storage_type is not None:
            context["storage_type"] = storage_type
        if operation is not None:
            context["operation"] = operation
        super().__init__(f"API storage: {message}", **context)


class FlextApiBuilderError(FlextApiError):
    """API builder errors with automatic context building."""

    def __init__(
        self,
        message: str = "API builder error",
        *,
        builder_step: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize with API builder context."""
        context: dict[str, object] = dict(kwargs)
        if builder_step is not None:
            context["builder_step"] = builder_step
        super().__init__(f"API builder: {message}", **context)


__all__: list[str] = [
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
