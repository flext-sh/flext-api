"""Constants and enumerations for flext-api domain.

All constant values, literals, and enums are centralized here following FLEXT standards.
Only constants and enums - no functions or classes with behavior.
"""

from __future__ import annotations

from typing import ClassVar, Final

from flext_core import FlextConstants, FlextTypes


class FlextApiConstants(FlextConstants):
    """Flext constants extending flext-core FlextConstants."""

    # Client configuration
    DEFAULT_TIMEOUT: ClassVar[int] = FlextConstants.Network.DEFAULT_TIMEOUT
    DEFAULT_MAX_RETRIES: ClassVar[int] = FlextConstants.Reliability.MAX_RETRY_ATTEMPTS
    DEFAULT_BASE_URL: ClassVar[str] = (
        f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
    )
    API_VERSION: ClassVar[str] = "v1"

    # Pagination constants
    DEFAULT_PAGE_SIZE: ClassVar[int] = (
        FlextConstants.Processing.DEFAULT_BATCH_SIZE // 5
    )  # 200
    MIN_PAGE_SIZE: ClassVar[int] = FlextConstants.Pagination.MIN_PAGE_SIZE
    MAX_PAGE_SIZE: ClassVar[int] = FlextConstants.Pagination.MAX_PAGE_SIZE
    MAX_PAGE_SIZE_PERFORMANCE: ClassVar[int] = FlextConstants.Pagination.MAX_PAGE_SIZE

    # HTTP constants moved to flext-core.FlextConstants.Http
    # Use FlextConstants.Http.HTTP_OK, FlextConstants.Http.HTTP_SUCCESS_MIN, etc.
    # Use FlextConstants.Http.Method.GET, FlextConstants.Http.Method.POST, etc.
    # Use FlextConstants.Http.ContentType.JSON, etc.

    # CORS constants
    DEFAULT_CORS_ORIGINS: ClassVar[FlextTypes.StringList] = ["*"]
    DEFAULT_CORS_METHODS: ClassVar[FlextTypes.StringList] = [
        FlextConstants.Http.Method.GET,
        FlextConstants.Http.Method.POST,
        FlextConstants.Http.Method.PUT,
        FlextConstants.Http.Method.DELETE,
    ]
    DEFAULT_CORS_HEADERS: ClassVar[FlextTypes.StringList] = [
        FlextConstants.Platform.HEADER_CONTENT_TYPE,
        FlextConstants.Platform.HEADER_AUTHORIZATION,
    ]

    # API-specific response templates (not in flext-core)
    SUCCESS_RESPONSE_TEMPLATE: ClassVar[dict[str, str | FlextTypes.Dict] | None] = None
    ERROR_RESPONSE_TEMPLATE: ClassVar[dict[str, str | FlextTypes.Dict] | None] = None

    @classmethod
    def get_success_template(cls) -> dict[str, str | FlextTypes.Dict]:
        """Get success response template."""
        if cls.SUCCESS_RESPONSE_TEMPLATE is None:
            cls.SUCCESS_RESPONSE_TEMPLATE = {
                "status": "success",
                "data": {},
            }
        return cls.SUCCESS_RESPONSE_TEMPLATE

    @classmethod
    def get_error_template(cls) -> dict[str, str | FlextTypes.Dict]:
        """Get error response template."""
        if cls.ERROR_RESPONSE_TEMPLATE is None:
            cls.ERROR_RESPONSE_TEMPLATE = {
                "status": "error",
                "data": {},
            }
        return cls.ERROR_RESPONSE_TEMPLATE

    # API-specific header defaults (customize flext-core defaults)
    DEFAULT_USER_AGENT: ClassVar[str] = "FlextAPI/0.9.0"
    USER_AGENT_HEADER: ClassVar[str] = "User-Agent"

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
    HTTP_PORT: ClassVar[int] = 80
    HTTPS_PORT: ClassVar[int] = 443

    # Security constants
    MASK_AUTH_THRESHOLD: ClassVar[int] = 8

    # HTTP constants (API-specific extensions)
    HTTP_DEFAULT_ACCEPT: ClassVar[str] = "application/json"

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
    # TIME CONSTANTS - HTTP-specific time calculations
    # =============================================================================

    class TimeConstants:
        """Time-related constants for HTTP operations."""

        SECONDS_PER_MINUTE: Final[int] = 60
        SECONDS_PER_HOUR: Final[int] = 3600

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

    # =============================================================================
    # ERROR CODES - API-specific error codes
    # =============================================================================

    class Errors:
        """API-specific error codes."""

        MIDDLEWARE_ERROR = "MIDDLEWARE_ERROR"
        PROTOCOL_ERROR = "PROTOCOL_ERROR"
        HTTP_ERROR = "HTTP_ERROR"
        CONNECTION_ERROR = "CONNECTION_ERROR"
        TIMEOUT_ERROR = "TIMEOUT_ERROR"
        VALIDATION_ERROR = "VALIDATION_ERROR"
        CONFIG_ERROR = "CONFIG_ERROR"


__all__ = ["FlextApiConstants"]
