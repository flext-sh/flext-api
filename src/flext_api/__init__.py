"""FLEXT API - Enterprise FastAPI Gateway.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Biblioteca limpa usando flext-core, sem aliases ou código legacy.
"""

from __future__ import annotations

import importlib.metadata

# === VERSÃO ===
try:
    __version__ = importlib.metadata.version("flext-api")
except importlib.metadata.PackageNotFoundError:
    __version__ = "1.0.0"

__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

# === FLEXT-CORE ESSENTIALS ===
from flext_core import FlextResult, get_logger

# === FUNCIONALIDADES PRINCIPAIS ===
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
    build_paginated_response,
    build_query,
    build_success_response,
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

# === EXPORTS ===
__all__ = [
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
    "build_paginated_response",
    "build_query",
    "build_success_response",
    "create_client",
    "create_client_with_plugins",
    "create_flext_api",
    "flext_api_create_app",
    "get_logger",
]
