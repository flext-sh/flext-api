"""FLEXT API - HTTP client and API building library.

HTTP client library with plugin support and query/response builder patterns.
Provides FlextApi service class, HTTP client with configurable plugins,
and builder classes for constructing queries and responses.

Main exports:
    - FlextApi: Main service class for HTTP operations
    - create_flext_api(): Factory function for FlextApi instances
    - FlextApiClient: HTTP client with plugin support
    - create_client(): Factory function for HTTP clients
    - FlextApiBuilder: Query and response builders
    - build_*_response(): Response building functions
    - flext_api_create_app(): FastAPI application factory

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import importlib.metadata

from flext_core import FlextResult, get_logger

from flext_api.api import FlextApi, create_flext_api
from flext_api.app import flext_api_create_app
from flext_api.builder import (
    FlextApiBuilder,
    FlextApiOperation,
    FlextApiQuery,
    FlextApiQueryBuilder,
    FlextApiResponse,
    FlextApiResponseBuilder,
    build_error_response,
    build_error_response_object,
    build_paginated_response,
    build_paginated_response_object,
    build_query,
    build_query_dict,
    build_success_response,
    build_success_response_object,
)
from flext_api.client import (
    FlextApiCachingPlugin,
    FlextApiCircuitBreakerPlugin,
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiClientMethod,
    FlextApiClientProtocol,
    FlextApiClientRequest,
    FlextApiClientResponse,
    FlextApiClientStatus,
    FlextApiPlugin,
    FlextApiRetryPlugin,
    create_client,
    create_client_with_plugins,
)

# === VERSÃO ===
try:
    __version__ = importlib.metadata.version("flext-api")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.9.0"

__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

# === EXPORTS ===
__all__: list[str] = [
    "FlextApi",
    "FlextApiBuilder",
    "FlextApiCachingPlugin",
    "FlextApiCircuitBreakerPlugin",
    "FlextApiClient",
    "FlextApiClientConfig",
    "FlextApiClientMethod",
    "FlextApiClientProtocol",
    "FlextApiClientRequest",
    "FlextApiClientResponse",
    "FlextApiClientStatus",
    "FlextApiOperation",
    "FlextApiPlugin",
    "FlextApiQuery",
    "FlextApiQueryBuilder",
    "FlextApiResponse",
    "FlextApiResponseBuilder",
    "FlextApiRetryPlugin",
    "FlextResult",
    "__version__",
    "__version_info__",
    "build_error_response",
    "build_error_response_object",
    "build_paginated_response",
    "build_paginated_response_object",
    "build_query",
    "build_query_dict",
    "build_success_response",
    "build_success_response_object",
    "create_client",
    "create_client_with_plugins",
    "create_flext_api",
    "flext_api_create_app",
    "get_logger",
]
