"""Legacy compatibility module for FLEXT API library.

This module provides backward compatibility facades for deprecated API patterns.
All functions and classes in this module are deprecated and will be removed
in future versions. Use the modern API patterns instead.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from flext_core import get_logger

from flext_api.builder import (
    FlextApiBuilder,
    FlextApiQuery,
)
from flext_api.client import FlextApiClient, FlextApiClientConfig
from flext_api.exceptions import (
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

if TYPE_CHECKING:
    from flext_core import FlextTypes

logger = get_logger(__name__)

# ==============================================================================
# DEPRECATED CONSTANTS
# ==============================================================================

# Legacy HTTP status codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_SERVER_ERROR = 500

# Legacy defaults
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_PAGE_SIZE = 20

# ==============================================================================
# DEPRECATED FUNCTIONS
# ==============================================================================


def create_client(
    base_url: str,
    timeout: float = DEFAULT_TIMEOUT,
    headers: dict[str, str] | None = None,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> FlextApiClient:
    """Create HTTP client (DEPRECATED).

    DEPRECATED: Use FlextApi.create_client() or create_flext_api().create_client()

    Args:
        base_url: Base URL for requests
        timeout: Request timeout in seconds
        headers: Default headers
        max_retries: Maximum retry attempts

    Returns:
        FlextApiClient instance

    """
    warnings.warn(
        "create_client() is deprecated. Use FlextApi.create_client() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    config = FlextApiClientConfig(
        base_url=base_url,
        timeout=timeout,
        headers=headers or {},
        max_retries=max_retries,
    )
    return FlextApiClient(config)


def create_builder() -> FlextApiBuilder:
    """Create API builder (DEPRECATED).

    DEPRECATED: Use FlextApi.get_builder() or create_flext_api().get_builder()

    Returns:
        FlextApiBuilder instance

    """
    warnings.warn(
        "create_builder() is deprecated. Use FlextApi.get_builder() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return FlextApiBuilder()


def build_query(
    filters: list[FlextTypes.Core.JsonDict] | None = None,
    sorts: list[dict[str, str]] | None = None,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> FlextApiQuery:
    """Build API query (DEPRECATED).

    DEPRECATED: Use FlextApiQueryBuilder or FlextApi.get_query_builder()

    Args:
        filters: Filter criteria
        sorts: Sort criteria
        page: Page number
        page_size: Page size

    Returns:
        FlextApiQuery instance

    """
    warnings.warn(
        "build_query() is deprecated. Use FlextApiQueryBuilder instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return FlextApiQuery(
        filters=filters or [],
        sorts=sorts or [],
        page=page,
        page_size=page_size,
    )


def build_response(
    success: bool,
    data: object = None,
    message: str | None = None,
    error: str | None = None,
    metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build API response (DEPRECATED).

    DEPRECATED: Use FlextApiResponseBuilder or FlextApi.get_response_builder()

    Args:
        success: Success status
        data: Response data
        message: Response message
        error: Error message
        metadata: Response metadata

    Returns:
        Response dictionary

    """
    warnings.warn(
        "build_response() is deprecated. Use FlextApiResponseBuilder instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    response = {
        "success": success,
        "data": data,
    }

    if message:
        response["message"] = message
    if error:
        response["error"] = error
    if metadata:
        response["metadata"] = metadata

    return response


def validate_request(request: dict[str, object]) -> bool:
    """Validate API request (DEPRECATED).

    DEPRECATED: Use ApiRequest.validate_business_rules() instead

    Args:
        request: Request dictionary

    Returns:
        True if valid, False otherwise

    """
    warnings.warn(
        "validate_request() is deprecated. "
        "Use ApiRequest.validate_business_rules() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    # Basic validation
    if not request:
        return False

    if "method" not in request or "url" not in request:
        return False

    method_val = request.get("method", "")
    method = str(method_val).upper() if method_val else "GET"
    if method not in {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}:
        return False

    url = request.get("url", "")
    return not (not url or not isinstance(url, str))


def parse_error_response(response: dict[str, object]) -> str:
    """Parse error from response (DEPRECATED).

    DEPRECATED: Use ApiResponse.error_message directly

    Args:
        response: Response dictionary

    Returns:
        Error message string

    """
    warnings.warn(
        "parse_error_response() is deprecated. Use ApiResponse.error_message instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    if "error" in response:
        return str(response["error"])

    if "message" in response and not response.get("success", True):
        return str(response["message"])

    if "errors" in response and isinstance(response["errors"], list):
        return "; ".join(str(e) for e in response["errors"])

    return "Unknown error"


# ==============================================================================
# DEPRECATED CLASSES
# ==============================================================================


class LegacyApiClient:
    """Legacy API client wrapper (DEPRECATED).

    DEPRECATED: Use FlextApiClient directly
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = DEFAULT_TIMEOUT,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Initialize legacy client."""
        warnings.warn(
            "LegacyApiClient is deprecated. Use FlextApiClient instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        config = FlextApiClientConfig(
            base_url=base_url,
            timeout=timeout,
            headers=headers or {},
            max_retries=DEFAULT_MAX_RETRIES,
        )
        self._client = FlextApiClient(config)

    def get(self, _endpoint: str, **_kwargs: object) -> dict[str, object]:
        """Make GET request (sync wrapper)."""
        warnings.warn(
            "Synchronous methods are deprecated. Use async methods instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        # This would need asyncio.run() in real implementation
        msg = "Use async client methods instead"
        raise NotImplementedError(msg)

    def post(
        self,
        _endpoint: str,
        _data: object = None,
        **_kwargs: object,
    ) -> dict[str, object]:
        """Make POST request (sync wrapper)."""
        warnings.warn(
            "Synchronous methods are deprecated. Use async methods instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        msg = "Use async client methods instead"
        raise NotImplementedError(msg)


class LegacyApiBuilder:
    """Legacy API builder wrapper (DEPRECATED).

    DEPRECATED: Use FlextApiBuilder directly
    """

    def __init__(self) -> None:
        """Initialize legacy builder."""
        warnings.warn(
            "LegacyApiBuilder is deprecated. Use FlextApiBuilder instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._builder = FlextApiBuilder()

    def with_query(
        self,
        _filters: list[FlextTypes.Core.JsonDict] | None = None,
        _sorts: list[dict[str, str]] | None = None,
    ) -> LegacyApiBuilder:
        """Build query (DEPRECATED)."""
        warnings.warn(
            "with_query() is deprecated. Use FlextApiQueryBuilder instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        # This is just a facade - use modern builder
        return self

    def with_response(
        self,
        _success: bool,
        _data: object = None,
    ) -> LegacyApiBuilder:
        """Build response (DEPRECATED)."""
        warnings.warn(
            "with_response() is deprecated. Use FlextApiResponseBuilder instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self

    def build(self) -> dict[str, object]:
        """Build result (DEPRECATED)."""
        return {"deprecated": True}


# ==============================================================================
# DEPRECATED EXCEPTIONS (Already in exceptions.py, just aliases here)
# ==============================================================================

# These are re-exported for backward compatibility
ApiError = FlextApiError
ApiValidationError = FlextApiValidationError
ApiConfigurationError = FlextApiConfigurationError
ApiConnectionError = FlextApiConnectionError
ApiProcessingError = FlextApiProcessingError
ApiAuthenticationError = FlextApiAuthenticationError
ApiTimeoutError = FlextApiTimeoutError
ApiRequestError = FlextApiRequestError
ApiResponseError = FlextApiResponseError
ApiStorageError = FlextApiStorageError
ApiBuilderError = FlextApiBuilderError


# ==============================================================================
# MIGRATION HELPERS
# ==============================================================================


def migrate_to_modern_api(old_code: str) -> str:
    """Show migration path (documentation only).

    Args:
        old_code: Example of old API usage

    Returns:
        String showing modern equivalent

    """
    migrations = {
        "create_client(": "FlextApi.create_client(",
        "create_builder(": "FlextApi.get_builder(",
        "build_query(": "FlextApiQueryBuilder(",
        "build_response(": "FlextApiResponseBuilder(",
        "LegacyApiClient(": "FlextApiClient(",
        "LegacyApiBuilder(": "FlextApiBuilder(",
        "ApiError": "FlextApiError",
        "validate_request(": "ApiRequest.validate_business_rules(",
        "parse_error_response(": "ApiResponse.error_message",
    }

    result: list[str] = []
    result.extend(
        (
            "# Old pattern (DEPRECATED):",
            old_code,
            "",
            "# Modern pattern (RECOMMENDED):",
        ),
    )

    modern_code = old_code
    for old, new in migrations.items():
        modern_code = modern_code.replace(old, new)

    result.append(modern_code)
    return "\n".join(result)


# ==============================================================================
# COMPATIBILITY WARNINGS
# ==============================================================================


def _emit_deprecation_warning() -> None:
    """Emit deprecation warning when module is imported."""
    warnings.warn(
        "The flext_api.legacy module is deprecated and will be removed in v2.0.0. "
        "Please migrate to the modern API patterns. "
        "See migration guide at: https://github.com/flext-sh/flext/blob/main/docs/migration.md",
        DeprecationWarning,
        stacklevel=2,
    )


# Emit warning on import
_emit_deprecation_warning()


# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_PAGE_SIZE",
    "DEFAULT_TIMEOUT",
    "HTTP_BAD_REQUEST",
    "HTTP_CREATED",
    "HTTP_FORBIDDEN",
    "HTTP_INTERNAL_SERVER_ERROR",
    "HTTP_NOT_FOUND",
    # Deprecated constants
    "HTTP_OK",
    "HTTP_UNAUTHORIZED",
    "ApiAuthenticationError",
    "ApiBuilderError",
    "ApiConfigurationError",
    "ApiConnectionError",
    # Deprecated exceptions (aliases)
    "ApiError",
    "ApiProcessingError",
    "ApiRequestError",
    "ApiResponseError",
    "ApiStorageError",
    "ApiTimeoutError",
    "ApiValidationError",
    "LegacyApiBuilder",
    # Deprecated classes
    "LegacyApiClient",
    "build_query",
    "build_response",
    "create_builder",
    # Deprecated functions
    "create_client",
    # Migration helper
    "migrate_to_modern_api",
    "parse_error_response",
    "validate_request",
]
