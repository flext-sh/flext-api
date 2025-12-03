"""FlextApi constants - Advanced type-safe constants using StrEnum + Pydantic 2 patterns.

FLEXT-API domain constants with FlextCore integration. Uses advanced Python 3.13+ features:
- StrEnum for type-safe enumerations with Pydantic 2 validation
- PEP 695 type aliases for strict Literal types
- Nested classes for logical grouping
- Collections.abc for immutable collections
- TypeIs and TypeGuard for advanced type narrowing

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Set as AbstractSet
from enum import StrEnum
from types import MappingProxyType
from typing import Final, Literal, TypeGuard, TypeIs

from flext_core import r, u

# ═══════════════════════════════════════════════════════════════════════════
# STRENUM + PYDANTIC 2: PADRÃO DEFINITIVO PARA FLEXT-API
# ═══════════════════════════════════════════════════════════════════════════

# PRINCÍPIO FUNDAMENTAL: StrEnum + Pydantic 2 = Validação Automática!
# - NÃO precisa criar Literal separado para validação
# - NÃO precisa criar frozenset para validação
# - NÃO precisa criar AfterValidator
# - Pydantic valida automaticamente contra o StrEnum

# SUBSETS: Use Literal[Status.MEMBER] para aceitar apenas ALGUNS valores.
# Isso referencia o enum member, não duplica strings!


class FlextApiConstants(FlextConstants):
    """FlextApi domain constants extending FlextConstants.

    Architecture: Layer 1 (Domain Constants - Extends Core)
    =========================================================
    Provides domain-specific constants for HTTP operations using advanced patterns:
    - StrEnum for type-safe enumerations with automatic Pydantic validation
    - PEP 695 type aliases for strict Literal unions
    - Nested classes for logical grouping (Methods, Status, ContentType)
    - TypeIs/TypeGuard methods for advanced type narrowing
    - Collections.abc for immutable validation sets

    Integration with p:
    This class provides the constant registry that FlextApiProtocols depend on.
    Structural typing ensures protocol compliance without explicit inheritance.

    Usage Patterns:
        # Direct access (recommended)
        >>> from flext_api.constants import FlextApiConstants as ApiConst
        >>> method = ApiConst.Method.GET
        >>> status = ApiConst.Status.SUCCESS

        # Type-safe validation
        >>> ApiConst.Method.is_valid_method("GET")  # True
        >>> ApiConst.Status.is_success_status("success")  # True

        # Literal types for Pydantic models
        >>> status: ApiConst.StatusLiteral  # Type-safe: "idle" | "pending" | ...
    """

    # ═══════════════════════════════════════════════════════════════════
    # STRENUM: Única declaração necessária para validação automática
    # ═══════════════════════════════════════════════════════════════════

    class Method(StrEnum):
        """HTTP method enumeration - automatic Pydantic validation.

        PYDANTIC MODELS:
            model_config = ConfigDict(use_enum_values=True)
            method: FlextApiConstants.Method

        Resultado:
            - Aceita "GET", "POST", etc. ou Method.GET
            - Serializa como string
            - Valida automaticamente (rejeita valores inválidos)
        """

        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"
        PATCH = "PATCH"
        HEAD = "HEAD"
        OPTIONS = "OPTIONS"
        CONNECT = "CONNECT"
        TRACE = "TRACE"

    class Status(StrEnum):
        """HTTP status enumeration for operations."""

        IDLE = "idle"
        PENDING = "pending"
        RUNNING = "running"
        COMPLETED = "completed"
        FAILED = "failed"
        ERROR = "error"
        SUCCESS = "success"

    class ContentType(StrEnum):
        """Content type enumeration."""

        JSON = "application/json"
        XML = "application/xml"
        TEXT = "text/plain"
        HTML = "text/html"
        FORM = "application/x-www-form-urlencoded"
        MULTIPART = "multipart/form-data"
        OCTET_STREAM = "application/octet-stream"

    class SerializationFormat(StrEnum):
        """Supported serialization formats."""

        JSON = "json"
        MSGPACK = "msgpack"
        CBOR = "cbor"
        CUSTOM = "custom"

    # ═══════════════════════════════════════════════════════════════════
    # SUBSETS: Literal referenciando membros do StrEnum
    # ═══════════════════════════════════════════════════════════════════
    # Use para aceitar apenas ALGUNS valores do enum em métodos
    # Isso NÃO duplica strings - referencia o enum member!

    type ActiveMethods = Literal[Method.GET, Method.POST, Method.PUT, Method.DELETE]
    """Active HTTP methods for operations."""
    type SafeMethods = Literal[Method.GET, Method.HEAD, Method.OPTIONS, Method.TRACE]
    """Safe HTTP methods (no side effects)."""
    type TerminalStatuses = Literal[Status.COMPLETED, Status.FAILED, Status.ERROR]
    """Terminal operation statuses."""
    type SuccessStatuses = Literal[Status.SUCCESS, Status.COMPLETED]
    """Success operation statuses."""
    type JsonCompatibleTypes = Literal[ContentType.JSON, ContentType.TEXT]
    """Content types compatible with JSON serialization."""

    # ═══════════════════════════════════════════════════════════════════
    # TYPEIS + TYPEGUARD: Advanced type narrowing (Python 3.13+ PEP 742)
    # ═══════════════════════════════════════════════════════════════════

    @classmethod
    def is_valid_method(cls, value: str) -> TypeIs[Method]:
        """TypeIs for HTTP Method validation - narrowing in if/else."""
        return value in cls.Method._value2member_map_

    @classmethod
    def is_active_method(cls, value: str) -> TypeGuard[ActiveMethods]:
        """TypeGuard for active method subset."""
        return value in {
            cls.Method.GET.value,
            cls.Method.POST.value,
            cls.Method.PUT.value,
            cls.Method.DELETE.value,
        }

    @classmethod
    def is_safe_method(cls, value: str) -> TypeGuard[SafeMethods]:
        """TypeGuard for safe method subset."""
        return value in {
            cls.Method.GET.value,
            cls.Method.HEAD.value,
            cls.Method.OPTIONS.value,
            cls.Method.TRACE.value,
        }

    @classmethod
    def is_terminal_status(cls, value: str) -> TypeIs[Status]:
        """TypeIs for terminal status validation."""
        if isinstance(value, cls.Status):
            return value in {cls.Status.COMPLETED, cls.Status.FAILED, cls.Status.ERROR}
        return value in {"completed", "failed", "error"}

    @classmethod
    def is_success_status(cls, value: str) -> TypeGuard[SuccessStatuses]:
        """TypeGuard for success status subset."""
        return value in {cls.Status.SUCCESS.value, cls.Status.COMPLETED.value}

    @classmethod
    def is_json_compatible(cls, value: str) -> TypeGuard[JsonCompatibleTypes]:
        """TypeGuard for JSON-compatible content types."""
        return value in {cls.ContentType.JSON.value, cls.ContentType.TEXT.value}

    # ═══════════════════════════════════════════════════════════════════
    # IMMUTABLE COLLECTIONS: frozenset para O(1) validação
    # ═══════════════════════════════════════════════════════════════════

    VALID_METHODS: Final[AbstractSet[str]] = frozenset(
        member.value for member in Method.__members__.values()
    )
    """Immutable set of all valid HTTP methods for O(1) validation."""

    VALID_STATUSES: Final[AbstractSet[str]] = frozenset(
        member.value for member in Status.__members__.values()
    )
    """Immutable set of all valid operation statuses."""

    VALID_CONTENT_TYPES: Final[AbstractSet[str]] = frozenset(
        member.value for member in ContentType.__members__.values()
    )
    """Immutable set of all valid content types."""

    ACTIVE_METHODS_SET: Final[AbstractSet[str]] = frozenset(
        member.value for member in [Method.GET, Method.POST, Method.PUT, Method.DELETE]
    )
    """Active HTTP methods for validation."""

    SAFE_METHODS_SET: Final[AbstractSet[str]] = frozenset(
        member.value
        for member in [Method.GET, Method.HEAD, Method.OPTIONS, Method.TRACE]
    )
    """Safe HTTP methods for validation."""

    # ═══════════════════════════════════════════════════════════════════
    # CONFIGURATION CONSTANTS: Valores padrão e limites
    # ═══════════════════════════════════════════════════════════════════

    DEFAULT_TIMEOUT: Final[float] = 30.0
    """Default request timeout in seconds."""

    DEFAULT_MAX_RETRIES: Final[int] = 3
    """Default maximum retry attempts."""

    DEFAULT_BASE_URL: Final[str] = (
        f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
    )
    """Default base URL for API operations."""

    API_VERSION: Final[str] = "v1"
    """API version string."""

    MAX_URL_LENGTH: Final[int] = 2048
    """Maximum URL length."""

    MIN_URL_LENGTH: Final[int] = 8
    """Minimum URL length."""

    MIN_PORT: Final[int] = 1
    """Minimum port number."""

    MAX_PORT: Final[int] = 65535
    """Maximum port number."""

    BACKOFF_FACTOR: Final[float] = 0.5
    """Exponential backoff factor."""

    HTTP_SUCCESS_MIN: Final[int] = 200
    """Minimum HTTP success status code."""

    HTTP_SUCCESS_MAX: Final[int] = 300
    """Maximum HTTP success status code."""

    HTTP_REDIRECT_MIN: Final[int] = 300
    """Minimum HTTP redirect status code."""

    HTTP_REDIRECT_MAX: Final[int] = 400
    """Maximum HTTP redirect status code."""

    HTTP_CLIENT_ERROR_MIN: Final[int] = 400
    """Minimum HTTP client error status code."""

    HTTP_CLIENT_ERROR_MAX: Final[int] = 500
    """Maximum HTTP client error status code."""

    HTTP_SERVER_ERROR_MIN: Final[int] = 500
    """Minimum HTTP server error status code."""

    HTTP_ERROR_MIN: Final[int] = 400
    """Minimum HTTP error status code."""

    # ═══════════════════════════════════════════════════════════════════
    # RESPONSE TEMPLATES: Mappings imutáveis
    # ═══════════════════════════════════════════════════════════════════

    SUCCESS_RESPONSE_TEMPLATE: Final[Mapping[str, str | None]] = MappingProxyType({
        "status": "success",
        "data": None,
        "error": None,
        "message": None,
    })
    """Template for successful API responses."""

    ERROR_RESPONSE_TEMPLATE: Final[Mapping[str, str | None]] = MappingProxyType({
        "status": "error",
        "data": None,
        "error": None,
        "message": None,
    })
    """Template for error API responses."""

    # ═══════════════════════════════════════════════════════════════════
    # HEADER CONSTANTS: HTTP headers padronizados
    # ═══════════════════════════════════════════════════════════════════

    HEADER_CONTENT_TYPE: Final[str] = "Content-Type"
    """Content-Type header name."""

    HEADER_AUTHORIZATION: Final[str] = "Authorization"
    """Authorization header name."""

    HEADER_USER_AGENT: Final[str] = "User-Agent"
    """User-Agent header name."""

    HEADER_ACCEPT: Final[str] = "Accept"
    """Accept header name."""

    # ═══════════════════════════════════════════════════════════════════
    # DERIVED CONSTANTS: Constantes derivadas de outras
    # ═══════════════════════════════════════════════════════════════════

    DEFAULT_USER_AGENT: Final[str] = f"FlextAPI/{API_VERSION}"
    """Default User-Agent string."""

    DEFAULT_RETRIES: Final[int] = 3
    """Default retry count."""

    # ═══════════════════════════════════════════════════════════════════
    # RATE LIMITING: Configuração de limites
    # ═══════════════════════════════════════════════════════════════════

    RATE_LIMIT_REQUESTS: Final[int] = 1000
    """Rate limit requests per window."""

    RATE_LIMIT_WINDOW: Final[int] = 3600
    """Rate limit window in seconds."""

    # ═══════════════════════════════════════════════════════════════════
    # PAGINATION: Configurações padrão
    # ═══════════════════════════════════════════════════════════════════

    DEFAULT_PAGE_SIZE: Final[int] = FlextConstants.Processing.DEFAULT_BATCH_SIZE // 5
    """Default page size for API responses."""

    MIN_PAGE_SIZE: Final[int] = FlextConstants.Pagination.MIN_PAGE_SIZE
    """Minimum page size."""

    MAX_PAGE_SIZE: Final[int] = FlextConstants.Pagination.MAX_PAGE_SIZE
    """Maximum page size."""

    # ═══════════════════════════════════════════════════════════════════
    # VALIDATION LIMITS: Mappings imutáveis para validação
    # ═══════════════════════════════════════════════════════════════════

    VALIDATION_LIMITS: Final[Mapping[str, int | float]] = MappingProxyType({
        "MAX_URL_LENGTH": MAX_URL_LENGTH,
        "MIN_TIMEOUT": 0.1,
        "MAX_TIMEOUT": 300.0,
        "MIN_RETRIES": 0,
        "MAX_RETRIES": 10,
    })
    """Validation limits mapping."""

    # ═══════════════════════════════════════════════════════════════════
    # CORS CONFIGURATION: Configuração CORS
    # ═══════════════════════════════════════════════════════════════════

    CORS_CONFIG: Final[Mapping[str, list[str]]] = MappingProxyType({
        "origins": ["*"],
        "methods": [Method.GET, Method.POST, Method.PUT, Method.DELETE],
        "headers": [HEADER_CONTENT_TYPE, HEADER_AUTHORIZATION],
    })
    """CORS configuration."""

    # ═══════════════════════════════════════════════════════════════════
    # URL CONFIGURATION: URLs padrão
    # ═══════════════════════════════════════════════════════════════════

    URL_CONFIG: Final[Mapping[str, str]] = MappingProxyType({
        "EXAMPLE_BASE_URL": "https://api.example.com",
        "LOCALHOST_BASE_URL": "https://localhost:8000",
    })
    """URL configuration mapping."""

    # ═══════════════════════════════════════════════════════════════════
    # UTILITY METHODS: Validação avançada com u
    # ═══════════════════════════════════════════════════════════════════

    @classmethod
    def validate_method_with_result(cls, value: str) -> r[Method]:
        """Validate HTTP method using u.Enum.parse."""
        return u.Enum.parse(cls.Method, value)

    @classmethod
    def validate_status_with_result(cls, value: str) -> r[Status]:
        """Validate status using u.Enum.parse."""
        return u.Enum.parse(cls.Status, value)

    @classmethod
    def validate_content_type_with_result(cls, value: str) -> r[ContentType]:
        """Validate content type using u.Enum.parse."""
        return u.Enum.parse(cls.ContentType, value)

    @classmethod
    def create_method_validator(cls) -> Callable[[str], Method]:
        """Create BeforeValidator for HTTP Method in Pydantic models."""
        return uvalidator(cls.Method)

    @classmethod
    def create_status_validator(cls) -> Callable[[str], Status]:
        """Create BeforeValidator for Status in Pydantic models."""
        return uvalidator(cls.Status)

    # ═══════════════════════════════════════════════════════════════════
    # LITERAL TYPES: PEP 695 strict type aliases (Python 3.13+)
    # ═══════════════════════════════════════════════════════════════════

    type MethodLiteral = Literal[
        "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "CONNECT", "TRACE"
    ]
    """HTTP method literal - matches Method StrEnum values exactly."""

    type StatusLiteral = Literal[
        "idle", "pending", "running", "completed", "failed", "error", "success"
    ]
    """Status literal - matches Status StrEnum values exactly."""

    type ContentTypeLiteral = Literal[
        "application/json",
        "application/xml",
        "text/plain",
        "text/html",
        "application/x-www-form-urlencoded",
        "multipart/form-data",
        "application/octet-stream",
    ]
    """Content type literal - matches ContentType StrEnum values exactly."""

    type SerializationFormatLiteral = Literal["json", "msgpack", "cbor", "custom"]
    """Serialization format literal - matches SerializationFormat StrEnum values exactly."""

    # Protocol Literals for type-safe protocol usage
    type HttpProtocolLiteral = Literal["http", "https", "http/1.1", "http/2", "http/3"]
    """HTTP protocol literal - matches HTTP.Protocol StrEnum values."""
    type WebSocketProtocolLiteral = Literal["ws", "wss"]
    """WebSocket protocol literal - matches WebSocket.Protocol StrEnum values."""
    type SseProtocolLiteral = Literal["sse"]
    """SSE protocol literal - matches SSE.Protocol StrEnum values."""
    type GraphQLProtocolLiteral = Literal["graphql", "graphql-ws"]
    """GraphQL protocol literal - matches GraphQL.Protocol StrEnum values."""

    # ═══════════════════════════════════════════════════════════════════
    # ADDITIONAL DOMAIN CLASSES: HTTP, Server, etc. (restaurados)
    # ═══════════════════════════════════════════════════════════════════

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

    class Server:
        """Server configuration constants."""

        DEFAULT_HOST: Final[str] = "127.0.0.1"
        DEFAULT_PORT: Final[int] = 8000

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

    class GraphQL:
        """GraphQL protocol constants."""

        class Protocol(StrEnum):
            """GraphQL protocol enumeration."""

            GRAPHQL = "graphql"
            GQL = "gql"

    class HTTPRetry:
        """HTTP retry status codes."""

        RETRYABLE_STATUS_CODES: Final[AbstractSet[int]] = frozenset({
            408,
            429,
            500,
            502,
            503,
            504,
        })

    class HTTPClient:
        """HTTP client connection constants."""

        DEFAULT_MAX_CONNECTIONS: Final[int] = 100
        DEFAULT_MAX_KEEPALIVE_CONNECTIONS: Final[int] = 20

    class PaginationDefaults:
        """Pagination default values."""

        DEFAULT_PAGE: Final[int] = 1
        DEFAULT_PAGE_SIZE_STRING: Final[str] = "20"
        DEFAULT_MAX_PAGE_SIZE_FALLBACK: Final[int] = 1000


__all__ = ["FlextApiConstants"]
