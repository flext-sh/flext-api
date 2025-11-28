"""Constants and enumerations for flext-api domain.

All constant values, literals, and enums are centralized here following FLEXT standards.
Only constants and enums - no functions or classes with behavior.
"""

from __future__ import annotations

from collections.abc import Mapping, Set as AbstractSet
from enum import StrEnum
from typing import ClassVar, Final, Literal

from flext_core import FlextConstants

# Unit type for operations that return no data (replaces None in FlextResult)
# Python 3.13+ PEP 695 best practice: Use type keyword for type aliases
type UnitLiteral = Literal[True]
"""Unit type literal - represents operations that return no data (replaces None in FlextResult)."""


class FlextApiConstants:
    """Flext constants for API domain functionality using composition."""

    # Core composition - inherit all core constants
    CoreErrors = FlextConstants.Errors
    CoreNetwork = FlextConstants.Network
    CoreReliability = FlextConstants.Reliability
    CorePlatform = FlextConstants.Platform
    CoreProcessing = FlextConstants.Processing
    CorePagination = FlextConstants.Pagination

    # Validation mappings for runtime validation
    class ValidationMappings:
        """Validation mappings for runtime checks using advanced collections.abc."""

        # HTTP Methods validation mapping
        HTTP_METHOD_VALIDATION_MAP: ClassVar[Mapping[str, str]] = {
            "GET": "GET",
            "POST": "POST",
            "PUT": "PUT",
            "DELETE": "DELETE",
            "PATCH": "PATCH",
            "HEAD": "HEAD",
            "OPTIONS": "OPTIONS",
            "CONNECT": "CONNECT",
            "TRACE": "TRACE",
        }
        HTTP_METHOD_VALIDATION_SET: ClassVar[AbstractSet[str]] = frozenset(
            HTTP_METHOD_VALIDATION_MAP.keys()
        )

        # Content Types validation mapping
        CONTENT_TYPE_VALIDATION_MAP: ClassVar[Mapping[str, str]] = {
            "application/json": "application/json",
            "application/xml": "application/xml",
            "text/plain": "text/plain",
            "text/html": "text/html",
            "application/x-www-form-urlencoded": "application/x-www-form-urlencoded",
            "multipart/form-data": "multipart/form-data",
            "application/octet-stream": "application/octet-stream",
        }
        CONTENT_TYPE_VALIDATION_SET: ClassVar[AbstractSet[str]] = frozenset(
            CONTENT_TYPE_VALIDATION_MAP.keys()
        )

        # Status validation mapping
        STATUS_VALIDATION_MAP: ClassVar[Mapping[str, str]] = {
            "idle": "idle",
            "pending": "pending",
            "running": "running",
            "completed": "completed",
            "failed": "failed",
            "error": "error",
        }
        STATUS_VALIDATION_SET: ClassVar[AbstractSet[str]] = frozenset(
            STATUS_VALIDATION_MAP.keys()
        )

    # Client configuration with core composition
    DEFAULT_TIMEOUT: ClassVar[int] = FlextConstants.Network.DEFAULT_TIMEOUT
    DEFAULT_MAX_RETRIES: ClassVar[int] = FlextConstants.Reliability.MAX_RETRY_ATTEMPTS
    DEFAULT_BASE_URL: ClassVar[str] = (
        f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
    )
    API_VERSION: ClassVar[str] = "v1"

    # HTTP Methods - StrEnum for type safety and Pydantic compatibility
    class Method(StrEnum):
        """HTTP method enumeration."""

        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"
        PATCH = "PATCH"
        HEAD = "HEAD"
        OPTIONS = "OPTIONS"
        CONNECT = "CONNECT"
        TRACE = "TRACE"

    # Valid HTTP methods set for validation (derived from enum)
    VALID_METHODS: Final[AbstractSet[str]] = (
        ValidationMappings.HTTP_METHOD_VALIDATION_SET
    )

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

    # Response templates - using Mapping for immutability
    SUCCESS_RESPONSE_TEMPLATE: ClassVar[Mapping[str, str | None]] = {
        "status": "success",
        "data": None,
        "error": None,
        "message": None,
    }

    ERROR_RESPONSE_TEMPLATE: ClassVar[Mapping[str, str | None]] = {
        "status": "error",
        "data": None,
        "error": None,
        "message": None,
    }

    # Content Types - StrEnum for type safety and Pydantic compatibility
    class ContentType(StrEnum):
        """Content type enumeration."""

        JSON = "application/json"
        XML = "application/xml"
        TEXT = "text/plain"
        HTML = "text/html"
        FORM = "application/x-www-form-urlencoded"
        MULTIPART = "multipart/form-data"
        OCTET_STREAM = "application/octet-stream"

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
    DEFAULT_PAGE_SIZE: ClassVar[int] = FlextConstants.Processing.DEFAULT_BATCH_SIZE // 5
    MIN_PAGE_SIZE: ClassVar[int] = FlextConstants.Pagination.MIN_PAGE_SIZE
    MAX_PAGE_SIZE: ClassVar[int] = FlextConstants.Pagination.MAX_PAGE_SIZE

    # Validation limits - using Mapping for immutability
    VALIDATION_LIMITS: ClassVar[Mapping[str, int | float]] = {
        "MAX_URL_LENGTH": 2048,
        "MIN_TIMEOUT": 0.0,
        "MAX_TIMEOUT": 300.0,
        "MIN_RETRIES": 0,
        "MAX_RETRIES": 10,
    }

    # Rate limiting - using Mapping for immutability
    RATE_LIMIT_CONFIG: ClassVar[Mapping[str, int | float]] = {
        "REQUESTS": 1000,
        "WINDOW": 3600,
        "BACKOFF_FACTOR": 0.3,
    }

    # CORS - using Mapping for immutability
    CORS_CONFIG: ClassVar[Mapping[str, list[str]]] = {
        "ORIGINS": ["*"],
        "METHODS": [Method.GET, Method.POST, Method.PUT, Method.DELETE],
        "HEADERS": [HEADER_CONTENT_TYPE, HEADER_AUTHORIZATION],
    }

    # URLs - using Mapping for immutability
    URL_CONFIG: ClassVar[Mapping[str, str]] = {
        "EXAMPLE_BASE_URL": "https://api.example.com",
        "LOCALHOST_BASE_URL": "https://localhost:8000",
    }

    # Server constants
    class Server:
        """Server configuration constants."""

        DEFAULT_HOST: ClassVar[str] = "127.0.0.1"
        DEFAULT_PORT: ClassVar[int] = 8000

    # Response templates - compact definition

    # Status constants - StrEnum for type safety and Pydantic compatibility
    class Status(StrEnum):
        """Unified status enumeration."""

        IDLE = "idle"
        PENDING = "pending"
        RUNNING = "running"
        COMPLETED = "completed"
        FAILED = "failed"
        ERROR = "error"

    # Valid statuses set for validation
    VALID_STATUSES: Final[AbstractSet[str]] = ValidationMappings.STATUS_VALIDATION_SET

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

        DEFAULT_PING_INTERVAL: Final[float] = 20.0
        DEFAULT_PING_TIMEOUT: Final[float] = 20.0
        DEFAULT_CLOSE_TIMEOUT: Final[float] = 10.0
        DEFAULT_MAX_SIZE: Final[int] = 10 * 1024 * 1024  # 10MB
        DEFAULT_MAX_QUEUE: Final[int] = 32
        DEFAULT_RECONNECT_MAX_ATTEMPTS: Final[int] = 5
        DEFAULT_RECONNECT_BACKOFF_FACTOR: Final[float] = 1.5
        COMPRESSION_DEFLATE: Final[str] = "deflate"
        STATUS_SWITCHING_PROTOCOLS: Final[int] = 101

        class MessageType(StrEnum):
            """WebSocket message type enumeration."""

            TEXT = "text"
            BINARY = "binary"

        class Protocol(StrEnum):
            """WebSocket protocol enumeration."""

            WS = "ws"
            WSS = "wss"
            WEBSOCKET = "websocket"

    # SSE constants
    class SSE:
        """Server-Sent Events protocol constants."""

        DEFAULT_RETRY_TIMEOUT: Final[int] = 3000
        DEFAULT_CONNECT_TIMEOUT: Final[float] = 30.0
        DEFAULT_READ_TIMEOUT: Final[float] = 300.0
        DEFAULT_RECONNECT_MAX_ATTEMPTS: Final[int] = 10
        DEFAULT_RECONNECT_BACKOFF_FACTOR: Final[float] = 1.5

        class Protocol(StrEnum):
            """SSE protocol enumeration."""

            SSE = "sse"
            SERVER_SENT_EVENTS = "server-sent-events"
            EVENTSOURCE = "eventsource"

    # GraphQL constants
    class GraphQL:
        """GraphQL protocol constants."""

        class Protocol(StrEnum):
            """GraphQL protocol enumeration."""

            GRAPHQL = "graphql"
            GQL = "gql"

    # HTTP Protocol constants
    class HTTP:
        """HTTP protocol-specific constants."""

        class Protocol(StrEnum):
            """HTTP protocol enumeration."""

            HTTP = "http"
            HTTPS = "https"
            HTTP_1_1 = "http/1.1"
            HTTP_2 = "http/2"
            HTTP_3 = "http/3"

        # Supported protocols - using frozenset for immutability
        SUPPORTED_PROTOCOLS: Final[AbstractSet[str]] = frozenset({
            Protocol.HTTP,
            Protocol.HTTPS,
            Protocol.HTTP_1_1,
            Protocol.HTTP_2,
        })
        SUPPORTED_PROTOCOLS_WITH_HTTP3: Final[AbstractSet[str]] = frozenset({
            Protocol.HTTP,
            Protocol.HTTPS,
            Protocol.HTTP_1_1,
            Protocol.HTTP_2,
            Protocol.HTTP_3,
        })

    # HTTP Retry constants
    class HTTPRetry:
        """HTTP retry status codes."""

        RETRYABLE_STATUS_CODES: ClassVar[AbstractSet[int]] = frozenset({
            408,
            429,
            500,
            502,
            503,
            504,
        })

    # HTTP Client constants
    class HTTPClient:
        """HTTP client connection constants."""

        DEFAULT_MAX_CONNECTIONS: ClassVar[int] = 100
        DEFAULT_MAX_KEEPALIVE_CONNECTIONS: ClassVar[int] = 20

    # Pagination defaults - moved from utilities
    class PaginationDefaults:
        """Pagination default values."""

        DEFAULT_PAGE: ClassVar[int] = 1
        DEFAULT_PAGE_SIZE_STRING: ClassVar[str] = "20"
        DEFAULT_MAX_PAGE_SIZE_FALLBACK: ClassVar[int] = 1000

    # Validation methods using ValidationMappings
    @classmethod
    def validate_http_method(cls, method: str) -> str | None:
        """Validate HTTP method against allowed values."""
        return cls.ValidationMappings.HTTP_METHOD_VALIDATION_MAP.get(method)

    @classmethod
    def validate_content_type(cls, content_type: str) -> str | None:
        """Validate content type against allowed values."""
        return cls.ValidationMappings.CONTENT_TYPE_VALIDATION_MAP.get(content_type)

    @classmethod
    def validate_status(cls, status: str) -> str | None:
        """Validate status against allowed values."""
        return cls.ValidationMappings.STATUS_VALIDATION_MAP.get(status)

    @classmethod
    def get_valid_http_methods(cls) -> AbstractSet[str]:
        """Get all valid HTTP methods."""
        return cls.ValidationMappings.HTTP_METHOD_VALIDATION_SET

    @classmethod
    def get_valid_content_types(cls) -> AbstractSet[str]:
        """Get all valid content types."""
        return cls.ValidationMappings.CONTENT_TYPE_VALIDATION_SET

    @classmethod
    def get_valid_statuses(cls) -> AbstractSet[str]:
        """Get all valid statuses."""
        return cls.ValidationMappings.STATUS_VALIDATION_SET

    # =========================================================================
    # LITERAL TYPES - Type-safe annotations (Python 3.13+ PEP 695 best practices)
    # =========================================================================

    # HTTP method literal (derived from Method StrEnum)
    type HttpMethodLiteral = Literal[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "HEAD",
        "OPTIONS",
        "CONNECT",
        "TRACE",
    ]

    # Content type literal (derived from ContentType StrEnum)
    type ContentTypeLiteral = Literal[
        "application/json",
        "application/xml",
        "text/plain",
        "text/html",
        "application/x-www-form-urlencoded",
        "multipart/form-data",
        "application/octet-stream",
    ]

    # Status literal (derived from Status StrEnum)
    type StatusLiteral = Literal[
        "idle", "pending", "running", "completed", "failed", "error"
    ]

    # Serialization format literal (derived from SerializationFormat StrEnum)
    type SerializationFormatLiteral = Literal["json", "msgpack", "cbor", "custom"]

    # WebSocket message type literal (derived from WebSocket.MessageType StrEnum)
    type WebSocketMessageTypeLiteral = Literal["text", "binary"]

    # WebSocket protocol literal (derived from WebSocket.Protocol StrEnum)
    type WebSocketProtocolLiteral = Literal["ws", "wss", "websocket"]

    # HTTP protocol literal (derived from HTTP.Protocol StrEnum)
    type HttpProtocolLiteral = Literal["http", "https", "http/1.1", "http/2", "http/3"]

    # SSE protocol literal (derived from SSE.Protocol StrEnum)
    type SseProtocolLiteral = Literal["sse", "server-sent-events", "eventsource"]

    # GraphQL protocol literal (derived from GraphQL.Protocol StrEnum)
    type GraphQLProtocolLiteral = Literal["graphql", "gql"]


__all__ = ["FlextApiConstants", "UnitLiteral"]
