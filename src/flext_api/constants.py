"""Constants and enumerations for flext-api domain.

All constant values, literals, and enums are centralized here following FLEXT standards.
Only constants and enums - no functions or classes with behavior.
"""

from __future__ import annotations

from enum import StrEnum
from typing import ClassVar, Literal

from flext_core import FlextConstants

# Unit type for operations that return no data (replaces None in FlextResult)
Unit = Literal[True]


class FlextApiConstants:
    """Flext constants for API domain functionality using composition."""

    # Core composition - inherit all core constants
    CoreErrors = FlextConstants.Errors
    CoreNetwork = FlextConstants.Network
    CoreReliability = FlextConstants.Reliability
    CorePlatform = FlextConstants.Platform
    CoreProcessing = FlextConstants.Processing
    CorePagination = FlextConstants.Pagination

    # Client configuration with core composition
    DEFAULT_TIMEOUT: ClassVar[int] = CoreNetwork.DEFAULT_TIMEOUT
    DEFAULT_MAX_RETRIES: ClassVar[int] = CoreReliability.MAX_RETRY_ATTEMPTS
    DEFAULT_BASE_URL: ClassVar[str] = (
        f"http://{CorePlatform.DEFAULT_HOST}:{CorePlatform.FLEXT_API_PORT}"
    )
    API_VERSION: ClassVar[str] = "v1"

    # HTTP Methods - compact tuple definition
    class Method:
        """HTTP method constants."""

        GET: ClassVar[str] = "GET"
        POST: ClassVar[str] = "POST"
        PUT: ClassVar[str] = "PUT"
        DELETE: ClassVar[str] = "DELETE"
        PATCH: ClassVar[str] = "PATCH"
        HEAD: ClassVar[str] = "HEAD"
        OPTIONS: ClassVar[str] = "OPTIONS"
        CONNECT: ClassVar[str] = "CONNECT"
        TRACE: ClassVar[str] = "TRACE"

    # URL and validation constants
    MAX_URL_LENGTH: ClassVar[int] = 2048
    MIN_URL_LENGTH: ClassVar[int] = 8
    MIN_PORT: ClassVar[int] = 1
    MAX_PORT: ClassVar[int] = 65535

    # Retry and reliability constants
    BACKOFF_FACTOR: ClassVar[float] = 0.5
    HTTP_SUCCESS_MIN: ClassVar[int] = 200
    HTTP_SUCCESS_MAX: ClassVar[int] = 300
    HTTP_REDIRECT_MIN: ClassVar[int] = 300
    HTTP_REDIRECT_MAX: ClassVar[int] = 400
    HTTP_CLIENT_ERROR_MIN: ClassVar[int] = 400
    HTTP_CLIENT_ERROR_MAX: ClassVar[int] = 500
    HTTP_SERVER_ERROR_MIN: ClassVar[int] = 500
    HTTP_ERROR_MIN: ClassVar[int] = 400

    # Rate limiting constants
    RATE_LIMIT_REQUESTS: ClassVar[int] = 1000
    RATE_LIMIT_WINDOW: ClassVar[int] = 3600

    # Response templates
    SUCCESS_RESPONSE_TEMPLATE: ClassVar[dict[str, str | None]] = {
        "status": "success",
        "data": None,
        "error": None,
        "message": None,
    }

    ERROR_RESPONSE_TEMPLATE: ClassVar[dict[str, str | None]] = {
        "status": "error",
        "data": None,
        "error": None,
        "message": None,
    }

    # Content Types - compact definitions
    class ContentType:
        """Content type constants."""

        JSON: ClassVar[str] = "application/json"
        XML: ClassVar[str] = "application/xml"
        TEXT: ClassVar[str] = "text/plain"
        HTML: ClassVar[str] = "text/html"
        FORM: ClassVar[str] = "application/x-www-form-urlencoded"
        MULTIPART: ClassVar[str] = "multipart/form-data"
        OCTET_STREAM: ClassVar[str] = "application/octet-stream"

    # HTTP Headers - compact definitions
    HEADER_CONTENT_TYPE: ClassVar[str] = "Content-Type"
    HEADER_AUTHORIZATION: ClassVar[str] = "Authorization"
    HEADER_USER_AGENT: ClassVar[str] = "User-Agent"
    HEADER_ACCEPT: ClassVar[str] = "Accept"

    # Combined constants using patterns
    DEFAULT_USER_AGENT: ClassVar[str] = f"FlextAPI/{API_VERSION}"
    DEFAULT_REQUEST_TIMEOUT: ClassVar[float] = 30.0
    DEFAULT_RETRIES: ClassVar[int] = 3

    # HTTP Status - compact ranges and codes
    HTTP_SUCCESS_RANGE: ClassVar[tuple[int, int]] = (200, 300)
    HTTP_SUCCESS_STATUSES: ClassVar[tuple[int, ...]] = (200, 201, 202, 204, 206, 304)

    # Pagination - direct core composition
    DEFAULT_PAGE_SIZE: ClassVar[int] = CoreProcessing.DEFAULT_BATCH_SIZE // 5
    MIN_PAGE_SIZE: ClassVar[int] = CorePagination.MIN_PAGE_SIZE
    MAX_PAGE_SIZE: ClassVar[int] = CorePagination.MAX_PAGE_SIZE

    # Validation limits - compact definitions
    VALIDATION_LIMITS: ClassVar[dict[str, int | float]] = {
        "MAX_URL_LENGTH": 2048,
        "MIN_TIMEOUT": 0.0,
        "MAX_TIMEOUT": 300.0,
        "MIN_RETRIES": 0,
        "MAX_RETRIES": 10,
    }

    # Rate limiting - compact configuration
    RATE_LIMIT_CONFIG: ClassVar[dict[str, int | float]] = {
        "REQUESTS": 1000,
        "WINDOW": 3600,
        "BACKOFF_FACTOR": 0.3,
    }

    # CORS - compact configuration
    CORS_CONFIG: ClassVar[dict[str, list[str]]] = {
        "ORIGINS": ["*"],
        "METHODS": [Method.GET, Method.POST, Method.PUT, Method.DELETE],
        "HEADERS": [HEADER_CONTENT_TYPE, HEADER_AUTHORIZATION],
    }

    # URLs - compact definitions
    URL_CONFIG: ClassVar[dict[str, str]] = {
        "EXAMPLE_BASE_URL": "https://api.example.com",
        "LOCALHOST_BASE_URL": "https://localhost:8000",
    }

    # Server constants
    class Server:
        """Server configuration constants."""

        DEFAULT_HOST: ClassVar[str] = "127.0.0.1"
        DEFAULT_PORT: ClassVar[int] = 8000

    # Response templates - compact definition

    # Status constants - compact enum-style
    class Status:
        """Unified status constants."""

        IDLE: ClassVar[str] = "idle"
        PENDING: ClassVar[str] = "pending"
        RUNNING: ClassVar[str] = "running"
        COMPLETED: ClassVar[str] = "completed"
        FAILED: ClassVar[str] = "failed"
        ERROR: ClassVar[str] = "error"

    # Error codes - API-specific (composition instead of inheritance to avoid final overrides)
    class Errors:
        """API-specific error codes.

        Note: Does not extend CoreErrors to avoid conflicts with final parent attributes.
        Includes both API-specific codes and common error references from FlextConstants.
        """

        # API-specific error codes
        MIDDLEWARE_ERROR: ClassVar[str] = "MIDDLEWARE_ERROR"
        PROTOCOL_ERROR: ClassVar[str] = "PROTOCOL_ERROR"
        HTTP_ERROR: ClassVar[str] = "HTTP_ERROR"

        # API HTTP-specific error codes (referenced from core)
        CONNECTION_ERROR: ClassVar[str] = "CONNECTION_ERROR"
        TIMEOUT_ERROR: ClassVar[str] = "TIMEOUT_ERROR"
        VALIDATION_ERROR: ClassVar[str] = "VALIDATION_ERROR"
        CONFIG_ERROR: ClassVar[str] = "CONFIG_ERROR"

    # Serialization formats - moved from typings.py
    class SerializationFormat(StrEnum):
        """Supported serialization formats."""

        JSON = "json"
        MSGPACK = "msgpack"
        CBOR = "cbor"
        CUSTOM = "custom"

    # WebSocket constants
    class WebSocket:
        """WebSocket protocol constants."""

        DEFAULT_PING_INTERVAL: ClassVar[float] = 20.0
        DEFAULT_PING_TIMEOUT: ClassVar[float] = 20.0
        DEFAULT_CLOSE_TIMEOUT: ClassVar[float] = 10.0
        DEFAULT_MAX_SIZE: ClassVar[int] = 10 * 1024 * 1024  # 10MB
        DEFAULT_MAX_QUEUE: ClassVar[int] = 32
        DEFAULT_RECONNECT_MAX_ATTEMPTS: ClassVar[int] = 5
        DEFAULT_RECONNECT_BACKOFF_FACTOR: ClassVar[float] = 1.5
        COMPRESSION_DEFLATE: ClassVar[str] = "deflate"
        MESSAGE_TYPE_TEXT: ClassVar[str] = "text"
        MESSAGE_TYPE_BINARY: ClassVar[str] = "binary"
        PROTOCOL_WS: ClassVar[str] = "ws"
        PROTOCOL_WSS: ClassVar[str] = "wss"
        PROTOCOL_WEBSOCKET: ClassVar[str] = "websocket"
        STATUS_SWITCHING_PROTOCOLS: ClassVar[int] = 101

    # SSE constants
    class SSE:
        """Server-Sent Events protocol constants."""

        DEFAULT_RETRY_TIMEOUT: ClassVar[int] = 3000
        DEFAULT_CONNECT_TIMEOUT: ClassVar[float] = 30.0
        DEFAULT_READ_TIMEOUT: ClassVar[float] = 300.0
        DEFAULT_RECONNECT_MAX_ATTEMPTS: ClassVar[int] = 10
        DEFAULT_RECONNECT_BACKOFF_FACTOR: ClassVar[float] = 1.5
        PROTOCOL_SSE: ClassVar[str] = "sse"
        PROTOCOL_SERVER_SENT_EVENTS: ClassVar[str] = "server-sent-events"
        PROTOCOL_EVENTSOURCE: ClassVar[str] = "eventsource"

    # GraphQL constants
    class GraphQL:
        """GraphQL protocol constants."""

        PROTOCOL_GRAPHQL: ClassVar[str] = "graphql"
        PROTOCOL_GQL: ClassVar[str] = "gql"

    # HTTP Protocol constants
    class HTTP:
        """HTTP protocol-specific constants."""

        PROTOCOL_HTTP: ClassVar[str] = "http"
        PROTOCOL_HTTPS: ClassVar[str] = "https"
        PROTOCOL_HTTP_1_1: ClassVar[str] = "http/1.1"
        PROTOCOL_HTTP_2: ClassVar[str] = "http/2"
        PROTOCOL_HTTP_3: ClassVar[str] = "http/3"
        SUPPORTED_PROTOCOLS: ClassVar[list[str]] = [
            PROTOCOL_HTTP,
            PROTOCOL_HTTPS,
            PROTOCOL_HTTP_1_1,
            PROTOCOL_HTTP_2,
        ]
        SUPPORTED_PROTOCOLS_WITH_HTTP3: ClassVar[list[str]] = [
            PROTOCOL_HTTP,
            PROTOCOL_HTTPS,
            PROTOCOL_HTTP_1_1,
            PROTOCOL_HTTP_2,
            PROTOCOL_HTTP_3,
        ]

    # HTTP Retry constants
    class HTTPRetry:
        """HTTP retry status codes."""

        RETRYABLE_STATUS_CODES: ClassVar[set[int]] = {408, 429, 500, 502, 503, 504}

    # HTTP Client constants
    class HTTPClient:
        """HTTP client connection constants."""

        DEFAULT_MAX_CONNECTIONS: ClassVar[int] = 100
        DEFAULT_MAX_KEEPALIVE_CONNECTIONS: ClassVar[int] = 20


__all__ = ["FlextApiConstants", "Unit"]
