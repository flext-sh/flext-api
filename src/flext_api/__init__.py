"""FLEXT API - High-Performance REST API Library for FLEXT ecosystem.

A comprehensive API library for building high-performance REST APIs with FastAPI,
implementing Clean Architecture and Domain-Driven Design principles across the
FLEXT ecosystem. This library provides enterprise-grade API services with type safety,
async operations, and comprehensive error handling.

The library has been reorganized according to PEP8 naming standards with consolidated
modules providing clean separation of concerns and maintainable architecture patterns.

Core Features:
    - FastAPI-based REST API framework with automatic OpenAPI documentation
    - Async HTTP client with plugin support and connection pooling
    - Query and response builders with fluent interfaces
    - Domain models following DDD patterns with value objects
    - Protocol-based interfaces for extensibility and testing
    - Base service abstractions following SOLID principles
    - Comprehensive error handling with FlextResult integration
    - Type-safe request/response handling with Pydantic models
    - Built-in authentication and authorization support
    - Metrics collection and observability integration

Module Organization (PEP8 Compliant):
    - api_config.py: Configuration management and environment settings
    - api_models.py: Domain models, entities, and value objects
    - api_types.py: Type definitions, field patterns, and protocols
    - api_client.py: HTTP client, query builders, and response handlers
    - api_exceptions.py: API-specific exception hierarchy
    - api_storage.py: Storage interfaces and persistence patterns
    - api_protocols.py: Interface definitions for services and repositories
    - api_app.py: FastAPI application factory and route definitions

Example:
    Basic API setup and usage:

    >>> from flext_api import FlextAPIApp, create_api_config
    >>> config = create_api_config()
    >>> app = FlextAPIApp(config)
    >>> # FastAPI app is available at app.fastapi_app

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import importlib.metadata


try:
    __version__ = importlib.metadata.version("flext-api")
except Exception:
    __version__ = "0.9.0"

# Version info tuple
__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

# ==============================================================================
# CORE FLEXT IMPORTS
# ==============================================================================

# Core types from flext-core
from flext_core import FlextResult, get_logger

# ==============================================================================
# CONSOLIDATED MODULE IMPORTS (PEP8)
# ==============================================================================

# Configuration Management
from flext_api.api_config import (
    FlextApiSettings,
    create_api_settings,
    load_configuration,
    validate_configuration,
)

# Domain Models and Entities
from flext_api.models import (
    # Enumerations
    HttpMethod,
    HttpStatus,
    ClientProtocol,
    ClientStatus,
    RequestState,
    ResponseState,
    TokenType,
    OperationType,
    # Value Objects
    URL,
    HttpHeader,
    BearerToken,
    ClientConfig,
    QueryConfig,
    PaginationInfo,
    # Entities
    ApiRequest,
    ApiResponse,
    ApiEndpoint,
    ApiSession,
    # DTOs
    RequestDto,
    ResponseDto,
    ApiErrorContext,
    QueryBuilder,
    ResponseBuilder,
    # Constants
    DEFAULT_TIMEOUT,
    DEFAULT_PAGE_SIZE,
    DEFAULT_MAX_RETRIES,
)

# Type System and Field Patterns
from flext_api.api_types import (
    # Type System
    APITypes,
    APITypesCompat,
    get_api_types,
    TData,
    T_Payload,
    T_Request,
    T_Response,
    # Field System
    FlextAPIFieldCore,
    FlextAPIFields,
    # Field Functions
    api_key_field,
    bearer_token_field,
    endpoint_path_field,
    http_method_field,
    pipeline_config_field,
    plugin_config_field,
    response_format_field,
    user_role_field,
)

# HTTP Client and Builder System
from flext_api.api_client import (
    # Client Classes
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiClientRequest,
    FlextApiClientResponse,
    # Client Enums
    FlextApiClientProtocol,
    FlextApiClientMethod,
    FlextApiClientStatus,
    # Builder Classes
    FlextApiBuilder,
    FlextApiQueryBuilder,
    FlextApiResponseBuilder,
    PaginatedResponseBuilder,
    # Data Structures
    FlextApiQuery,
    FlextApiResponse,
    FlextApiOperation,
    # Configuration
    ResponseConfig,
    PaginationConfig,
    # Plugin System
    FlextApiPlugin,
    FlextApiCachingPlugin,
    FlextApiRetryPlugin,
    # Factory Functions
    create_client,
    build_query,
    build_success_response,
    build_error_response,
    build_paginated_response,
)
from flext_api.client import create_client_with_plugins


# Backwards-compatibility helper used by tests expecting a dict
def build_query_dict(
    filters: dict[str, object] | None = None,
    sorts: list[dict[str, str]] | None = None,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    fields: list[str] | None = None,
) -> dict[str, object]:
    """Build a query and return it as a plain dict.

    This is a thin wrapper around ``build_query`` that returns the serialized
    representation expected by legacy tests.
    """
    query = build_query(
        filters=filters,
        sorts=sorts,
        page=page,
        page_size=page_size,
        search=search,
        fields=fields,
    )
    return query.to_dict()


# Exception Hierarchy
from flext_api.api_exceptions import (
    # Base Error
    FlextApiError,
    # Core API Errors
    FlextApiValidationError,
    FlextApiAuthenticationError,
    FlextApiAuthorizationError,
    FlextApiConfigurationError,
    FlextApiConnectionError,
    FlextApiProcessingError,
    FlextApiTimeoutError,
    # Specific API Errors
    FlextApiRequestError,
    FlextApiResponseError,
    FlextApiStorageError,
    FlextApiBuilderError,
    FlextApiRateLimitError,
    FlextApiNotFoundError,
    # Utility Functions
    create_error_response,
    map_http_status_to_exception,
)

# Storage and Persistence
from flext_api.api_storage import (
    # Main Classes
    FlextApiStorage,
    # Configuration
    StorageConfig,
    StorageBackend,
    # Backends
    MemoryStorageBackend,
    FileStorageBackend,
    # Cache Implementation
    MemoryCache,
    # Factory Functions
    create_storage,
    create_memory_storage,
    create_file_storage,
)

# Protocol Definitions (Interfaces)
from flext_api.api_protocols import (
    # HTTP Client Protocols
    FlextApiPluginProtocol,
    FlextApiConnectionPoolProtocol,
    # Builder Protocols
    FlextApiQueryBuilderProtocol,
    FlextApiResponseBuilderProtocol,
    # Service Protocols
    FlextApiServiceProtocol,
    FlextApiAuthProtocol,
    FlextApiAuthorizationProtocol,
    # Repository Protocols
    FlextApiRepositoryProtocol,
    FlextApiCacheProtocol,
    # Middleware Protocols
    FlextApiMiddlewareProtocol,
    FlextApiRateLimitProtocol,
    # Handler Protocols
    FlextApiHandlerProtocol,
    FlextApiValidatorProtocol,
    # Streaming Protocols
    FlextApiStreamProtocol,
    FlextApiWebSocketProtocol,
    # Monitoring Protocols
    FlextApiMetricsProtocol,
    FlextApiHealthCheckProtocol,
)

# FastAPI Application
from flext_api.api_app import (
    create_flext_api_app,
    create_flext_api_app_with_settings,
    run_development_server,
    run_production_server,
    app,  # Default app instance
)

# ==============================================================================
# LEGACY COMPATIBILITY IMPORTS
# ==============================================================================

# Core API components (canonical)
from flext_api.api import FlextApi, create_flext_api


"""Legacy helper aliases and behavior adjustments for tests."""
# Expose sync-compatible health_check for legacy tests without monkey-patching
def sync_health_check(api: FlextApi) -> FlextResult[dict[str, object]]:
    """Run health check synchronously using FlextApi's compatibility helper."""
    return api.health_check_sync()

# Note: Do not monkey-patch FlextApi.health_check. Async tests expect an awaitable.


from flext_api.base_service import (
    FlextApiBaseAuthService,
    FlextApiBaseBuilderService,
    FlextApiBaseClientService,
    FlextApiBaseHandlerService,
    FlextApiBaseRepositoryService,
    FlextApiBaseService,
    FlextApiBaseStreamingService,
)

from flext_api.constants import FlextApiConstants

# Extract constants
FLEXT_API_TIMEOUT = FlextApiConstants.Config.DEFAULT_TIMEOUT
FLEXT_API_MAX_RETRIES = FlextApiConstants.Config.DEFAULT_MAX_RETRIES
FLEXT_API_CACHE_TTL = FlextApiConstants.Cache.DEFAULT_TTL
FLEXT_API_VERSION = __version__


# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================


def create_api_client(config: dict[str, object] | None = None) -> FlextApiClient:
    """Create HTTP client with configuration.

    Convenience function that creates a configured client instance.

    Args:
        config: Client configuration dictionary

    Returns:
        Configured FlextApiClient instance

    Raises:
        ValueError: If configuration is invalid

    """
    return create_client(config)


def create_api_builder() -> FlextApiBuilder:
    """Create API builder instance.

    Convenience function for creating a builder without
    instantiating the full API service.

    Returns:
        FlextApiBuilder instance

    """
    return FlextApiBuilder()


def create_api_storage(backend: str = "memory", **kwargs: object) -> FlextApiStorage:
    """Create storage instance with specified backend.

    Args:
        backend: Storage backend type
        **kwargs: Backend-specific configuration

    Returns:
        Configured FlextApiStorage instance

    """
    return create_storage(backend, **kwargs)


# ==============================================================================
# PUBLIC API EXPORTS
# ==============================================================================

__all__: list[str] = [
    "__version__",
    "__version_info__",
    "FlextResult",
    "get_logger",
    "FlextApiSettings",
    "create_api_settings",
    "load_configuration",
    "validate_configuration",
    "HttpMethod",
    "HttpStatus",
    "ClientProtocol",
    "ClientStatus",
    "RequestState",
    "ResponseState",
    "TokenType",
    "OperationType",
    "URL",
    "HttpHeader",
    "BearerToken",
    "ClientConfig",
    "QueryConfig",
    "PaginationInfo",
    "ApiRequest",
    "ApiResponse",
    "ApiEndpoint",
    "ApiSession",
    "RequestDto",
    "ResponseDto",
    "ApiErrorContext",
    "QueryBuilder",
    "ResponseBuilder",
    "DEFAULT_TIMEOUT",
    "DEFAULT_PAGE_SIZE",
    "DEFAULT_MAX_RETRIES",
    "APITypes",
    "APITypesCompat",
    "get_api_types",
    "TData",
    "T_Payload",
    "T_Request",
    "T_Response",
    "FlextAPIFieldCore",
    "FlextAPIFields",
    "api_key_field",
    "bearer_token_field",
    "endpoint_path_field",
    "http_method_field",
    "pipeline_config_field",
    "plugin_config_field",
    "response_format_field",
    "user_role_field",
    "FlextApiClient",
    "FlextApiClientConfig",
    "FlextApiClientRequest",
    "FlextApiClientResponse",
    "FlextApiClientProtocol",
    "FlextApiClientMethod",
    "FlextApiClientStatus",
    "FlextApiBuilder",
    "FlextApiQueryBuilder",
    "FlextApiResponseBuilder",
    "PaginatedResponseBuilder",
    "FlextApiQuery",
    "FlextApiResponse",
    "FlextApiOperation",
    "ResponseConfig",
    "PaginationConfig",
    "FlextApiPlugin",
    "FlextApiCachingPlugin",
    "FlextApiRetryPlugin",
    "FlextApiError",
    "FlextApiValidationError",
    "FlextApiAuthenticationError",
    "FlextApiAuthorizationError",
    "FlextApiConfigurationError",
    "FlextApiConnectionError",
    "FlextApiProcessingError",
    "FlextApiTimeoutError",
    "FlextApiRequestError",
    "FlextApiResponseError",
    "FlextApiStorageError",
    "FlextApiBuilderError",
    "FlextApiRateLimitError",
    "FlextApiNotFoundError",
    "create_error_response",
    "map_http_status_to_exception",
    "FlextApiStorage",
    "StorageConfig",
    "StorageBackend",
    "MemoryStorageBackend",
    "FileStorageBackend",
    "MemoryCache",
    "FlextApiPluginProtocol",
    "FlextApiConnectionPoolProtocol",
    "FlextApiQueryBuilderProtocol",
    "FlextApiResponseBuilderProtocol",
    "FlextApiServiceProtocol",
    "FlextApiAuthProtocol",
    "FlextApiAuthorizationProtocol",
    "FlextApiRepositoryProtocol",
    "FlextApiCacheProtocol",
    "FlextApiMiddlewareProtocol",
    "FlextApiRateLimitProtocol",
    "FlextApiHandlerProtocol",
    "FlextApiValidatorProtocol",
    "FlextApiStreamProtocol",
    "FlextApiWebSocketProtocol",
    "FlextApiMetricsProtocol",
    "FlextApiHealthCheckProtocol",
    "create_flext_api_app",
    "create_flext_api_app_with_settings",
    "run_development_server",
    "run_production_server",
    "app",
    "create_client",
    "create_api_client",
    "sync_health_check",
    "create_api_builder",
    "create_storage",
    "create_api_storage",
    "create_memory_storage",
    "create_file_storage",
    "build_query",
    "build_query_dict",
    "build_success_response",
    "build_error_response",
    "build_paginated_response",
    "create_client_with_plugins",
    "FLEXT_API_VERSION",
    "FLEXT_API_TIMEOUT",
    "FLEXT_API_MAX_RETRIES",
    "FLEXT_API_CACHE_TTL",
    "annotations",
]

__all__ += [
    "FlextApi",
    "create_flext_api",
    "FlextApiBaseService",
    "FlextApiBaseClientService",
    "FlextApiBaseAuthService",
    "FlextApiBaseRepositoryService",
    "FlextApiBaseHandlerService",
    "FlextApiBaseBuilderService",
    "FlextApiBaseStreamingService",
    "FlextApiConstants",
]
