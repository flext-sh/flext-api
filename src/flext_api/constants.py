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

from flext_core import FlextConstants, r

from flext_api.utilities import u

# ═══════════════════════════════════════════════════════════════════════════
# STRENUM + PYDANTIC 2: DEFINITIVE PATTERN FOR FLEXT-API
# ═══════════════════════════════════════════════════════════════════════════

# FUNDAMENTAL PRINCIPLE: StrEnum + Pydantic 2 = Automatic Validation!
# - No need to create separate Literal for validation
# - No need to create frozenset for validation
# - No need to create AfterValidator
# - Pydantic automatically validates against StrEnum

# SUBSETS: Use Literal[Status.MEMBER] to accept only SOME values.
# This references the enum member, does not duplicate strings!


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

    Architecture:
    - All API constants are organized in the .Api namespace
    - Direct access via FlextApiConstants.Api.*
    - No aliases - use namespaces directly following FLEXT architecture patterns

    Usage Patterns:
        # Direct access (recommended)
        >>> from flext_api.constants import FlextApiConstants as ApiConst
        >>> method = ApiConst.Api.Method.GET
        >>> status = ApiConst.Api.Status.SUCCESS

        # Type-safe validation
        >>> ApiConst.Api.Method.is_valid_method("GET")  # True
        >>> ApiConst.Api.Status.is_success_status("success")  # True

        # Literal types for Pydantic models
        >>> status: ApiConst.Api.StatusLiteral  # Type-safe: "idle" | "pending" | ...
    """

    # =========================================================================
    # NAMESPACE: .Api - All API domain constants
    # =========================================================================

    class Api:
        """API domain constants namespace.

        All API-specific constants are organized here for better namespace
        organization and to enable composition with other domain constants.
        """

        # ═══════════════════════════════════════════════════════════════════
        # STRENUM: Single declaration needed for automatic validation
        # ═══════════════════════════════════════════════════════════════════

        class Method(StrEnum):
            """HTTP method enumeration - automatic Pydantic validation.

            PYDANTIC MODELS:
            model_config = ConfigDict(use_enum_values=True)
            method: FlextApiConstants.Api.Method

            Result:
            - Accepts "GET", "POST", etc. or Method.GET
            - Serializes as string
            - Automatically validates (rejects invalid values)

            DRY Pattern:
                StrEnum is the single source of truth. Use Method.GET.value
                or Method.GET directly - no base strings needed.
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
            """HTTP status enumeration for operations.

            DRY Pattern:
                StrEnum is the single source of truth. Use Status.IDLE.value
                or Status.IDLE directly - no base strings needed.
            """

            IDLE = "idle"
            PENDING = "pending"
            RUNNING = "running"
            COMPLETED = "completed"
            FAILED = "failed"
            ERROR = "error"
            SUCCESS = "success"

        class ContentType(StrEnum):
            """Content type enumeration.

            DRY Pattern:
                StrEnum is the single source of truth. Use ContentType.JSON.value
                or ContentType.JSON directly - no base strings needed.
            """

            JSON = "application/json"
            XML = "application/xml"
            TEXT = "text/plain"
            HTML = "text/html"
            FORM = "application/x-www-form-urlencoded"
            MULTIPART = "multipart/form-data"
            OCTET_STREAM = "application/octet-stream"

        class HttpSerializationFormat(StrEnum):
            """HTTP-specific serialization formats (extends parent SerializationFormat).

            DRY Pattern:
                StrEnum is the single source of truth. Use HttpSerializationFormat.JSON.value
                or HttpSerializationFormat.JSON directly - no base strings needed.
            """

            JSON = "json"
            MSGPACK = "msgpack"
            CBOR = "cbor"
            CUSTOM = "custom"

        # ═══════════════════════════════════════════════════════════════════
        # SUBSETS: Literal referencing StrEnum members (NO string duplication!)
        # ═══════════════════════════════════════════════════════════════════
        # Use to accept only SOME enum values in methods
        # References StrEnum members directly - NO string duplication!

        type ActiveMethods = Literal[
            Method.GET,
            Method.POST,
            Method.PUT,
            Method.DELETE,
        ]
        """Active HTTP methods for operations."""
        type SafeMethods = Literal[
            Method.GET,
            Method.HEAD,
            Method.OPTIONS,
            Method.TRACE,
        ]
        """Safe HTTP methods (no side effects)."""
        type TerminalStatuses = Literal[
            Status.COMPLETED,
            Status.FAILED,
            Status.ERROR,
        ]
        """Terminal operation statuses."""
        type SuccessStatuses = Literal[
            Status.SUCCESS,
            Status.COMPLETED,
        ]
        """Success operation statuses."""
        type JsonCompatibleTypes = Literal[
            ContentType.JSON,
            ContentType.TEXT,
        ]
        """Content types compatible with JSON serialization."""

        # ═══════════════════════════════════════════════════════════════════
        # TYPEIS + TYPEGUARD: Advanced type narrowing (Python 3.13+ PEP 742)
        # ═══════════════════════════════════════════════════════════════════

        @classmethod
        def is_valid_method(cls, value: str) -> TypeIs[Method]:
            """TypeIs for HTTP Method validation - narrowing in if/else."""
            return u.Enum.is_member(cls.Method, value)

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
                return value in {
                    cls.Status.COMPLETED,
                    cls.Status.FAILED,
                    cls.Status.ERROR,
                }
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
        # IMMUTABLE COLLECTIONS: frozenset for O(1) validation
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

        ACTIVE_METHODS_SET: Final[AbstractSet[str]] = frozenset({
            Method.GET.value,
            Method.POST.value,
            Method.PUT.value,
            Method.DELETE.value,
        })
        """Active HTTP methods for validation - references Method enum members."""

        SAFE_METHODS_SET: Final[AbstractSet[str]] = frozenset({
            Method.GET.value,
            Method.HEAD.value,
            Method.OPTIONS.value,
            Method.TRACE.value,
        })
        """Safe HTTP methods for validation - references Method enum members."""

        # ═══════════════════════════════════════════════════════════════════
        # CONFIGURATION CONSTANTS: Default values and limits
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
        # RESPONSE TEMPLATES: Immutable mappings
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
        # DERIVED CONSTANTS: Constants derived from others
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
        # PAGINATION: Default settings
        # ═══════════════════════════════════════════════════════════════════
        # Note: DEFAULT_PAGE_SIZE, MIN_PAGE_SIZE, MAX_PAGE_SIZE are Final in base class
        # Use FlextConstants.Pagination.* for access instead of overriding

        # ═══════════════════════════════════════════════════════════════════
        # VALIDATION LIMITS: Immutable mappings for validation
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
            "methods": [
                "GET",
                "POST",
                "PUT",
                "DELETE",
            ],
            "headers": [HEADER_CONTENT_TYPE, HEADER_AUTHORIZATION],
        })
        """CORS configuration."""

        # ═══════════════════════════════════════════════════════════════════
        # URL CONFIGURATION: Default URLs
        # ═══════════════════════════════════════════════════════════════════

        URL_CONFIG: Final[Mapping[str, str]] = MappingProxyType({
            "EXAMPLE_BASE_URL": "https://api.example.com",
            "LOCALHOST_BASE_URL": "https://localhost:8000",
        })
        """URL configuration mapping."""

        # ═══════════════════════════════════════════════════════════════════
        # UTILITY METHODS: Advanced validation with u
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
            return u.Enum.coerce_validator(cls.Method)

        @classmethod
        def create_status_validator(cls) -> Callable[[str], Status]:
            """Create BeforeValidator for Status in Pydantic models."""
            return u.Enum.coerce_validator(cls.Status)

        # ═══════════════════════════════════════════════════════════════════
        # LITERAL TYPES: PEP 695 strict type aliases (Python 3.13+)
        # ═══════════════════════════════════════════════════════════════════
        # All Literal types reference StrEnum members - NO string duplication!

        type MethodLiteral = Literal[
            Method.GET,
            Method.POST,
            Method.PUT,
            Method.DELETE,
            Method.PATCH,
            Method.HEAD,
            Method.OPTIONS,
            Method.CONNECT,
            Method.TRACE,
        ]
        """HTTP method literal - references Method StrEnum members."""

        type StatusLiteral = Literal[
            Status.IDLE,
            Status.PENDING,
            Status.RUNNING,
            Status.COMPLETED,
            Status.FAILED,
            Status.ERROR,
            Status.SUCCESS,
        ]
        """Status literal - references Status StrEnum members."""

        type ContentTypeLiteral = Literal[
            ContentType.JSON,
            ContentType.XML,
            ContentType.TEXT,
            ContentType.HTML,
            ContentType.FORM,
            ContentType.MULTIPART,
            ContentType.OCTET_STREAM,
        ]
        """Content type literal - references ContentType StrEnum members."""

        type SerializationFormatLiteral = Literal[
            HttpSerializationFormat.JSON,
            HttpSerializationFormat.MSGPACK,
            HttpSerializationFormat.CBOR,
            HttpSerializationFormat.CUSTOM,
        ]
        """Serialization format literal - references HttpSerializationFormat StrEnum members."""

        # ═══════════════════════════════════════════════════════════════════
        # ADDITIONAL DOMAIN CLASSES: HTTP, Server, etc. (restaurados)
        # ═══════════════════════════════════════════════════════════════════

        class HTTP:
            """HTTP protocol-specific constants."""

            class Protocol(StrEnum):
                """HTTP protocol enumeration.

                DRY Pattern:
                    StrEnum is the single source of truth. Use Protocol.HTTP.value
                    or Protocol.HTTP directly - no base strings needed.
                """

                HTTP = "http"
                HTTPS = "https"
                HTTP_1_1 = "http/1.1"
                HTTP_2 = "http/2"
                HTTP_3 = "http/3"

            # Supported protocols - using frozenset for immutability
            # DRY Pattern: References Protocol enum members - NO string duplication!
            SUPPORTED_PROTOCOLS: Final[AbstractSet[str]] = frozenset({
                Protocol.HTTP.value,
                Protocol.HTTPS.value,
                Protocol.HTTP_1_1.value,
                Protocol.HTTP_2.value,
            })
            """Supported HTTP protocols - references Protocol enum members."""
            SUPPORTED_PROTOCOLS_WITH_HTTP3: Final[AbstractSet[str]] = frozenset({
                Protocol.HTTP.value,
                Protocol.HTTPS.value,
                Protocol.HTTP_1_1.value,
                Protocol.HTTP_2.value,
                Protocol.HTTP_3.value,
            })
            """Supported HTTP protocols including HTTP/3 - references Protocol enum members."""

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
                """WebSocket message type enumeration.

                DRY Pattern:
                    StrEnum is the single source of truth. Use MessageType.TEXT.value
                    or MessageType.TEXT directly - no base strings needed.
                """

                TEXT = "text"
                BINARY = "binary"

            class Protocol(StrEnum):
                """WebSocket protocol enumeration.

                DRY Pattern:
                    StrEnum is the single source of truth. Use Protocol.WS.value
                    or Protocol.WS directly - no base strings needed.
                """

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
                """SSE protocol enumeration.

                DRY Pattern:
                    StrEnum is the single source of truth. Use Protocol.SSE.value
                    or Protocol.SSE directly - no base strings needed.
                """

                SSE = "sse"
                SERVER_SENT_EVENTS = "server-sent-events"
                EVENTSOURCE = "eventsource"

        class GraphQL:
            """GraphQL protocol constants."""

            class Protocol(StrEnum):
                """GraphQL protocol enumeration.

                DRY Pattern:
                    StrEnum is the single source of truth. Use Protocol.GRAPHQL.value
                    or Protocol.GRAPHQL directly - no base strings needed.
                """

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

    # ═══════════════════════════════════════════════════════════════════
    # PROTOCOL LITERALS - Defined at class level to reference sibling classes
    # ═══════════════════════════════════════════════════════════════════
    # Note: HTTP, WebSocket, SSE, and GraphQL protocol Literals are defined
    # after the class definition to avoid forward reference issues.
    # The StrEnum types themselves provide type safety and can be used directly.


c = FlextApiConstants  # Runtime alias (not TypeAlias to avoid PYI042)

__all__ = [
    "FlextApiConstants",
    "c",
]
