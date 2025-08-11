"""FLEXT API Exceptions Module.

Compatibility module that bridges to api_exceptions.py functionality.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Import specific exceptions from api_exceptions for compatibility
from flext_api.api_exceptions import (
    FlextApiAuthenticationError,
    FlextApiAuthorizationError,
    FlextApiBuilderError,
    FlextApiConfigurationError,
    FlextApiConnectionError,
    FlextApiError,
    FlextApiNotFoundError,
    FlextApiProcessingError,
    FlextApiRateLimitError,
    FlextApiRequestError,
    FlextApiResponseError,
    FlextApiStorageError,
    FlextApiTimeoutError,
    FlextApiValidationError,
    create_error_response,
    map_http_status_to_exception,
)

# Re-export all for compatibility
__all__ = [
    "FlextApiAuthenticationError",
    "FlextApiAuthorizationError",
    "FlextApiBuilderError",
    "FlextApiConfigurationError",
    "FlextApiConnectionError",
    "FlextApiError",
    "FlextApiNotFoundError",
    "FlextApiProcessingError",
    "FlextApiRateLimitError",
    "FlextApiRequestError",
    "FlextApiResponseError",
    "FlextApiStorageError",
    "FlextApiTimeoutError",
    "FlextApiValidationError",
    "create_error_response",
    "map_http_status_to_exception",
]
