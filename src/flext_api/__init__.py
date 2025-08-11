"""FLEXT API - High-Performance REST API Library (PEP8 Reorganized).

A comprehensive API library for building high-performance REST APIs with FastAPI,
following Clean Architecture and Domain-Driven Design principles. Reorganized
according to PEP8 naming standards with consolidated modules.

Core Features:
    - HTTP client with async operations and plugin support
    - Query and response builders with fluent interfaces
    - Domain models following DDD patterns
    - Protocol-based interfaces for extensibility
    - Base service abstractions for SOLID compliance
    - Comprehensive error handling with FlextResult
    - Full backward compatibility through legacy module

Module Organization (PEP8):
    - api_config.py: Configuration management
    - api_models.py: Domain models and entities
    - api_types.py: Type definitions and field patterns
    - api_client.py: HTTP client and builders
    - api_exceptions.py: Exception hierarchy
    - api_storage.py: Storage and persistence
    - api_protocols.py: Interface definitions
    - api_app.py: FastAPI application

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import importlib.metadata

# Version management
try:
    __version__ = importlib.metadata.version("flext-api")
except importlib.metadata.PackageNotFoundError:
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
from flext_api.api_models import (
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

# Import legacy components for backward compatibility
try:
    # Main service and factory - these should always be available
    from flext_api.api import FlextApi, create_flext_api

    # Base service abstractions - these should always be available
    from flext_api.base_service import (
        FlextApiBaseAuthService,
        FlextApiBaseBuilderService,
        FlextApiBaseClientService,
        FlextApiBaseHandlerService,
        FlextApiBaseRepositoryService,
        FlextApiBaseService,
        FlextApiBaseStreamingService,
    )

    _API_SERVICE_AVAILABLE = True

except ImportError as e:
    _API_SERVICE_AVAILABLE = False
    # If these fail, we have a more serious problem
    import warnings
    warnings.warn(f"Failed to import core API components: {e}", ImportWarning, stacklevel=2)

# Try to import constants
try:
    from flext_api.constants import (
        FLEXT_API_CACHE_TTL,
        FLEXT_API_MAX_RETRIES,
        FLEXT_API_TIMEOUT,
        FLEXT_API_VERSION,
        FlextApiConstants,
        FlextApiEndpoints,
        FlextApiFieldType,
        FlextApiSemanticConstants,
        FlextApiStatus,
    )

    _CONSTANTS_AVAILABLE = True

except ImportError:
    # Provide fallback constants if not available
    _CONSTANTS_AVAILABLE = False
    FLEXT_API_VERSION = __version__
    FLEXT_API_TIMEOUT = DEFAULT_TIMEOUT
    FLEXT_API_MAX_RETRIES = DEFAULT_MAX_RETRIES
    FLEXT_API_CACHE_TTL = 300


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

__all__ = [
    # Version Information
    "__version__",
    "__version_info__",

    # Core Types
    "FlextResult",
    "get_logger",

    # Configuration
    "FlextApiSettings",
    "create_api_settings",
    "load_configuration",
    "validate_configuration",

    # Domain Models - Enumerations
    "HttpMethod",
    "HttpStatus",
    "ClientProtocol",
    "ClientStatus",
    "RequestState",
    "ResponseState",
    "TokenType",
    "OperationType",

    # Domain Models - Value Objects
    "URL",
    "HttpHeader",
    "BearerToken",
    "ClientConfig",
    "QueryConfig",
    "PaginationInfo",

    # Domain Models - Entities
    "ApiRequest",
    "ApiResponse",
    "ApiEndpoint",
    "ApiSession",

    # Domain Models - DTOs
    "RequestDto",
    "ResponseDto",
    "ApiErrorContext",
    "QueryBuilder",
    "ResponseBuilder",

    # Domain Models - Constants
    "DEFAULT_TIMEOUT",
    "DEFAULT_PAGE_SIZE",
    "DEFAULT_MAX_RETRIES",

    # Type System
    "APITypes",
    "APITypesCompat",
    "get_api_types",
    "TData",
    "T_Payload",
    "T_Request",
    "T_Response",

    # Field System
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

    # HTTP Client
    "FlextApiClient",
    "FlextApiClientConfig",
    "FlextApiClientRequest",
    "FlextApiClientResponse",
    "FlextApiClientProtocol",
    "FlextApiClientMethod",
    "FlextApiClientStatus",

    # Builders
    "FlextApiBuilder",
    "FlextApiQueryBuilder",
    "FlextApiResponseBuilder",
    "PaginatedResponseBuilder",
    "FlextApiQuery",
    "FlextApiResponse",
    "FlextApiOperation",
    "ResponseConfig",
    "PaginationConfig",

    # Plugin System
    "FlextApiPlugin",
    "FlextApiCachingPlugin",
    "FlextApiRetryPlugin",

    # Exceptions
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

    # Storage
    "FlextApiStorage",
    "StorageConfig",
    "StorageBackend",
    "MemoryStorageBackend",
    "FileStorageBackend",
    "MemoryCache",

    # Protocols
    "FlextApiClientProtocol",
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

    # Application
    "create_flext_api_app",
    "create_flext_api_app_with_settings",
    "run_development_server",
    "run_production_server",
    "app",

    # Factory Functions
    "create_client",
    "create_api_client",
    "create_api_builder",
    "create_storage",
    "create_api_storage",
    "create_memory_storage",
    "create_file_storage",
    "build_query",
    "build_success_response",
    "build_error_response",
    "build_paginated_response",

    # Legacy Constants
    "FLEXT_API_VERSION",
    "FLEXT_API_TIMEOUT",
    "FLEXT_API_MAX_RETRIES",
    "FLEXT_API_CACHE_TTL",
]

# Add legacy imports to __all__ if available
if _API_SERVICE_AVAILABLE:
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
    ]

if _CONSTANTS_AVAILABLE:
    __all__ += [
        "FlextApiConstants",
        "FlextApiSemanticConstants",
        "FlextApiEndpoints",
        "FlextApiFieldType",
        "FlextApiStatus",
    ]
