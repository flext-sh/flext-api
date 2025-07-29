"""FLEXT API domain layer.

Built on flext-core foundation for robust domain modeling.
Uses modern Python 3.13 patterns and DDD architecture.
"""

from __future__ import annotations

# ==============================================================================
# DOMAIN ENTITIES - Business entities with identity
# ==============================================================================
from flext_api.domain.entities import (
    APIResponseLog,
    FlextApiEndpoint,
    FlextAPIPipeline,
    FlextAPIRequest,
    FlextApiRequest,
    FlextApiResponse,
    HttpMethod,
    Pipeline,
    PipelineExecution,
    PipelineStatus,
    Plugin,
    PluginMetadata,
    PluginType,
)

# ==============================================================================
# VALUE OBJECTS - Immutable domain values
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
# PUBLIC DOMAIN API - Organized by semantic category
# ==============================================================================
__all__ = [
    "APIResponseLog"
    # ================== VALUE OBJECTS ==================
    # API Configuration
    "ApiEndpoint"
    "ApiKey"
    "ApiVersion"
    "CorsOrigin"
    # ================== DOMAIN ENTITIES ==================
    # Core Entities
    "FlextAPIPipeline"
    # Request/Response Entities
    "FlextAPIRequest"
    "FlextApiEndpoint"
    "FlextApiRequest"
    "FlextApiResponse"
    # ================== ENUMERATIONS ==================
    "HttpMethod"
    "Pipeline"
    "PipelineExecution"
    # Identifiers
    "PipelineId"
    "PipelineStatus"
    "Plugin"
    "PluginId"
    # Metadata and Support
    "PluginMetadata"
    "PluginType"
    "RateLimit"
    "RequestId"
    "RequestTimeout",
]
