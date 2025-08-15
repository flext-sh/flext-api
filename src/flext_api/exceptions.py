"""FLEXT API exceptions module."""

from __future__ import annotations

from flext_api.api_exceptions import (
    FlextApiAuthenticationError,
    FlextApiBuilderError,
    FlextApiConfigurationError,
    FlextApiConnectionError,
    FlextApiError,
    FlextApiProcessingError,
    FlextApiRequestError,
    FlextApiResponseError,
    FlextApiStorageError,
    FlextApiTimeoutError,
    FlextApiValidationError,
)

# Re-export only the exceptions expected by tests
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
