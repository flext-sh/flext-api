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
    FlextAuthenticationError as FlextApiAuthenticationError,
    FlextConfigurationError as FlextApiConfigurationError,
    FlextConnectionError as FlextApiConnectionError,
    FlextError as FlextApiError,
    FlextProcessingError as FlextApiProcessingError,
    FlextTimeoutError as FlextApiTimeoutError,
    FlextValidationError as FlextApiValidationError,
)

# else:
#     api_exceptions = create_module_exception_classes("flext_api")
#
#     # Import generated classes for clean usage
#     FlextApiError = api_exceptions["FlextApiError"]
#     _FactoryFlextApiValidationError = api_exceptions["FlextApiValidationError"]
#     FlextApiConfigurationError = api_exceptions["FlextApiConfigurationError"]
#     FlextApiConnectionError = api_exceptions["FlextApiConnectionError"]
#     FlextApiProcessingError = api_exceptions["FlextApiProcessingError"]
#     FlextApiAuthenticationError = api_exceptions["FlextApiAuthenticationError"]
#     FlextApiTimeoutError = api_exceptions["FlextApiTimeoutError"]
#
#     # COMPATIBILITY FIX: Add validation_details interface for tests
#     class FlextApiValidationError(_FactoryFlextApiValidationError):
#         """Enhanced validation error with test-compatible validation_details."""
#
#         @property
#         def validation_details(self) -> dict[str, str]:
#             """Compatibility property mapping to factory-generated attributes."""
#             details = {}
#             if hasattr(self, "field") and self.field is not None:
#                 details["field"] = str(self.field)
#             if hasattr(self, "value") and self.value is not None:
#                 # Truncate long values as tests expect
#                 value_str = str(self.value)
#                 details["value"] = (
#                     value_str[:100] if len(value_str) > 100 else value_str
#                 )
#             return details


# Domain-specific exceptions using DRY patterns - eliminates 18-line duplication
# SOLID REFACTORING: Simplified approach using inheritance with context building


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

        super().__init__(f"API request: {message}", context=context_dict)


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
        super().__init__(f"API response: {message}", context=context)


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
        super().__init__(f"API storage: {message}", context=context)


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
        super().__init__(f"API builder: {message}", context=context)


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
