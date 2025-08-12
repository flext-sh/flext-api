"""FLEXT API Exceptions Module.

Compatibility module that bridges to api_exceptions.py functionality.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

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
