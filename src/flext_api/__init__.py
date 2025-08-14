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

import dataclasses
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

# HTTP Client and Builder System
from flext_api.api_client import (
    # Builder Classes
    FlextApiBuilder,
    FlextApiCachingPlugin,
    # Client Classes
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiClientMethod,
    # Client Enums
    FlextApiClientProtocol,
    FlextApiClientRequest,
    FlextApiClientResponse,
    FlextApiClientStatus,
    FlextApiOperation,
    # Plugin System
    FlextApiPlugin,
    # Data Structures
    FlextApiQuery,
    FlextApiQueryBuilder,
    FlextApiResponse,
    FlextApiResponseBuilder,
    FlextApiRetryPlugin,
    PaginatedResponseBuilder,
    PaginationConfig,
    # Configuration
    ResponseConfig,
    build_error_response,
    build_paginated_response,
    build_query,
    build_query_from_params,
    build_success_response,
    # Factory Functions
    create_client,
)

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

# Type System and Field Patterns
from flext_api.api_types import (
    # Type System
    APITypes,
    APITypesCompat,
    # Field System
    FlextAPIFieldCore,
    FlextAPIFields,
    T_Payload,
    T_Request,
    T_Response,
    TData,
    # Field Functions
    api_key_field,
    bearer_token_field,
    endpoint_path_field,
    get_api_types,
    http_method_field,
    pipeline_config_field,
    plugin_config_field,
    response_format_field,
    user_role_field,
)
from flext_api.client import create_client_with_plugins

# Domain Models and Entities
from flext_api.api_models import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_PAGE_SIZE,
    # Constants
    DEFAULT_TIMEOUT,
    # Value Objects
    URL,
    ApiEndpoint,
    ApiErrorContext,
    # Entities
    ApiRequest,
    ApiResponse,
    ApiSession,
    BearerToken,
    ClientConfig,
    ClientProtocol,
    ClientStatus,
    HttpHeader,
    # Enumerations
    HttpMethod,
    HttpStatus,
    OperationType,
    PaginationInfo,
    QueryBuilder,
    QueryConfig,
    # DTOs
    RequestDto,
    RequestState,
    ResponseBuilder,
    ResponseDto,
    ResponseState,
    TokenType,
)


# Backwards-compatibility helper used by tests expecting a dict
@dataclasses.dataclass
class FlextApiQueryParameters:
    """Parameter Object Pattern: Encapsulates query building parameters.

    REFACTORED: Applied Parameter Object pattern to reduce function complexity
    from 6 parameters to single object following SOLID principles.
    """

    filters: dict[str, object] | list[dict[str, object]] | None = None
    sorts: list[dict[str, str]] | None = None
    page: int = 1
    page_size: int = 20
    search: str | None = None
    fields: list[str] | None = None


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

    REFACTORED: Function signature maintained for backward compatibility.
    """
    params = FlextApiQueryParameters(
        filters=filters,
        sorts=sorts,
        page=page,
        page_size=page_size,
        search=search,
        fields=fields,
    )
    query = build_query_from_params(params)
    return query.to_dict()


# Exception Hierarchy
# ==============================================================================
# LEGACY COMPATIBILITY IMPORTS
# ==============================================================================
# Core API components (canonical)
from flext_api.api import FlextApi, create_flext_api

# FastAPI Application
from flext_api.api_app import (
    app,  # Default app instance
    create_flext_api_app,
    create_flext_api_app_with_settings,
    run_development_server,
    run_production_server,
)
from flext_api.api_exceptions import (
    FlextApiAuthenticationError,
    FlextApiAuthorizationError,
    FlextApiBuilderError,
    FlextApiConfigurationError,
    FlextApiConnectionError,
    # Base Error
    FlextApiError,
    FlextApiNotFoundError,
    FlextApiProcessingError,
    FlextApiRateLimitError,
    # Specific API Errors
    FlextApiRequestError,
    FlextApiResponseError,
    FlextApiStorageError,
    FlextApiTimeoutError,
    # Core API Errors
    FlextApiValidationError,
    # Utility Functions
    create_error_response,
    map_http_status_to_exception,
)

# Protocol Definitions (Interfaces)
from flext_api.api_protocols import (
    FlextApiAuthorizationProtocol,
    FlextApiAuthProtocol,
    FlextApiCacheProtocol,
    FlextApiConnectionPoolProtocol,
    # Handler Protocols
    FlextApiHandlerProtocol,
    FlextApiHealthCheckProtocol,
    # Monitoring Protocols
    FlextApiMetricsProtocol,
    # Middleware Protocols
    FlextApiMiddlewareProtocol,
    # HTTP Client Protocols
    FlextApiPluginProtocol,
    # Builder Protocols
    FlextApiQueryBuilderProtocol,
    FlextApiRateLimitProtocol,
    # Repository Protocols
    FlextApiRepositoryProtocol,
    FlextApiResponseBuilderProtocol,
    # Service Protocols
    FlextApiServiceProtocol,
    # Streaming Protocols
    FlextApiStreamProtocol,
    FlextApiValidatorProtocol,
    FlextApiWebSocketProtocol,
)

# Storage and Persistence
from flext_api.api_storage import (
    FileStorageBackend,
    # Main Classes
    FlextApiStorage,
    # Cache Implementation
    MemoryCache,
    # Backends
    MemoryStorageBackend,
    StorageBackend,
    # Configuration
    StorageConfig,
    create_file_storage,
    create_memory_storage,
    # Factory Functions
    create_storage,
)

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
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_PAGE_SIZE",
    "DEFAULT_TIMEOUT",
    "FLEXT_API_CACHE_TTL",
    "FLEXT_API_MAX_RETRIES",
    "FLEXT_API_TIMEOUT",
    "FLEXT_API_VERSION",
    "URL",
    "APITypes",
    "APITypesCompat",
    "ApiEndpoint",
    "ApiErrorContext",
    "ApiRequest",
    "ApiResponse",
    "ApiSession",
    "BearerToken",
    "ClientConfig",
    "ClientProtocol",
    "ClientStatus",
    "FileStorageBackend",
    "FlextAPIFieldCore",
    "FlextAPIFields",
    "FlextApiAuthProtocol",
    "FlextApiAuthenticationError",
    "FlextApiAuthorizationError",
    "FlextApiAuthorizationProtocol",
    "FlextApiBuilder",
    "FlextApiBuilderError",
    "FlextApiCacheProtocol",
    "FlextApiCachingPlugin",
    "FlextApiClient",
    "FlextApiClientConfig",
    "FlextApiClientMethod",
    "FlextApiClientProtocol",
    "FlextApiClientRequest",
    "FlextApiClientResponse",
    "FlextApiClientStatus",
    "FlextApiConfigurationError",
    "FlextApiConnectionError",
    "FlextApiConnectionPoolProtocol",
    "FlextApiError",
    "FlextApiHandlerProtocol",
    "FlextApiHealthCheckProtocol",
    "FlextApiMetricsProtocol",
    "FlextApiMiddlewareProtocol",
    "FlextApiNotFoundError",
    "FlextApiOperation",
    "FlextApiPlugin",
    "FlextApiPluginProtocol",
    "FlextApiProcessingError",
    "FlextApiQuery",
    "FlextApiQueryBuilder",
    "FlextApiQueryBuilderProtocol",
    "FlextApiRateLimitError",
    "FlextApiRateLimitProtocol",
    "FlextApiRepositoryProtocol",
    "FlextApiRequestError",
    "FlextApiResponse",
    "FlextApiResponseBuilder",
    "FlextApiResponseBuilderProtocol",
    "FlextApiResponseError",
    "FlextApiRetryPlugin",
    "FlextApiServiceProtocol",
    "FlextApiSettings",
    "FlextApiStorage",
    "FlextApiStorageError",
    "FlextApiStreamProtocol",
    "FlextApiTimeoutError",
    "FlextApiValidationError",
    "FlextApiValidatorProtocol",
    "FlextApiWebSocketProtocol",
    "FlextResult",
    "HttpHeader",
    "HttpMethod",
    "HttpStatus",
    "MemoryCache",
    "MemoryStorageBackend",
    "OperationType",
    "PaginatedResponseBuilder",
    "PaginationConfig",
    "PaginationInfo",
    "QueryBuilder",
    "QueryConfig",
    "RequestDto",
    "RequestState",
    "ResponseBuilder",
    "ResponseConfig",
    "ResponseDto",
    "ResponseState",
    "StorageBackend",
    "StorageConfig",
    "TData",
    "T_Payload",
    "T_Request",
    "T_Response",
    "TokenType",
    "__version__",
    "__version_info__",
    "annotations",
    "api_key_field",
    "app",
    "bearer_token_field",
    "build_error_response",
    "build_paginated_response",
    "build_query",
    "build_query_dict",
    "build_query_from_params",
    "build_success_response",
    "create_api_builder",
    "create_api_client",
    "create_api_settings",
    "create_api_storage",
    "create_client",
    "create_client_with_plugins",
    "create_error_response",
    "create_file_storage",
    "create_flext_api_app",
    "create_flext_api_app_with_settings",
    "create_memory_storage",
    "create_storage",
    "endpoint_path_field",
    "get_api_types",
    "get_logger",
    "http_method_field",
    "load_configuration",
    "map_http_status_to_exception",
    "pipeline_config_field",
    "plugin_config_field",
    "response_format_field",
    "run_development_server",
    "run_production_server",
    "sync_health_check",
    "user_role_field",
    "validate_configuration",
    "FlextApi",
    "FlextApiBaseAuthService",
    "FlextApiBaseBuilderService",
    "FlextApiBaseClientService",
    "FlextApiBaseHandlerService",
    "FlextApiBaseRepositoryService",
    "FlextApiBaseService",
    "FlextApiBaseStreamingService",
    "FlextApiConstants",
    "create_flext_api",
]
