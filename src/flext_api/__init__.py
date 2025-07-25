"""FLEXT API - Enterprise FastAPI Gateway.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Modern enterprise-grade API gateway built on flext-core foundation.
NO FAKE IMPORTS, NO LEGACY CODE, NO FALLBACKS.
"""

from __future__ import annotations

import importlib.metadata
import logging
from typing import Any

# Core flext-core imports
from flext_core import (
    FlextEntity,
    FlextResult,
    FlextValueObject,
)

# Application layer imports
from flext_api.application.services.api_service import FlextAPIService
from flext_api.application.services.auth_service import FlextAuthService
from flext_api.application.services.pipeline_service import PipelineService
from flext_api.application.services.plugin_service import PluginService
from flext_api.application.services.system_service import SystemService

# ==============================================================================
# API BASE PATTERNS - Foundation classes
# ==============================================================================
from flext_api.base import (
    APIStatus,
    FlextApiBaseRequest,
    FlextAPIRequest,
    FlextAPIResponse,
)

# Universal API Client imports
from flext_api.client import (
    FlextApiCachingPlugin,
    FlextApiCircuitBreakerPlugin,
    FlextApiClient,
    FlextApiClientBuilder,
    FlextApiClientConfig,
    FlextApiClientMethod,
    FlextApiClientProtocol,
    FlextApiClientRequest,
    FlextApiClientResponse,
    FlextApiClientStatus,
    FlextApiGraphQLClient,
    FlextApiGraphQLQuery,
    FlextApiGraphQLResponse,
    FlextApiLoggingPlugin,
    FlextApiMetricsPlugin,
    FlextApiPlugin,
    FlextApiRequestValidator,
    FlextApiResponseValidator,
    FlextApiRetryPlugin,
    FlextApiStreamingClient,
    FlextApiValidationManager,
    FlextApiValidationRule,
    FlextApiValidationRuleset,
    FlextApiValidators,
    FlextApiWebSocketClient,
    FlextApiWebSocketMessage,
    flext_api_client_context,
    flext_api_create_client,
)

# ==============================================================================
# COMMON UTILITIES - Shared functionality
# ==============================================================================
from flext_api.common import (
    create_health_check_response,
    ensure_service_available,
    handle_api_exceptions,
    validate_entity_name,
    validate_uuid,
)

# ==============================================================================
# DOMAIN ENTITIES - Core business objects
# ==============================================================================
from flext_api.domain.entities import (
    FlextAPIPipeline,
    Pipeline,
    PipelineExecution,
    Plugin,
    PluginType,
)

# ==============================================================================
# DOMAIN VALUE OBJECTS - Immutable business values
# ==============================================================================
from flext_api.domain.value_objects import (
    ApiEndpoint,
    ApiKey,
    ApiVersion,
    CorsOrigin,
    PipelineId,
    PluginId,
    RateLimit,
    RequestId,
    RequestTimeout,
)

# ==============================================================================
# EXCEPTIONS - API-specific error handling
# ==============================================================================
from flext_api.exceptions import (
    FlextAPIAuthenticationError,
    FlextAPIAuthorizationError,
    FlextAPIConfigurationError,
    FlextAPIConnectionError,
    FlextAPIError,
    FlextAPINotFoundError,
    FlextAPIValidationError,
)

# ==============================================================================
# HELPER CLASSES - Traditional utilities
# ==============================================================================
from flext_api.helpers import (
    FlextApiValidator,
    flext_api_authenticated,
    flext_api_authorize_roles,
    flext_api_cache_response,
    flext_api_handle_errors,
    flext_api_log_execution,
    flext_api_normalize_phone,
    flext_api_rate_limit,
    flext_api_require_json,
    flext_api_sanitize_email,
    flext_api_sanitize_string,
    flext_api_validate_email,
    flext_api_validate_ip_address,
    flext_api_validate_password,
    flext_api_validate_phone,
    flext_api_validate_request,
    flext_api_validate_url,
    # Additional validation helpers
    flext_api_validate_uuid,
)

# ==============================================================================
# BOILERPLATE REDUCERS - Massive code reduction utilities (NEW)
# ==============================================================================
from flext_api.helpers.flext_api_boilerplate import (
    FlextApiApplicationClient,
    FlextApiApplicationMixin,
    FlextApiAuthMixin,
    FlextApiCacheMixin,
    FlextApiClientBuilder,
    FlextApiConfig,
    FlextApiData,
    FlextApiDataProcessingMixin,
    FlextApiEnhancedClient,
    FlextApiHeaders,
    FlextApiHealthCheck,
    FlextApiMetrics,
    FlextApiMetricsMixin,
    FlextApiParams,
    FlextApiRequest,
    FlextApiResponse,
    FlextApiServiceCall,
    FlextApiValidationMixin,
    flext_api_config_dict,
    flext_api_create_application_client,
    flext_api_create_client_builder,
    flext_api_create_enhanced_client,
    flext_api_create_full_client,
    flext_api_create_microservice_client,
    flext_api_create_service_calls,
    flext_api_error_dict,
    flext_api_filter_dict,
    flext_api_flatten_dict,
    flext_api_group_by_key,
    flext_api_merge_dicts,
    flext_api_pick_values,
    flext_api_rename_keys,
    flext_api_request_dict,
    flext_api_success_dict,
    flext_api_transform_values,
    flext_api_with_cache,
    flext_api_with_logging,
    flext_api_with_retry,
    flext_api_with_timeout,
    flext_api_with_validation,
)

# ==============================================================================
# FLEXT-API BUILDER CLASSES - Massive code reduction patterns
# ==============================================================================
from flext_api.helpers.flext_api_builder import (
    FlextApiBuilder,
    FlextApiConfig,
    flext_api_create_app,
)

# ==============================================================================
# FLEXT-API MIDDLEWARE - Enterprise middleware patterns
# ==============================================================================
from flext_api.helpers.flext_api_middleware import (
    FlextApiCORSMiddleware,
    FlextApiLoggingMiddleware,
    FlextApiMetricsMiddleware,
    FlextApiRateLimitMiddleware,
    FlextApiSecurityMiddleware,
)

# ==============================================================================
# ENTERPRISE PATTERNS - Advanced code reduction (NEW)
# ==============================================================================
from flext_api.helpers.flext_api_patterns import (
    FlextApiClientPool,
    FlextApiDataFlow,
    FlextApiEnterpriseOrchestrator,
    FlextApiServiceDefinition,
    FlextApiSmartCache,
    flext_api_create_client_pool,
    flext_api_create_enterprise_orchestrator,
    flext_api_create_smart_cache,
)

# ==============================================================================
# PRACTICAL HELPERS - Real-world utilities (NEW)
# ==============================================================================
from flext_api.helpers.flext_api_practical import (
    FlextApiConfigManager,
    FlextApiDataTransformer,
    FlextApiDebugger,
    FlextApiPerformanceMonitor,
    FlextApiWorkflow,
    flext_api_compare_responses,
    flext_api_create_config_manager,
    flext_api_create_debugger,
    flext_api_create_performance_monitor,
    flext_api_create_workflow,
    flext_api_quick_health_check,
)

# ==============================================================================
# QUICK HELPERS - Massive code reduction utilities (NEW)
# ==============================================================================
from flext_api.helpers.flext_api_quick import (
    FlextApiMicroserviceIntegrator,
    FlextApiResponseAggregator,
    flext_api_enterprise_client,
    flext_api_fetch_user_data,
    flext_api_health_check_all,
    flext_api_quick_bulk,
    flext_api_quick_get,
    flext_api_quick_post,
)

# Query builder utilities with FlextApi prefix
from flext_api.helpers.query_builder import (
    FlextApiQueryBuilder,
    FlextApiQueryOperator,
    FlextApiSortDirection,
    flext_api_build_simple_query,
    flext_api_create_filter,
    flext_api_create_sort,
    flext_api_parse_query_params,
)

# Response builder functions with FlextApi prefix
from flext_api.helpers.response_builder import (
    FlextApiResponseBuilder,
    flext_api_error_response,
    flext_api_from_flext_result,
    flext_api_paginated_response,
    flext_api_success_response,
)

# ==============================================================================
# INFRASTRUCTURE - Technical implementation
# ==============================================================================
from flext_api.infrastructure.config import APIConfig
from flext_api.infrastructure.ports import (
    FlextApiAuthPort,
    FlextApiPluginPort,
    FlextAuthorizationStrategy,
    FlextJWTAuthService,
    FlextRoleBasedAuthorizationStrategy,
    FlextTokenManager,
)
from flext_api.infrastructure.repositories.pipeline_repository import (
    FlextInMemoryPipelineRepository,
)
from flext_api.infrastructure.repositories.plugin_repository import (
    FlextInMemoryPluginRepository,
)

# ==============================================================================
# VERSION AND UTILITY FUNCTIONS
# ==============================================================================


def get_logger(name: str) -> logging.Logger:
    """Get logger instance - compatibility function."""
    return logging.getLogger(name)


try:
    __version__ = importlib.metadata.version("flext-api")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.8.0"

__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

# ==============================================================================
# MAIN FLEXT API CLASSES - Primary unified exports
# ==============================================================================
# Main API classes - unified access point
FlextApi = FlextAPIService
FlextApiService = FlextAPIService
FlextApiPlatform = FlextAPIService

# Configuration classes
FlextApiSettings = APIConfig

# Core service classes
FlextApiAuthService = FlextAuthService
FlextApiPipelineService = PipelineService
FlextApiPluginService = PluginService
FlextApiSystemService = SystemService

# Domain entity classes
FlextApiPipeline = FlextAPIPipeline
FlextApiDomainPlugin = Plugin  # Renamed to avoid conflict with client Plugin

# Request/Response classes
FlextApiRequest = FlextAPIRequest
FlextApiResponse = FlextAPIResponse
# Infrastructure classes
FlextApiAuthorizationStrategy = FlextAuthorizationStrategy
FlextApiJWTAuthService = FlextJWTAuthService
FlextApiRoleBasedAuthorizationStrategy = FlextRoleBasedAuthorizationStrategy
FlextApiTokenManager = FlextTokenManager
FlextApiInMemoryPipelineRepository = FlextInMemoryPipelineRepository
FlextApiInMemoryPluginRepository = FlextInMemoryPluginRepository


# ==============================================================================
# FLEXT-API FACTORY FUNCTIONS - Unified creation patterns
# ==============================================================================
def flext_api_create_service(
    config: dict[str, object] | None = None,
) -> FlextAPIService:
    """Create FlextAPIService instance with optional configuration."""
    # FlextAPIService uses dependency injection, config is optional
    return FlextAPIService()


def flext_api_create_config(
    **kwargs: object,
) -> APIConfig:
    """Create APIConfig instance with optional parameters."""
    return APIConfig(**kwargs)


def flext_api_create_auth_service(
    config: dict[str, object] | None = None,
) -> FlextAuthService:
    """Create FlextAuthService instance with optional configuration."""
    # FlextAuthService uses dependency injection, config is optional
    return FlextAuthService()


def flext_api_create_pipeline_service() -> PipelineService:
    """Create PipelineService instance with repository."""
    repository = FlextInMemoryPipelineRepository()
    return PipelineService(repository)


def flext_api_create_plugin_service() -> PluginService:
    """Create PluginService instance with repository."""
    repository = FlextInMemoryPluginRepository()
    return PluginService(repository)


def flext_api_create_system_service(
    config: dict[str, object] | None = None,
) -> SystemService:
    """Create SystemService instance with optional configuration."""
    # SystemService uses dependency injection, config is optional
    return SystemService()


def flext_api_validate_config(config: dict[str, object]) -> FlextResult[bool]:
    """Validate API configuration using FlextResult pattern."""
    try:
        APIConfig(**config)
        return FlextResult.ok(True)
    except Exception as e:
        return FlextResult.fail(f"Configuration validation failed: {e}")


def flext_api_create_health_check(
    entity_name: str = "flext-api",
    is_healthy: bool = True,
    message: str = "API is running",
) -> dict[str, object]:
    """Create health check response with customizable parameters."""
    return create_health_check_response(
        entity_name=entity_name, is_healthy=is_healthy, message=message
    )


def flext_api_handle_exceptions(func: Any) -> Any:
    """Decorator to handle API exceptions."""
    return handle_api_exceptions(func)


# ==============================================================================
# PUBLIC API EXPORTS - What users should import
# ==============================================================================
__all__ = [
    # ===== CORE UTILITIES =====
    "APIStatus",
    # ===== MAIN FLEXT API CLASSES =====
    "FlextApi",
    # ===== BOILERPLATE REDUCERS =====
    "FlextApiAuthMixin",
    # ===== INFRASTRUCTURE =====
    "FlextApiAuthPort",
    # ===== CORE SERVICES =====
    "FlextApiAuthService",
    "FlextApiAuthorizationStrategy",
    "FlextApiBaseRequest",
    # ===== BUILDER PATTERNS =====
    "FlextApiBuilder",
    # ===== MIDDLEWARE =====
    "FlextApiCORSMiddleware",
    "FlextApiCacheMixin",
    # ===== UNIVERSAL API CLIENT =====
    "FlextApiCachingPlugin",
    "FlextApiCircuitBreakerPlugin",
    "FlextApiClient",
    "FlextApiClientBuilder",
    "FlextApiClientConfig",
    "FlextApiClientMethod",
    # ===== ENTERPRISE PATTERNS =====
    "FlextApiClientPool",
    "FlextApiClientProtocol",
    "FlextApiClientRequest",
    "FlextApiClientResponse",
    "FlextApiClientStatus",
    # ===== CONFIGURATION =====
    "FlextApiConfig",
    # ===== PRACTICAL HELPERS =====
    "FlextApiConfigManager",
    "FlextApiData",
    "FlextApiDataFlow",
    "FlextApiDataTransformer",
    "FlextApiDebugger",
    "FlextApiEnterpriseOrchestrator",
    "FlextApiGraphQLClient",
    "FlextApiGraphQLQuery",
    "FlextApiGraphQLResponse",
    "FlextApiHeaders",
    "FlextApiHealthCheck",
    "FlextApiInMemoryPipelineRepository",
    "FlextApiInMemoryPluginRepository",
    "FlextApiJWTAuthService",
    "FlextApiLoggingMiddleware",
    "FlextApiLoggingPlugin",
    "FlextApiMetrics",
    "FlextApiMetricsMiddleware",
    "FlextApiMetricsMixin",
    "FlextApiMetricsPlugin",
    # ===== QUICK HELPERS - MASSIVE CODE REDUCTION =====
    "FlextApiMicroserviceIntegrator",
    "FlextApiParams",
    "FlextApiPerformanceMonitor",
    # ===== DOMAIN ENTITIES =====
    "FlextApiPipeline",
    "FlextApiPipelineService",
    "FlextApiPlatform",
    "FlextApiPlugin",
    "FlextApiPlugin",
    "FlextApiPluginPort",
    "FlextApiPluginService",
    "FlextApiQueryBuilder",
    # ===== QUERY UTILITIES =====
    "FlextApiQueryOperator",
    "FlextApiRateLimitMiddleware",
    "FlextApiRequest",
    # ===== REQUEST/RESPONSE =====
    "FlextApiRequest",
    "FlextApiRequestValidator",
    "FlextApiResponse",
    "FlextApiResponse",
    "FlextApiResponseAggregator",
    "FlextApiResponseBuilder",
    "FlextApiResponseValidator",
    "FlextApiRetryPlugin",
    "FlextApiRoleBasedAuthorizationStrategy",
    "FlextApiSecurityMiddleware",
    "FlextApiService",
    "FlextApiServiceCall",
    "FlextApiServiceDefinition",
    "FlextApiSettings",
    "FlextApiSimpleClient",
    "FlextApiSmartCache",
    "FlextApiSortDirection",
    "FlextApiStreamingClient",
    "FlextApiSystemService",
    "FlextApiTokenManager",
    "FlextApiValidationManager",
    "FlextApiValidationMixin",
    "FlextApiValidationRule",
    "FlextApiValidationRuleset",
    "FlextApiValidator",
    "FlextApiValidators",
    "FlextApiWebSocketClient",
    "FlextApiWebSocketMessage",
    "FlextApiWorkflow",
    # ===== CORE PATTERNS FROM FLEXT-CORE =====
    "FlextEntity",
    "FlextResult",
    "FlextValueObject",
    # ===== DECORATORS =====
    "flext_api_authenticated",
    "flext_api_authorize_roles",
    "flext_api_build_simple_query",
    "flext_api_cache_response",
    "flext_api_client_context",
    "flext_api_compare_responses",
    "flext_api_config_dict",
    # ===== FACTORY FUNCTIONS =====
    "flext_api_create_app",
    "flext_api_create_application_client",
    "flext_api_create_auth_service",
    "flext_api_create_client",
    "flext_api_create_client_builder",
    "flext_api_create_client_pool",
    "flext_api_create_config",
    "flext_api_create_config_manager",
    "flext_api_create_debugger",
    "flext_api_create_enhanced_client",
    "flext_api_create_enterprise_orchestrator",
    "flext_api_create_full_client",
    "flext_api_create_health_check",
    "flext_api_create_microservice_client",
    "flext_api_create_performance_monitor",
    "flext_api_create_pipeline_service",
    "flext_api_create_plugin_service",
    "flext_api_create_service",
    "flext_api_create_service_calls",
    "flext_api_create_smart_cache",
    "flext_api_create_smart_cache",
    "flext_api_create_system_service",
    "flext_api_create_workflow",
    "flext_api_enterprise_client",
    "flext_api_error_dict",
    # ===== RESPONSE UTILITIES =====
    "flext_api_error_response",
    "flext_api_fetch_user_data",
    "flext_api_filter_dict",
    "flext_api_flatten_dict",
    "flext_api_from_flext_result",
    "flext_api_group_by_key",
    "flext_api_handle_errors",
    "flext_api_handle_exceptions",
    "flext_api_health_check_all",
    "flext_api_log_execution",
    "flext_api_merge_dicts",
    "flext_api_paginated_response",
    "flext_api_parse_query_params",
    "flext_api_pick_values",
    "flext_api_quick_bulk",
    "flext_api_quick_get",
    "flext_api_quick_health_check",
    "flext_api_quick_post",
    "flext_api_rate_limit",
    "flext_api_rename_keys",
    "flext_api_request_dict",
    "flext_api_require_json",
    "flext_api_success_dict",
    "flext_api_success_response",
    "flext_api_transform_values",
    "flext_api_validate_config",
    # ===== VALIDATION UTILITIES =====
    "flext_api_validate_email",
    "flext_api_validate_password",
    "flext_api_validate_request",
    "flext_api_with_cache",
    "flext_api_with_logging",
    "flext_api_with_retry",
    "flext_api_with_timeout",
    "flext_api_with_validation",
    "get_logger",
    "validate_uuid",
]
