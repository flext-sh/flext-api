"""FlextApi - HTTP Foundation Library for FLEXT ecosystem.

This module provides HTTP client functionality, FastAPI app creation, and essential
utilities using flext-core patterns with FlextResult for type-safe error handling.

Architecture:
    Foundation Layer: Constants, types, exceptions from flext-core
    Domain Layer: Models, configuration using FlextModels patterns
    Application Layer: API, client, plugins using FlextDomainService
    Infrastructure Layer: Storage, utilities using FlextUtilities
    Support Layer: App creation, authentication patterns

Core Components:
    FlextApi: Main HTTP API coordination class following composition patterns
    FlextApiClient: HTTP client with plugin system and FlextResult error handling
    FlextApiApp: FastAPI application factory with middleware and CORS
    FlextApiConfig: Configuration management with Pydantic validation
    FlextApiConstants: HTTP-specific constants inheriting from FlextConstants
    FlextApiExceptions: HTTP exception hierarchy with status codes
    FlextApiModels: HTTP domain models with request/response patterns
    FlextApiPlugins: Extensible plugin system for caching, retry, circuit breaker
    FlextApiStorage: Storage backend with memory cache and persistent storage
    FlextApiTypes: Type definitions for HTTP operations and client configuration
    FlextApiUtilities: HTTP utilities extending FlextUtilities

Examples:
    HTTP client with plugins:
    >>> api = FlextApi()
    >>> client_result = api.flext_api_create_client({
    ...     "base_url": "https://api.example.com",
    ...     "timeout": 30,
    ... })
    >>> if client_result.success:
    ...     client = client_result.value
    ...     response = await client.get("/data")

    FastAPI app creation:
    >>> app = FlextApiApp.create_flext_api_app_with_settings()
    >>> # Includes CORS, error handlers, request ID middleware

    Builder pattern:
    >>> builder = api.get_builder()
    >>> query = (
    ...     builder.for_query()
    ...     .equals("status", "active")
    ...     .sort_desc("created_at")
    ...     .build()
    ... )

Notes:
    - All operations return FlextResult[T] following railway-oriented programming
    - Uses flext-core foundation for consistency across FLEXT ecosystem
    - HTTP client supports plugins for caching, retry logic, authentication
    - Configuration follows Pydantic patterns with environment variable support
    - Follows Clean Architecture with layered imports

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

# =============================================================================
# FOUNDATION LAYER - Import first, following flext-core pattern
# =============================================================================

from flext_api.constants import *
from flext_api.typings import *
from flext_api.exceptions import *

# =============================================================================
# DOMAIN LAYER - Depends only on Foundation layer
# =============================================================================

from flext_api.models import *
from flext_api.config import *

# =============================================================================
# APPLICATION LAYER - Depends on Domain + Foundation layers
# =============================================================================

from flext_api.api import *
from flext_api.client import *
from flext_api.plugins import *

# =============================================================================
# INFRASTRUCTURE LAYER - Depends on Application + Domain + Foundation
# =============================================================================

from flext_api.storage import *
from flext_api.utilities import *

# =============================================================================
# SUPPORT LAYER - Depends on layers as needed, imported last
# =============================================================================

from flext_api.app import *

# =============================================================================
# CONSOLIDATED EXPORTS - Combine all __all__ from modules
# =============================================================================

# Combine all __all__ exports from imported modules
import flext_api.api as _api
import flext_api.app as _app
import flext_api.client as _client
import flext_api.config as _config
import flext_api.constants as _constants
import flext_api.exceptions as _exceptions
import flext_api.models as _models
import flext_api.plugins as _plugins
import flext_api.storage as _storage
import flext_api.typings as _typings
import flext_api.utilities as _utilities

# Collect all __all__ exports from imported modules
_temp_exports: list[str] = []

for module in [
    _constants,
    _typings,
    _exceptions,
    _models,
    _config,
    _api,
    _client,
    _plugins,
    _storage,
    _utilities,
    _app,
]:
    if hasattr(module, "__all__"):
        _temp_exports.extend(module.__all__)

# Remove duplicates and sort for consistent exports - build complete list first
_seen: set[str] = set()
_final_exports: list[str] = []
for item in _temp_exports:
    if item not in _seen:
        _seen.add(item)
        _final_exports.append(item)
_final_exports.sort()

# Define __all__ as literal list for linter compatibility
# This dynamic assignment is necessary for aggregating module exports
__all__: list[str] = _final_exports  # pyright: ignore[reportUnsupportedDunderAll] # noqa: PLE0605

__version__ = "0.9.0"
