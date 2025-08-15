"""FLEXT API builder module."""

from __future__ import annotations

from flext_api.api_client import (
    FlextApiBuilder,
    FlextApiQuery,
    FlextApiQueryBuilder,
    FlextApiResponse,
    FlextApiResponseBuilder,
    PaginatedResponseBuilder,
    PaginationConfig,
    ResponseConfig,
    build_error_response,
    build_paginated_response,
    build_query,
    build_success_response,
)

# Create aliases for functions that tests expect with different names
build_success_response_object = build_success_response
build_error_response_object = build_error_response
build_paginated_response_object = build_paginated_response

# Re-export all for compatibility
__all__ = [
    "FlextApiBuilder",
    "FlextApiQuery",
    "FlextApiQueryBuilder",
    "FlextApiResponse",
    "FlextApiResponseBuilder",
    "PaginatedResponseBuilder",
    "PaginationConfig",
    "ResponseConfig",
    "build_error_response_object",
    "build_paginated_response_object",
    "build_query",
    "build_success_response_object",
]
