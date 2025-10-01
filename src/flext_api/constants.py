"""Constants and enumerations for flext-api domain.

All constant values, literals, and enums are centralized here following FLEXT standards.
Only constants and enums - no functions or classes with behavior.
"""

from __future__ import annotations

from typing import ClassVar

from flext_core import FlextConstants


class FlextApiConstants(FlextConstants):
    """API-specific constants extending flext-core FlextConstants."""

    # Client configuration
    DEFAULT_TIMEOUT: ClassVar[int] = FlextConstants.Network.DEFAULT_TIMEOUT
    DEFAULT_MAX_RETRIES: ClassVar[int] = FlextConstants.Reliability.MAX_RETRY_ATTEMPTS
    DEFAULT_BASE_URL: ClassVar[str] = (
        f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
    )
    API_VERSION: ClassVar[str] = "v1"

    # Environment-specific timeouts
    PRODUCTION_TIMEOUT: ClassVar[int] = FlextConstants.Network.DEFAULT_TIMEOUT
    DEVELOPMENT_TIMEOUT: ClassVar[int] = FlextConstants.Network.DEFAULT_TIMEOUT * 2
    TESTING_TIMEOUT: ClassVar[int] = FlextConstants.Network.DEFAULT_TIMEOUT // 3
    MONITORING_TIMEOUT: ClassVar[int] = FlextConstants.Network.DEFAULT_TIMEOUT // 6

    # Pagination constants
    DEFAULT_PAGE_SIZE: ClassVar[int] = 20
    MIN_PAGE_SIZE: ClassVar[int] = 1
    MAX_PAGE_SIZE: ClassVar[int] = 1000
    MAX_PAGE_SIZE_PERFORMANCE: ClassVar[int] = 1000

    # HTTP constants moved to flext-core.FlextConstants.Http
    # Use FlextConstants.Http.HTTP_OK, FlextConstants.Http.HTTP_SUCCESS_MIN, etc.
    # Use FlextConstants.Http.Method.GET, FlextConstants.Http.Method.POST, etc.
    # Use FlextConstants.Http.ContentType.JSON, etc.

    # API-specific response templates (not in flext-core)
    SUCCESS_RESPONSE_TEMPLATE: ClassVar[dict[str, str | dict[str, object]]] = {
        "status": "success",
        "data": {},
    }
    ERROR_RESPONSE_TEMPLATE: ClassVar[dict[str, str | dict[str, object]]] = {
        "status": "error",
        "data": {},
    }

    # API-specific header defaults (customize flext-core defaults)
    DEFAULT_USER_AGENT: ClassVar[str] = "FlextAPI/0.9.0"

    # Timeout constants
    MIN_TIMEOUT: ClassVar[float] = 0.0
    MAX_TIMEOUT: ClassVar[float] = 300.0

    # Retry constants
    MIN_RETRIES: ClassVar[int] = 0
    MAX_RETRIES: ClassVar[int] = 10
    MAX_RETRIES_PRODUCTION: ClassVar[int] = 10
    DEFAULT_RETRIES: ClassVar[int] = 3

    # Rate limiting constants
    RATE_LIMIT_REQUESTS: ClassVar[int] = 1000
    RATE_LIMIT_WINDOW: ClassVar[int] = 3600  # 1 hour in seconds

    # URL validation
    MAX_URL_LENGTH: ClassVar[int] = 2048
    MAX_HOSTNAME_LENGTH: ClassVar[int] = 253  # RFC 1035 max hostname length
    MIN_PORT: ClassVar[int] = 1
    MAX_PORT: ClassVar[int] = 65535

    # Security constants
    MASK_AUTH_THRESHOLD: ClassVar[int] = 8

    # =============================================================================
    # HTTP METHOD CONSTANTS - Moved to flext-core.FlextConstants.Http.Method
    # Use FlextConstants.Http.Method.GET, etc.
    # =============================================================================

    # =============================================================================
    # CLIENT STATUS CONSTANTS - Consolidated from single-class modules
    # =============================================================================

    class ClientStatus:
        """Client status constants for API operations."""

        IDLE = "idle"
        CONNECTING = "connecting"
        CONNECTED = "connected"
        DISCONNECTING = "disconnecting"
        DISCONNECTED = "disconnected"
        ERROR = "error"

    # =============================================================================
    # REQUEST STATUS CONSTANTS - Consolidated from single-class modules
    # =============================================================================

    class RequestStatus:
        """Request status constants for API operations."""

        PENDING = "pending"
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"
        FAILED = "failed"
        CANCELLED = "cancelled"
        TIMEOUT = "timeout"

    # =============================================================================
    # SERVICE STATUS CONSTANTS - Consolidated from single-class modules
    # =============================================================================

    class ServiceStatus:
        """Service status constants for API operations."""

        STARTING = "starting"
        RUNNING = "running"
        STOPPING = "stopping"
        STOPPED = "stopped"
        ERROR = "error"
        MAINTENANCE = "maintenance"

    # =============================================================================
    # CONTENT TYPE CONSTANTS - Moved to flext-core.FlextConstants.Http.ContentType
    # Use FlextConstants.Http.ContentType.JSON, etc.
    # =============================================================================

    # =============================================================================
    # STORAGE BACKEND CONSTANTS - Consolidated from single-class modules
    # =============================================================================

    class StorageBackend:
        """Storage backend constants for API operations."""

        MEMORY = "memory"
        REDIS = "redis"
        DATABASE = "database"
        FILE = "file"
        CACHE = "cache"

    # =============================================================================
    # AUTHENTICATION TYPE CONSTANTS - Consolidated from single-class modules
    # =============================================================================

    class AuthenticationType:
        """Authentication type constants for API operations."""

        NONE = "none"
        BASIC = "basic"
        BEARER = "bearer"
        API_KEY = "api_key"
        OAUTH2 = "oauth2"
        JWT = "jwt"

    # =============================================================================
    # CACHE STRATEGY CONSTANTS - Consolidated from single-class modules
    # =============================================================================

    class CacheStrategy:
        """Cache strategy constants for API operations."""

        NONE = "none"
        MEMORY = "memory"
        REDIS = "redis"
        LRU = "lru"
        TTL = "ttl"
        WRITE_THROUGH = "write_through"
        WRITE_BACK = "write_back"

    # =============================================================================
    # LOGGING CONSTANTS - Consolidated from single-class modules
    # =============================================================================

    class LoggingConstants:
        """Logging constants for API operations."""

        REQUEST_LOG_FORMAT = "Request: {method} {url} - Status: {status_code} - Duration: {duration_ms}ms"
        RESPONSE_LOG_FORMAT = "Response: {status_code} - Size: {size_bytes} bytes"
        ERROR_LOG_FORMAT = (
            "Error: {error_type} - Message: {message} - Traceback: {traceback}"
        )
        DEBUG_LOG_FORMAT = "Debug: {component} - {message} - Data: {data}"


__all__ = ["FlextApiConstants"]
