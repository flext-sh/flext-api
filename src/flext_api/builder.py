"""FLEXT API Builder Module.

Compatibility module that bridges to api_client.py builder functionality.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Import builder classes and functions from api_client
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
