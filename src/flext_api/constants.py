"""Constants and enumerations for flext-api domain.

All constant values, literals, and enums are centralized here following FLEXT standards.
Only constants and enums - no functions or classes with behavior.
"""

from enum import StrEnum
from typing import ClassVar

from flext_core import FlextConstants


class FlextApiConstants(FlextConstants):
    """HTTP API constants extending flext-core constants."""

    # HTTP Status Codes
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

    # HTTP Status Ranges
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

    # Default Configuration Values
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_RETRIES = 3
    DEFAULT_BASE_URL = "http://127.0.0.1:8000"
    DEFAULT_USER_AGENT = "FlextAPI/1.0.0"
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 1000
    MIN_PAGE_SIZE = 1

    # Network and Port Limits
    MIN_PORT = 1
    MAX_PORT = 65535
    MAX_HOSTNAME_LENGTH = 253
    MAX_URL_LENGTH = 2048

    # Rate Limiting
    RATE_LIMIT_REQUESTS = 1000
    RATE_LIMIT_WINDOW = 3600

    # Validation Limits
    MIN_TIMEOUT = 0.1
    MAX_TIMEOUT = 300.0
    MIN_RETRIES = 0
    MAX_RETRIES = 10

    # Content Types
    JSON_CONTENT_TYPE = "application/json"
    XML_CONTENT_TYPE = "application/xml"
    TEXT_CONTENT_TYPE = "text/plain"
    HTML_CONTENT_TYPE = "text/html"
    FORM_CONTENT_TYPE = "application/x-www-form-urlencoded"
    MULTIPART_CONTENT_TYPE = "multipart/form-data"

    # HTTP Headers
    CONTENT_TYPE_HEADER = "Content-Type"
    AUTHORIZATION_HEADER = "Authorization"
    USER_AGENT_HEADER = "User-Agent"
    ACCEPT_HEADER = "Accept"
    CACHE_CONTROL_HEADER = "Cache-Control"
    ETAG_HEADER = "ETag"

    # API Endpoints
    API_V1_PREFIX = "/api/v1"
    HEALTH_ENDPOINT = "/health"
    METRICS_ENDPOINT = "/metrics"
    DOCS_ENDPOINT = "/docs"
    REDOC_ENDPOINT = "/redoc"
    OPENAPI_ENDPOINT = "/openapi.json"

    # Authentication Endpoints
    AUTH_LOGIN_ENDPOINT = "/api/v1/auth/login"
    AUTH_LOGOUT_ENDPOINT = "/api/v1/auth/logout"
    AUTH_REFRESH_ENDPOINT = "/api/v1/auth/refresh"
    AUTH_VERIFY_ENDPOINT = "/api/v1/auth/verify"

    # Response Templates
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

    # Client Error Status Codes Set
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

    # Server Error Status Codes Set
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

    # Nested classes for backward compatibility with old structure
    class ApiLimits:
        """API pagination limits."""

        MAX_PAGE_SIZE = 1000
        MIN_PAGE_SIZE = 1
        DEFAULT_PAGE_SIZE = 20

    class FlextApiEndpoints:
        """API endpoint constants."""

        API_V1 = "/api/v1"
        HEALTH = "/health"
        METRICS = "/metrics"
        DOCS = "/docs"

    class FlextApiFieldType:
        """API field types."""

        API_KEY = "api_key"
        BEARER_TOKEN = "bearer_token"

    class FlextApiStatus:
        """API status values."""

        PENDING = "pending"
        PROCESSING = "processing"
        COMPLETED = "completed"
        FAILED = "failed"


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


__all__ = [
    "AuthenticationType",
    "CacheStrategy",
    "ClientStatus",
    "ContentType",
    "FlextApiConstants",
    "HttpMethod",
    "RequestStatus",
    "ServiceStatus",
    "StorageBackend",
]
