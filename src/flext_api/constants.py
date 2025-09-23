"""Constants and enumerations for flext-api domain.

All constant values, literals, and enums are centralized here following FLEXT standards.
Only constants and enums - no functions or classes with behavior.
"""

from enum import StrEnum
from typing import ClassVar

from flext_core import FlextConstants


class FlextApiConstants(FlextConstants):
    """HTTP API constants extending flext-core constants."""

    HTTP_OK = 200
    HTTP_CREATED = 201
    HTTP_NO_CONTENT = 204
    HTTP_BAD_REQUEST = 400
    HTTP_UNAUTHORIZED = 401
    HTTP_FORBIDDEN = 403
    HTTP_NOT_FOUND = 404
    HTTP_METHOD_NOT_ALLOWED = 405
    HTTP_REQUEST_TIMEOUT = 408
    HTTP_CONFLICT = 409
    HTTP_TOO_MANY_REQUESTS = 429
    HTTP_INTERNAL_SERVER_ERROR = 500
    HTTP_BAD_GATEWAY = 502
    HTTP_SERVICE_UNAVAILABLE = 503
    HTTP_GATEWAY_TIMEOUT = 504

    HTTP_STATUS_MIN = 100
    HTTP_STATUS_MAX = 599
    HTTP_INFORMATIONAL_MIN = 100
    HTTP_INFORMATIONAL_MAX = 199
    HTTP_SUCCESS_MIN = 200
    HTTP_SUCCESS_MAX = 299
    HTTP_REDIRECTION_MIN = 300
    HTTP_REDIRECTION_MAX = 399
    HTTP_CLIENT_ERROR_MIN = 400
    HTTP_CLIENT_ERROR_MAX = 499
    HTTP_SERVER_ERROR_MIN = 500
    HTTP_SERVER_ERROR_MAX = 599

    DEFAULT_TIMEOUT = 30.0
    DEFAULT_RETRIES = 3
    DEFAULT_BASE_URL = "http://127.0.0.1:8000"
    DEFAULT_USER_AGENT = "FlextAPI/1.0.0"
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 1000
    MIN_PAGE_SIZE = 1

    MIN_PORT = 1
    MAX_PORT = 65535
    MAX_HOSTNAME_LENGTH = 253
    MAX_URL_LENGTH = 2048

    RATE_LIMIT_REQUESTS = 1000
    RATE_LIMIT_WINDOW = 3600

    MIN_TIMEOUT = 0.1
    MAX_TIMEOUT = 300.0
    MIN_RETRIES = 0
    MAX_RETRIES = 10

    JSON_CONTENT_TYPE = "application/json"
    XML_CONTENT_TYPE = "application/xml"
    TEXT_CONTENT_TYPE = "text/plain"
    HTML_CONTENT_TYPE = "text/html"
    FORM_CONTENT_TYPE = "application/x-www-form-urlencoded"
    MULTIPART_CONTENT_TYPE = "multipart/form-data"

    CONTENT_TYPE_HEADER = "Content-Type"
    AUTHORIZATION_HEADER = "Authorization"
    USER_AGENT_HEADER = "User-Agent"
    ACCEPT_HEADER = "Accept"
    CACHE_CONTROL_HEADER = "Cache-Control"
    ETAG_HEADER = "ETag"

    API_V1_PREFIX = "/api/v1"
    HEALTH_ENDPOINT = "/health"
    METRICS_ENDPOINT = "/metrics"
    DOCS_ENDPOINT = "/docs"
    REDOC_ENDPOINT = "/redoc"
    OPENAPI_ENDPOINT = "/openapi.json"

    AUTH_LOGIN_ENDPOINT = "/api/v1/auth/login"
    AUTH_LOGOUT_ENDPOINT = "/api/v1/auth/logout"
    AUTH_REFRESH_ENDPOINT = "/api/v1/auth/refresh"
    AUTH_VERIFY_ENDPOINT = "/api/v1/auth/verify"

    SUCCESS_RESPONSE_TEMPLATE: ClassVar[dict[str, object]] = {
        "status": "success",
        "data": None,
        "error": None,
    }

    ERROR_RESPONSE_TEMPLATE: ClassVar[dict[str, object]] = {
        "status": "error",
        "data": None,
        "error": None,
    }

    CLIENT_ERROR_CODES: ClassVar[set[int]] = {
        400,
        401,
        402,
        403,
        404,
        405,
        406,
        407,
        408,
        409,
        410,
        411,
        412,
        413,
        414,
        415,
        416,
        417,
        418,
        421,
        422,
        423,
        424,
        425,
        426,
        428,
        429,
        431,
        451,
    }

    SERVER_ERROR_CODES: ClassVar[set[int]] = {
        500,
        501,
        502,
        503,
        504,
        505,
        506,
        507,
        508,
        510,
        511,
    }

    API_KEY_FIELD_TYPE = "api_key"
    BEARER_TOKEN_FIELD_TYPE = "bearer_token"

    PENDING_STATUS = "pending"
    PROCESSING_STATUS = "processing"
    COMPLETED_STATUS = "completed"
    FAILED_STATUS = "failed"

    class HttpMethod(StrEnum):
        """HTTP method enumeration."""

        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"
        PATCH = "PATCH"
        HEAD = "HEAD"
        OPTIONS = "OPTIONS"
        TRACE = "TRACE"
        CONNECT = "CONNECT"
        # WebDAV methods
        PROPFIND = "PROPFIND"
        COPY = "COPY"
        MOVE = "MOVE"
        LOCK = "LOCK"

    class ClientStatus(StrEnum):
        """HTTP client status enumeration."""

        IDLE = "idle"
        ACTIVE = "active"
        CONNECTING = "connecting"
        CONNECTED = "connected"
        DISCONNECTED = "disconnected"
        ERROR = "error"

    class RequestStatus(StrEnum):
        """HTTP request status enumeration."""

        PENDING = "pending"
        PROCESSING = "processing"
        COMPLETED = "completed"
        FAILED = "failed"
        CANCELLED = "cancelled"
        TIMEOUT = "timeout"

    class ServiceStatus(StrEnum):
        """Service health status enumeration."""

        HEALTHY = "healthy"
        DEGRADED = "degraded"
        UNHEALTHY = "unhealthy"
        MAINTENANCE = "maintenance"
        STARTING = "starting"
        STOPPING = "stopping"

    class ContentType(StrEnum):
        """Content type enumeration."""

        JSON = "application/json"
        XML = "application/xml"
        TEXT = "text/plain"
        HTML = "text/html"
        FORM = "application/x-www-form-urlencoded"
        MULTIPART = "multipart/form-data"
        OCTET_STREAM = "application/octet-stream"

    class StorageBackend(StrEnum):
        """Storage backend type enumeration."""

        MEMORY = "memory"
        FILE = "file"
        REDIS = "redis"
        DATABASE = "database"
        S3 = "s3"
        GCS = "gcs"

    class AuthenticationType(StrEnum):
        """Authentication type enumeration."""

        BEARER = "bearer"
        BASIC = "basic"
        API_KEY = "api_key"
        OAUTH2 = "oauth2"
        JWT = "jwt"

    class CacheStrategy(StrEnum):
        """Cache strategy enumeration."""

        NO_CACHE = "no_cache"
        MEMORY = "memory"
        REDIS = "redis"
        LRU = "lru"
        TTL = "ttl"

    class Logging:
        """API-specific logging constants for FLEXT API module.

        Provides domain-specific logging defaults, levels, and configuration
        options tailored for API operations, request/response logging, and
        API performance monitoring.
        """

        DEFAULT_LEVEL = "INFO"
        REQUEST_LEVEL = "INFO"
        RESPONSE_LEVEL = "INFO"
        ERROR_LEVEL = "ERROR"
        PERFORMANCE_LEVEL = "WARNING"
        SECURITY_LEVEL = "WARNING"

        LOG_REQUESTS = True
        LOG_RESPONSES = True
        LOG_REQUEST_BODY = False
        LOG_RESPONSE_BODY = False
        LOG_REQUEST_HEADERS = True
        LOG_RESPONSE_HEADERS = False
        LOG_QUERY_PARAMETERS = True
        LOG_PATH_PARAMETERS = True

        TRACK_API_PERFORMANCE = True
        API_PERFORMANCE_THRESHOLD_WARNING = 1000.0
        API_PERFORMANCE_THRESHOLD_CRITICAL = 5000.0
        TRACK_RESPONSE_SIZE = True
        LARGE_RESPONSE_THRESHOLD = 1024 * 1024

        LOG_AUTHENTICATION_HEADERS = False
        LOG_SENSITIVE_HEADERS = False
        MASK_API_KEYS = True
        MASK_AUTHORIZATION_HEADERS = True
        LOG_RATE_LIMITING = True
        LOG_ACCESS_CONTROL = True

        LOG_4XX_ERRORS = True
        LOG_5XX_ERRORS = True
        LOG_VALIDATION_ERRORS = True
        LOG_BUSINESS_LOGIC_ERRORS = True
        LOG_EXTERNAL_SERVICE_ERRORS = True

        INCLUDE_REQUEST_ID = True
        INCLUDE_CORRELATION_ID = True
        INCLUDE_USER_ID = True
        INCLUDE_CLIENT_IP = True
        INCLUDE_USER_AGENT = False
        INCLUDE_API_VERSION = True
        INCLUDE_ENDPOINT = True

        ENABLE_API_AUDIT_LOGGING = True
        AUDIT_LOG_LEVEL = "INFO"
        AUDIT_LOG_FILE = "flext_api_audit.log"

        REQUEST_RECEIVED = "API request received: {method} {endpoint} from {client_ip}"
        REQUEST_PROCESSING = "Processing API request: {request_id} {method} {endpoint}"
        RESPONSE_SENT = (
            "API response sent: {status_code} {method} {endpoint} in {duration}ms"
        )
        REQUEST_COMPLETED = "API request completed: {request_id} {status_code} {duration}ms"

        REQUEST_ERROR = "API request error: {error} for {method} {endpoint}"
        VALIDATION_ERROR = "API validation error: {error} for {method} {endpoint}"
        BUSINESS_LOGIC_ERROR = "API business logic error: {error} for {method} {endpoint}"
        EXTERNAL_SERVICE_ERROR = "External service error: {error} for {method} {endpoint}"

        SLOW_REQUEST = "Slow API request: {method} {endpoint} took {duration}ms"
        LARGE_RESPONSE = "Large API response: {method} {endpoint} {size} bytes"
        HIGH_MEMORY_USAGE = (
            "High memory usage for API request: {method} {endpoint} {memory}MB"
        )

        UNAUTHORIZED_ACCESS = (
            "Unauthorized API access attempt: {method} {endpoint} from {client_ip}"
        )
        RATE_LIMIT_EXCEEDED = "Rate limit exceeded: {client_ip} for {method} {endpoint}"
        SUSPICIOUS_REQUEST = "Suspicious API request: {method} {endpoint} from {client_ip}"

        AUTH_REQUIRED = "Authentication required for API request: {method} {endpoint}"
        AUTH_SUCCESS = "API authentication successful: {user_id} for {method} {endpoint}"
        AUTH_FAILED = "API authentication failed: {reason} for {method} {endpoint}"

        SERVICE_STARTED = "API service started on {host}:{port}"
        SERVICE_STOPPED = "API service stopped"
        SERVICE_ERROR = "API service error: {error}"
        HEALTH_CHECK = "API health check: {status}"

        MIDDLEWARE_PROCESSING = (
            "Middleware processing: {middleware} for {method} {endpoint}"
        )
        MIDDLEWARE_ERROR = "Middleware error: {middleware} {error} for {method} {endpoint}"


__all__ = [
]
