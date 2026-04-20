"""FlextApi constants - Pure constants using StrEnum + Pydantic 2 patterns.

FLEXT-API domain constants with FlextCore integration. Uses advanced Python 3.13+ features:
- StrEnum for type-safe enumerations with Pydantic 2 validation
- PEP 695 type aliases for strict Literal types
- Nested classes for logical grouping
- Collections.abc for immutable collections

NOTE: Validation/TypeGuard methods are in utilities.py, not here.
Constants classes contain ONLY pure constant definitions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Mapping,
)
from enum import StrEnum, unique
from types import MappingProxyType
from typing import Final

from flext_web import FlextWebConstants, t


class FlextApiConstants(FlextWebConstants):
    """FlextApi domain constants extending FlextConstants."""

    class Api:
        """API domain constants namespace.

        All API-specific constants are organized here for better namespace
        organization and to enable composition with other domain constants.
        """

        @unique
        class Method(StrEnum):
            """HTTP method enumeration - automatic Pydantic validation.

            PYDANTIC MODELS:
            model_config: ClassVar[m.ConfigDict] = ConfigDict(use_enum_values=True)
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

        @unique
        class ProtocolMethod(StrEnum):
            """Protocol route method enumeration for special handlers (WS, SSE, GRAPHQL).

            These are pseudo-HTTP methods used to route requests to protocol-specific
            handlers. They are NOT standard HTTP methods and require special handling.

            DRY Pattern:
                StrEnum is the single source of truth. Use ProtocolMethod.WS.value
                or ProtocolMethod.WS directly in route registration and dispatching.
            """

            WS = "WS"
            SSE = "SSE"
            GRAPHQL = "GRAPHQL"

        class MethodLiterals:
            """Lowercase HTTP method literals for case-insensitive comparisons."""

            GET_LOWER: Final[str] = "get"
            POST_LOWER: Final[str] = "post"
            PUT_LOWER: Final[str] = "put"
            DELETE_LOWER: Final[str] = "delete"
            PATCH_LOWER: Final[str] = "patch"
            HEAD_LOWER: Final[str] = "head"
            OPTIONS_LOWER: Final[str] = "options"

        VALID_HTTP_METHODS_LOWER: Final[frozenset[str]] = frozenset({
            "get",
            "post",
            "put",
            "delete",
            "patch",
            "head",
            "options",
            "connect",
            "trace",
        })
        "Lowercase HTTP methods for validation."

        VALID_PROTOCOL_METHODS: Final[frozenset[str]] = frozenset({
            member.value for member in ProtocolMethod.__members__.values()
        })
        "Valid protocol route methods (WS, SSE, GRAPHQL)."

        @unique
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

        @unique
        class WebhookDeliveryStatus(StrEnum):
            """Webhook delivery status enumeration (single source of truth).

            DRY Pattern:
                StrEnum is the single source of truth. Use WebhookDeliveryStatus.DELIVERED.value
                or WebhookDeliveryStatus.DELIVERED directly - no base strings needed.

            This enum defines all possible states for webhook event delivery attempts.
            """

            DELIVERED = "delivered"
            DELIVERED_AFTER_RETRY = "delivered_after_retry"
            FAILED = "failed"

        @unique
        class WebhookAlgorithm(StrEnum):
            """HMAC algorithm enumeration for webhook signature verification.

            DRY Pattern:
                StrEnum is the single source of truth. Use WebhookAlgorithm.SHA256.value
                or WebhookAlgorithm.SHA256 directly - no base strings needed.
            """

            SHA256 = "sha256"
            SHA512 = "sha512"

        @unique
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

        @unique
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

        @unique
        class OpenApiSecuritySchemeType(StrEnum):
            """OpenAPI security scheme type enumeration.

            DRY Pattern:
                StrEnum is the single source of truth. Use OpenApiSecuritySchemeType.API_KEY.value
                or OpenApiSecuritySchemeType.API_KEY directly - no base strings needed.
            """

            API_KEY = "apiKey"
            HTTP = "http"
            OAUTH2 = "oauth2"
            OPEN_ID_CONNECT = "openIdConnect"

        VALID_OPENAPI_SECURITY_SCHEME_TYPES: Final[frozenset[str]] = frozenset({
            member.value for member in OpenApiSecuritySchemeType.__members__.values()
        })
        "Immutable set of valid OpenAPI security scheme types."

        ACTIVE_METHODS: Final[frozenset[str]] = frozenset({
            "GET",
            "POST",
            "PUT",
            "DELETE",
        })
        "Active HTTP methods for operations."
        SAFE_METHODS: Final[frozenset[str]] = frozenset({
            "GET",
            "HEAD",
            "OPTIONS",
            "TRACE",
        })
        "Safe HTTP methods (no side effects)."
        TERMINAL_STATUSES: Final[frozenset[str]] = frozenset({
            "completed",
            "failed",
            "error",
        })
        "Terminal operation statuses."
        SUCCESS_STATUSES: Final[frozenset[str]] = frozenset({"success", "completed"})
        "Success operation statuses."
        "Immutable set of all valid HTTP methods for O(1) validation."
        VALID_STATUSES: Final[frozenset[str]] = frozenset(
            member.value for member in Status.__members__.values()
        )
        "Immutable set of all valid operation statuses."
        "Immutable set of all valid content types."
        "Active HTTP methods for validation - references Method enum members."
        "Safe HTTP methods for validation - references Method enum members."
        DEFAULT_TIMEOUT: Final[float] = float(FlextWebConstants.DEFAULT_TIMEOUT_SECONDS)
        "Default request timeout in seconds."
        "Default maximum retry attempts."
        DEFAULT_BASE_URL: Final[str] = (
            f"http://{FlextWebConstants.DEFAULT_HOST}:{FlextWebConstants.FLEXT_API_PORT}"
        )
        "Default base URL for API operations."
        "API version string."
        MAX_URL_LENGTH: Final[int] = 2048
        "Maximum URL length."
        "Minimum URL length."
        MIN_PORT: Final[int] = 1
        "Minimum port number."
        MAX_PORT: Final[int] = 65535
        "Maximum port number."
        BACKOFF_FACTOR: Final[float] = 0.5
        "Exponential backoff factor."
        HTTP_SUCCESS_MIN: Final[int] = 200
        "Minimum HTTP success status code."
        HTTP_SUCCESS_MAX: Final[int] = 300
        "Maximum HTTP success status code."
        HTTP_REDIRECT_MIN: Final[int] = 300
        "Minimum HTTP redirect status code."
        HTTP_REDIRECT_MAX: Final[int] = 400
        "Maximum HTTP redirect status code."
        HTTP_CLIENT_ERROR_MIN: Final[int] = 400
        "Minimum HTTP client error status code."
        HTTP_CLIENT_ERROR_MAX: Final[int] = 500
        "Maximum HTTP client error status code."
        HTTP_STATUS_MIN: Final[int] = 100
        "Minimum valid HTTP status code."
        HTTP_STATUS_MAX: Final[int] = 599
        "Maximum valid HTTP status code."
        HTTP_SERVER_ERROR_MIN: Final[int] = 500
        "Minimum HTTP server error status code."
        HTTP_ERROR_MIN: Final[int] = 400
        "Minimum HTTP error status code."
        "Template for successful API responses."
        "Template for error API responses."
        HEADER_CONTENT_TYPE: Final[str] = "Content-Type"
        "Content-Type header name."
        HEADER_AUTHORIZATION: Final[str] = "Authorization"
        "Authorization header name."
        "User-Agent header name."
        HEADER_ACCEPT: Final[str] = "Accept"
        "Accept header name."
        "Default User-Agent string."
        "Default retry count."
        "Rate limit requests per window."
        "Rate limit window in seconds."
        VALIDATION_LIMITS: Final[Mapping[str, t.Numeric]] = MappingProxyType({
            "MAX_URL_LENGTH": MAX_URL_LENGTH,
            "MIN_TIMEOUT": 0.1,
            "MAX_TIMEOUT": 300.0,
            "MIN_RETRIES": 0,
            "MAX_RETRIES": 10,
        })
        "Validation limits mapping."
        "CORS configuration."
        "URL configuration mapping."

        class HTTP:
            """HTTP protocol-specific constants."""

            @unique
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

            SUPPORTED_PROTOCOLS: Final[frozenset[str]] = frozenset({
                Protocol.HTTP.value,
                Protocol.HTTPS.value,
                Protocol.HTTP_1_1.value,
                Protocol.HTTP_2.value,
            })
            "Supported HTTP protocols - references Protocol enum members."
            SUPPORTED_PROTOCOLS_WITH_HTTP3: Final[frozenset[str]] = frozenset({
                Protocol.HTTP.value,
                Protocol.HTTPS.value,
                Protocol.HTTP_1_1.value,
                Protocol.HTTP_2.value,
                Protocol.HTTP_3.value,
            })
            "Supported HTTP protocols including HTTP/3 - references Protocol enum members."

        class Server:
            """Server configuration constants."""

            DEFAULT_HOST: Final[str] = "127.0.0.1"
            DEFAULT_PORT: Final[int] = 8000

        class WebSocket:
            """WebSocket protocol constants."""

            DEFAULT_PING_INTERVAL: Final[float] = 20.0
            "Default ping interval in seconds."
            DEFAULT_PING_TIMEOUT: Final[float] = 20.0
            "Default ping timeout in seconds."
            DEFAULT_CLOSE_TIMEOUT: Final[float] = 10.0
            "Default close timeout in seconds."
            DEFAULT_MAX_SIZE: Final[int] = 2**20
            "Default maximum message size in bytes (1 MiB)."
            DEFAULT_MAX_QUEUE: Final[int] = 16
            "Default maximum queue size for outgoing messages."
            COMPRESSION_DEFLATE: Final[str] = "deflate"
            "Deflate compression method identifier."
            DEFAULT_RECONNECT_MAX_ATTEMPTS: Final[int] = 5
            "Default maximum reconnection attempts."
            DEFAULT_RECONNECT_BACKOFF_FACTOR: Final[float] = 1.5
            "Default reconnection backoff multiplier."
            STATUS_SWITCHING_PROTOCOLS: Final[int] = 101
            "HTTP 101 Switching Protocols status code for WebSocket upgrade."

            @unique
            class MessageType(StrEnum):
                """WebSocket message type enumeration.

                DRY Pattern:
                    StrEnum is the single source of truth. Use MessageType.TEXT.value
                    or MessageType.TEXT directly - no base strings needed.
                """

                TEXT = "text"
                BINARY = "binary"

            @unique
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
            "Default retry timeout in milliseconds."
            DEFAULT_CONNECT_TIMEOUT: Final[float] = 10.0
            "Default connect timeout in seconds."
            DEFAULT_READ_TIMEOUT: Final[float] = 60.0
            "Default read timeout in seconds."
            DEFAULT_RECONNECT_MAX_ATTEMPTS: Final[int] = 5
            "Default maximum reconnection attempts."
            DEFAULT_RECONNECT_BACKOFF_FACTOR: Final[float] = 1.5
            "Default reconnection backoff multiplier."

            @unique
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

            @unique
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

            RETRYABLE_STATUS_CODES: Final[frozenset[int]] = frozenset({
                408,
                429,
                500,
                502,
                503,
                504,
            })
            "HTTP status codes eligible for automatic retry."

        class HTTPClient:
            """HTTP client connection constants."""

            DEFAULT_MAX_CONNECTIONS: Final[int] = 100
            "Default maximum number of connections in the pool."
            DEFAULT_MAX_KEEPALIVE_CONNECTIONS: Final[int] = 20
            "Default maximum number of keepalive connections."

        class PaginationDefaults:
            """Pagination default values."""


__all__: list[str] = ["FlextApiConstants", "c"]

c = FlextApiConstants
