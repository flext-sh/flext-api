"""Constants for FLEXT API module.

This module defines centralized constants following the ``FlextConstants``
pattern from ``flext-core``, extending it with API-specific constants and
exporting convenience values used across the codebase and tests.
"""

from __future__ import annotations

from typing import ClassVar as _ClassVar

from flext_core import FlextConstants


class FlextApiConstants(FlextConstants):
    """Central container for API-specific constants.

    Follows the same pattern as FlextConstants from flext-core,
    organizing constants into logical categories with type safety.
    """

    class HTTP:
        """HTTP protocol constants."""

        # Status Code Ranges
        SUCCESS_MIN = 200
        SUCCESS_MAX = 300
        CLIENT_ERROR_MIN = 400
        CLIENT_ERROR_MAX = 500
        SERVER_ERROR_MIN = 500
        SERVER_ERROR_MAX = 600

        # Common Status Codes
        OK = 200
        CREATED = 201
        NO_CONTENT = 204
        BAD_REQUEST = 400
        UNAUTHORIZED = 401
        FORBIDDEN = 403
        NOT_FOUND = 404
        INTERNAL_SERVER_ERROR = 500
        SERVICE_UNAVAILABLE = 503

        # Headers
        CONTENT_TYPE = "Content-Type"
        AUTHORIZATION = "Authorization"
        USER_AGENT = "User-Agent"
        ACCEPT = "Accept"

    class ContentTypes:
        """Standard HTTP content types."""

        JSON = "application/json"
        HTML = "text/html"

    class Config:
        """API configuration defaults."""

        # Timeouts
        DEFAULT_TIMEOUT = FlextConstants.Defaults.TIMEOUT
        CONNECTION_TIMEOUT = FlextConstants.Defaults.CONNECTION_TIMEOUT
        READ_TIMEOUT = FlextConstants.Platform.HTTP_READ_TIMEOUT

        # Retries
        DEFAULT_MAX_RETRIES = 3
        RETRY_BACKOFF_FACTOR = 2.0
        RETRY_MAX_WAIT = 60
        MAX_RETRIES = 10  # Maximum allowable retries for external APIs

        # Pagination
        DEFAULT_PAGE_SIZE = 50
        MAX_PAGE_SIZE = 1000
        DEFAULT_BATCH_SIZE = 100

    class RateLimit:
        """Rate limiting configuration."""

        DEFAULT_RATE_LIMIT = 100  # requests per minute
        RATE_LIMIT_WINDOW = 60  # seconds
        BURST_SIZE = 10  # additional requests allowed in burst

    class ApiCache:
        """Cache configuration."""

        DEFAULT_TTL = 300  # 5 minutes
        MAX_SIZE = 1000
        CLEANUP_INTERVAL = 600  # 10 minutes

    class ApiValidation:
        """Validation limits and constraints."""

        MAX_REQUEST_SIZE = 10485760  # 10MB
        MAX_RESPONSE_SIZE = 52428800  # 50MB
        MIN_PORT = 1
        MAX_PORT = 65535
        MAX_URL_LENGTH = 2048
        MAX_HEADER_SIZE = 8192
        MAX_ERROR_VALUE_LENGTH = 100  # Truncate error values for security

    class ApiAuth:
        """Authentication and token constants."""

        JWT_PARTS_COUNT = 3  # JWT has 3 parts: header.payload.signature
        JWT_SEPARATOR_COUNT = 2  # JWT has 2 dots separating 3 parts
        MIN_TOKEN_LENGTH = 16  # Minimum viable token length

    class Connection:
        """Connection pool settings."""

        POOL_SIZE = 10
        MAX_CONNECTIONS = 100
        KEEP_ALIVE_TIMEOUT = 120  # seconds
        IDLE_TIMEOUT = 300  # seconds
        PRIVILEGED_PORT_LIMIT = 1024  # Ports below this require elevated privileges

    class ApiDatabase:
        """Database configuration limits."""

        MAX_POOL_SIZE = 50  # Maximum database connection pool size

    class ApiPerformance:
        """Performance monitoring thresholds."""

        SLOW_REQUEST_THRESHOLD = 3.0  # seconds
        CRITICAL_LATENCY_THRESHOLD = 10.0  # seconds
        MONITORING_SAMPLE_RATE = 0.1  # 10% sampling

    # ----------------------------------------------------------------------------
    # Derived/public constants used by tests and public API
    # ----------------------------------------------------------------------------
    # Success (2xx), client error (4xx), and server error (5xx) ranges
    SUCCESS_CODES: _ClassVar[set[int]] = set(range(200, 300))
    CLIENT_ERROR_CODES: _ClassVar[set[int]] = set(range(400, 500))
    SERVER_ERROR_CODES: _ClassVar[set[int]] = set(range(500, 600))

    # Rate limiting public constants expected by tests
    RATE_LIMIT_REQUESTS: int = 1000
    RATE_LIMIT_WINDOW: int = 3600  # seconds (1 hour)

    # Response templates
    SUCCESS_RESPONSE: _ClassVar[dict[str, object | None]] = {
        "status": "success",
        "data": None,
        "error": None,
    }
    ERROR_RESPONSE: _ClassVar[dict[str, object | None]] = {
        "status": "error",
        "data": None,
        "error": None,
    }


class FlextApiStatus:
    """Domain status constants for requests, services, pipelines and plugins."""

    # Request lifecycle
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    # Service health
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"

    # Pipeline states
    PIPELINE_IDLE = "idle"
    PIPELINE_RUNNING = "running"
    PIPELINE_SUCCESS = "success"
    PIPELINE_ERROR = "error"
    PIPELINE_TIMEOUT = "timeout"

    # Plugin lifecycle
    PLUGIN_LOADED = "loaded"
    PLUGIN_ACTIVE = "active"
    PLUGIN_INACTIVE = "inactive"
    PLUGIN_ERROR = "error"


class FlextApiFieldType:
    """API-specific field type identifiers (string constants)."""

    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"  # noqa: S105
    PIPELINE_CONFIG = "pipeline_config"
    PLUGIN_CONFIG = "plugin_config"
    USER_ROLE = "user_role"
    ENDPOINT_PATH = "endpoint_path"
    HTTP_METHOD = "http_method"
    RESPONSE_FORMAT = "response_format"


class FlextApiEndpoints:
    """HTTP endpoint path constants for the public API."""

    # Base paths
    API_V1 = "/api/v1"
    HEALTH = "/health"
    METRICS = "/metrics"
    DOCS = "/docs"

    # Auth
    AUTH_LOGIN = f"{API_V1}/auth/login"
    AUTH_LOGOUT = f"{API_V1}/auth/logout"
    AUTH_REFRESH = f"{API_V1}/auth/refresh"
    AUTH_VERIFY = f"{API_V1}/auth/verify"

    # Pipelines
    PIPELINES = f"{API_V1}/pipelines"
    PIPELINE_RUN = f"{API_V1}/pipelines/{{pipeline_id}}/run"
    PIPELINE_STATUS = f"{API_V1}/pipelines/{{pipeline_id}}/status"
    PIPELINE_LOGS = f"{API_V1}/pipelines/{{pipeline_id}}/logs"

    # Plugins
    PLUGINS = f"{API_V1}/plugins"
    PLUGIN_INSTALL = f"{API_V1}/plugins/install"
    PLUGIN_UNINSTALL = f"{API_V1}/plugins/{{plugin_id}}/uninstall"
    PLUGIN_CONFIG = f"{API_V1}/plugins/{{plugin_id}}/config"


# ----------------------------------------------------------------------------
# Top-level constants expected by tests
# ----------------------------------------------------------------------------
# Version is kept in sync with project metadata. Tests expect 0.9.0 here.
FLEXT_API_VERSION: str = "0.9.0"

# Configuration shortcuts
FLEXT_API_TIMEOUT: int = int(FlextApiConstants.Config.DEFAULT_TIMEOUT)
FLEXT_API_MAX_RETRIES: int = int(FlextApiConstants.Config.DEFAULT_MAX_RETRIES)
FLEXT_API_CACHE_TTL: int = int(FlextApiConstants.ApiCache.DEFAULT_TTL)


__all__ = [
    "FLEXT_API_CACHE_TTL",
    "FLEXT_API_MAX_RETRIES",
    "FLEXT_API_TIMEOUT",
    "FLEXT_API_VERSION",
    "FlextApiConstants",
    "FlextApiEndpoints",
    "FlextApiFieldType",
    "FlextApiStatus",
]


# ----------------------------------------------------------------------------
# Legacy aliases - Deprecated classes redirected to FlextApiConstants
# ----------------------------------------------------------------------------

# Validation constants aliases
Validation = FlextApiConstants.ApiValidation

# Auth constants aliases
Auth = FlextApiConstants.ApiAuth

# Connection constants aliases
Connection = FlextApiConstants.Connection

# Performance constants aliases
Performance = FlextApiConstants.ApiPerformance
