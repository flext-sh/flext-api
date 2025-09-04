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
    >>> client_result = api.flext_api_create_client(
    ...     {
    ...         "base_url": "https://api.example.com",
    ...         "timeout": 30,
    ...     }
    ... )
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

# =============================================================================
# MODULE AGGREGATION - Following flext-core pattern with explicit imports
# =============================================================================

# Explicit imports to avoid F405 Ruff errors
from flext_api.constants import FlextApiConstants, FlextApiEndpoints, FlextApiStatus, FlextApiFieldType
from flext_api.typings import FlextApiTypes
from flext_api.exceptions import FlextApiExceptions
from flext_api.models import FlextApiModels, CacheConfig, ClientConfig, HttpResponseConfig, RetryConfig
from flext_api.config import FlextApiConfig
from flext_api.api import FlextApi
from flext_api.client import FlextApiClient
from flext_api.plugins import FlextApiPlugins
from flext_api.protocols import FlextApiClientProtocol, FlextApiManagerProtocol
from flext_api.storage import FlextApiStorage
from flext_api.utilities import FlextApiUtilities, HttpRequestConfig, HttpErrorConfig, ValidationConfig
from flext_api.app import FlextApiApp

# Backward compatibility aliases - import explicitly to avoid F405
from flext_api.exceptions import FlextApiExceptions as _FlextApiExceptions
FlextErrors = _FlextApiExceptions

# Additional aliases for tests - based on what models.py actually contains
FlextApiQueryBuilder = FlextApiModels.HttpQuery  # Tests expect FlextApiQueryBuilder
FlextApiBaseService = FlextApiModels.ApiBaseService  # Tests expect FlextApiBaseService
StorageBackend = FlextApiModels.StorageBackend  # Tests expect StorageBackend enum
StorageConfig = FlextApiModels.StorageConfig  # Tests expect StorageConfig
FlextUtils = FlextApiUtilities  # Tests expect FlextUtils
TData = object  # Tests expect TData type alias
PaginationConfig = FlextApiModels.PaginationConfig  # Tests expect PaginationConfig

# URL class aliases for tests - Factory functions returning FlextResult[HttpUrl]
def FlextApiURL(url_string: str) -> "FlextResult[object]":
    """Factory function for creating FlextApiURL with FlextResult pattern."""
    try:
        http_url = FlextApiModels.HttpUrl(url_string)
        from flext_core import FlextResult
        return FlextResult.ok(http_url)
    except Exception as e:
        from flext_core import FlextResult
        return FlextResult.fail(f"Invalid URL: {e}")

def URL(url_string: str) -> "FlextResult[object]":
    """Factory function for creating URL with FlextResult pattern."""
    return FlextApiURL(url_string)

# Model class aliases for tests
ApiRequest = FlextApiModels.ApiRequest  # Tests expect ApiRequest

# Comprehensive manual public API exports
__all__ = [
    # === Core API Classes ===
    "FlextApi",                     # Main API orchestration class
    "FlextApiClient",               # HTTP client with plugin system
    "FlextApiApp",                  # FastAPI application factory
    "FlextApiConfig",               # Configuration management
    "FlextApiStorage",              # Storage backend system
    "FlextApiModels",               # Domain models container
    "FlextApiPlugins",              # Plugin system
    "FlextApiUtilities",            # Utility functions
    "FlextApiConstants",            # Project constants
    "FlextApiTypes",                # Type definitions
    "FlextApiExceptions",           # Exception hierarchy

    # === Configuration Classes ===
    "CacheConfig",                  # Cache configuration
    "ClientConfig",                 # HTTP client configuration
    "HttpResponseConfig",           # Response configuration
    "RetryConfig",                  # Retry policy configuration
    "HttpRequestConfig",            # Request configuration
    "HttpErrorConfig",              # Error handling configuration
    "ValidationConfig",             # Validation configuration

    # === Protocol Interfaces ===
    "FlextApiClientProtocol",       # Client interface protocol
    "FlextApiManagerProtocol",      # Manager interface protocol

    # === Factory Functions ===
    "create_flext_api",             # Create FlextApi instance
    "create_client",                # Create HTTP client
    "create_flext_api_app",         # Create FastAPI app

    # === Backward Compatibility ===
    "FlextErrors",                  # Alias for FlextApiExceptions
    "FlextApiQueryBuilder",         # Legacy builder alias
    "FlextApiBaseService",          # Legacy service alias
    "StorageBackend",               # Legacy storage alias
    "StorageConfig",                # Legacy config alias
    "FlextUtils",                   # Legacy utils alias
    "TData",                        # Type variable alias
    "PaginationConfig",             # Pagination configuration

    # === Constants Aliases ===
    "FlextApiEndpoints",            # Endpoints constants
    "FlextApiStatus",               # Status constants
    "FlextApiFieldType",            # Field type constants

    # === URL Factory Functions ===
    "FlextApiURL",                  # HTTP URL factory function
    "URL",                          # URL factory function

    # === Model Classes ===
    "ApiRequest",                   # API request model

    # === Version Information ===
    "__version__",                  # Package version
]


# Factory functions
def create_flext_api(**kwargs: object) -> FlextApi:
    """Factory function to create FlextApi instance."""
    return FlextApi(**kwargs)


def create_client(config: dict[str, object] | None = None) -> FlextApiClient:
    """Factory function to create HTTP client using default FlextApi instance."""
    api = create_flext_api()
    result = api.create_client(config)
    if result.success:
        return result.value
    msg = f"Client creation failed: {result.error}"
    raise RuntimeError(msg)


def create_flext_api_app(config: object = None, **kwargs: object) -> object:
    """Factory function to create FlextApiApp instance."""
    if config is not None:
        kwargs.update({"config": config})
    app = FlextApiApp(**kwargs)
    # Return the FastAPI app instance for test compatibility
    return app.create_app_instance()


__version__ = "0.9.0"
