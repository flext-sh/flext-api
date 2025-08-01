"""API service exception hierarchy using flext-core DRY patterns.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

Domain-specific exceptions using factory pattern to eliminate duplication.
SOLID REFACTORING: Eliminates 50+ lines of duplicate exception code.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.exceptions import create_module_exception_classes

if TYPE_CHECKING:
    # For type checking, import the actual base types
    from flext_core.exceptions import (
        FlextAuthenticationError as FlextApiAuthenticationError,
        FlextConfigurationError as FlextApiConfigurationError,
        FlextConnectionError as FlextApiConnectionError,
        FlextError as FlextApiError,
        FlextProcessingError as FlextApiProcessingError,
        FlextTimeoutError as FlextApiTimeoutError,
        FlextValidationError as FlextApiValidationError,
    )
else:
    # Create all standard exception classes using factory pattern - eliminates 50+ lines
    api_exceptions = create_module_exception_classes("flext_api")

    # Import generated classes for clean usage
    FlextApiError = api_exceptions["FlextApiError"]
    FlextApiValidationError = api_exceptions["FlextApiValidationError"]
    FlextApiConfigurationError = api_exceptions["FlextApiConfigurationError"]
    FlextApiConnectionError = api_exceptions["FlextApiConnectionError"]
    FlextApiProcessingError = api_exceptions["FlextApiProcessingError"]
    FlextApiAuthenticationError = api_exceptions["FlextApiAuthenticationError"]
    FlextApiTimeoutError = api_exceptions["FlextApiTimeoutError"]


# Domain-specific exceptions unique to API service
class FlextApiRequestError(FlextApiError):
    """API service request errors with request-specific context."""

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
        if endpoint is not None:
            context["endpoint"] = endpoint
        if status_code is not None:
            context["status_code"] = status_code

        super().__init__(f"API request: {message}", context=context)


class FlextApiResponseError(FlextApiError):
    """API service response errors with response-specific context."""

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
    """API service storage errors with storage-specific context."""

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
    """API service builder errors with builder-specific context."""

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
