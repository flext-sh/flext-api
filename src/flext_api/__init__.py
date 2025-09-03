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
    >>> app = FlextApiApp.create_app_instance()
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

from typing import TYPE_CHECKING

# Import types for factory functions
from flext_api.api import FlextApi
from flext_api.app import FlextApiApp

# =============================================================================
# MODULE AGGREGATION - Following flext-core pattern
# =============================================================================

# Import all from each module with proper type handling
from flext_api.constants import *
from flext_api.typings import *
from flext_api.exceptions import *
from flext_api.models import *
from flext_api.config import *
from flext_api.api import *
from flext_api.client import *
from flext_api.plugins import *
from flext_api.protocols import *
from flext_api.storage import *
from flext_api.utilities import *
from flext_api.app import *

# Manually aggregated __all__ from all modules - star imports are intentional FLEXT pattern
__all__ = [
    # From constants
    "FlextApiConstants",
    # From typings
    "FlextApiTypes",
    # From exceptions
    "FlextApiExceptions",
    # From models
    "FlextApiModels",
    # From config
    "FlextApiConfig",
    # From api
    "FlextApi",
    # From client
    "FlextApiClient",
    # From plugins
    "FlextApiCachingPlugin",
    "FlextApiCircuitBreakerPlugin",
    "FlextApiPlugin",
    "FlextApiPlugins",
    "FlextApiRetryPlugin",
    # From protocols
    "FlextApiAuthentication",
    "FlextApiClientProtocol",
    "FlextApiDiscovery",
    "FlextApiFactory",
    "FlextApiManagerProtocol",
    "FlextApiService",
    # From storage
    "FlextApiStorage",
    # From utilities
    "FlextApiUtilities",
    # From app
    "FlextApiApp",
    "create_flext_api",
    "create_flext_api_app",
]


# Factory functions
def create_flext_api(**kwargs: object) -> FlextApi:
    """Factory function to create FlextApi instance."""
    return FlextApi(**kwargs)


def create_flext_api_app(**kwargs: object) -> FlextApiApp:
    """Factory function to create FlextApiApp instance."""
    return FlextApiApp(**kwargs)


__version__ = "0.9.0"
