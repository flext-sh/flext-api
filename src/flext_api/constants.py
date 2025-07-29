"""FLEXT-API Constants - Domain-specific constants WITHOUT duplicating flext-core.

This module provides ONLY API-specific constants that extend flext-core's
robust constants system without re-exporting base constants.
"""

from __future__ import annotations

from typing import Final

# ==============================================================================
# API-SPECIFIC CONSTANTS - NO FLEXT-CORE DUPLICATIONS
# ==============================================================================

# API version and timeout settings
FLEXT_API_VERSION: Final[str] = "1.0.0"
FLEXT_API_TIMEOUT: Final[int] = 30
FLEXT_API_MAX_RETRIES: Final[int] = 3
FLEXT_API_CACHE_TTL: Final[int] = 300  # 5 minutes

# Authentication constants
FLEXT_AUTH_TOKEN_EXPIRY: Final[int] = 3600  # 1 hour
FLEXT_AUTH_REFRESH_THRESHOLD: Final[int] = 300  # 5 minutes

# Pipeline constants
FLEXT_PIPELINE_MAX_STEPS: Final[int] = 100
FLEXT_PIPELINE_TIMEOUT: Final[int] = 1800  # 30 minutes

# Plugin constants
FLEXT_PLUGIN_TIMEOUT: Final[int] = 60
FLEXT_PLUGIN_MAX_MEMORY: Final[int] = 512  # MB


class FlextApiConstants:
    """API-specific constants that don't exist in flext-core."""

    # HTTP status groups
    SUCCESS_CODES = [200, 201, 202, 204]
    CLIENT_ERROR_CODES = [400, 401, 403, 404, 422]
    SERVER_ERROR_CODES = [500, 502, 503, 504]

    # Rate limiting
    RATE_LIMIT_REQUESTS = 1000
    RATE_LIMIT_WINDOW = 3600  # 1 hour

    # API response formats
    SUCCESS_RESPONSE = {"status": "success", "data": None, "error": None}
    ERROR_RESPONSE = {"status": "error", "data": None, "error": None}

    # Validation patterns
    UUID_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    USERNAME_PATTERN = r"^[a-zA-Z0-9_]{3,50}$"
    PIPELINE_NAME_PATTERN = r"^[a-zA-Z0-9_-]{1,100}$"


class FlextApiFieldType:
    """API-specific field types that don't exist in flext-core."""

    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    PIPELINE_CONFIG = "pipeline_config"
    PLUGIN_CONFIG = "plugin_config"
    USER_ROLE = "user_role"
    ENDPOINT_PATH = "endpoint_path"
    HTTP_METHOD = "http_method"
    RESPONSE_FORMAT = "response_format"


class FlextApiStatus:
    """API operation status constants."""

    # Request status
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    # Service status
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"

    # Pipeline status
    PIPELINE_IDLE = "idle"
    PIPELINE_RUNNING = "running"
    PIPELINE_SUCCESS = "success"
    PIPELINE_ERROR = "error"
    PIPELINE_TIMEOUT = "timeout"

    # Plugin status
    PLUGIN_LOADED = "loaded"
    PLUGIN_ACTIVE = "active"
    PLUGIN_INACTIVE = "inactive"
    PLUGIN_ERROR = "error"


class FlextApiEndpoints:
    """API endpoint constants."""

    # Base paths
    API_V1 = "/api/v1"
    HEALTH = "/health"
    METRICS = "/metrics"
    DOCS = "/docs"

    # Authentication endpoints
    AUTH_LOGIN = f"{API_V1}/auth/login"
    AUTH_LOGOUT = f"{API_V1}/auth/logout"
    AUTH_REFRESH = f"{API_V1}/auth/refresh"
    AUTH_VERIFY = f"{API_V1}/auth/verify"

    # Pipeline endpoints
    PIPELINES = f"{API_V1}/pipelines"
    PIPELINE_RUN = f"{API_V1}/pipelines/{{pipeline_id}}/run"
    PIPELINE_STATUS = f"{API_V1}/pipelines/{{pipeline_id}}/status"
    PIPELINE_LOGS = f"{API_V1}/pipelines/{{pipeline_id}}/logs"

    # Plugin endpoints
    PLUGINS = f"{API_V1}/plugins"
    PLUGIN_INSTALL = f"{API_V1}/plugins/install"
    PLUGIN_UNINSTALL = f"{API_V1}/plugins/{{plugin_id}}/uninstall"
    PLUGIN_CONFIG = f"{API_V1}/plugins/{{plugin_id}}/config"


# ==============================================================================
# EXPORTS - ONLY API-SPECIFIC CONSTANTS
# ==============================================================================

__all__ = [
    "FLEXT_API_CACHE_TTL",
    "FLEXT_API_MAX_RETRIES",
    "FLEXT_API_TIMEOUT",
    # Constants
    "FLEXT_API_VERSION",
    "FLEXT_AUTH_REFRESH_THRESHOLD",
    "FLEXT_AUTH_TOKEN_EXPIRY",
    "FLEXT_PIPELINE_MAX_STEPS",
    "FLEXT_PIPELINE_TIMEOUT",
    "FLEXT_PLUGIN_MAX_MEMORY",
    "FLEXT_PLUGIN_TIMEOUT",
    # Classes
    "FlextApiConstants",
    "FlextApiEndpoints",
    "FlextApiFieldType",
    "FlextApiStatus",
]
