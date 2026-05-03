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

from httpx import HTTPError as _HttpxError

from flext_web import FlextWebConstants, c, t


class FlextApiConstants(FlextWebConstants):
    """FlextApi domain constants extending FlextWebConstants via MRO."""

    class Api:
        """API domain constants namespace.

        All API-specific constants are organized here for better namespace
        organization and to enable composition with other domain constants.
        """

        EXC_HTTPX: Final[tuple[type[Exception], ...]] = (
            ConnectionError,
            KeyError,
            TypeError,
            ValueError,
            _HttpxError,
        )
        """HTTP boundary catch including httpx.HTTPError for httpx-based clients."""

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

            SSE = "SSE"

        # ===== HTTP Method Literals =====
        METHOD_LITERALS_HEAD_LOWER: Final[str] = "head"
        "Lowercase HEAD method literal."

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

            FAILED = "failed"

        @unique
        class WebhookAlgorithm(StrEnum):
            """HMAC algorithm enumeration for webhook signature verification.

            DRY Pattern:
                StrEnum is the single source of truth. Use WebhookAlgorithm.SHA256.value
                or WebhookAlgorithm.SHA256 directly - no base strings needed.
            """

            SHA256 = "sha256"

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
        "Immutable set of all valid HTTP methods for O(1) validation."
        VALID_STATUSES: Final[frozenset[str]] = frozenset(
            member.value for member in Status.__members__.values()
        )
        "Immutable set of all valid operation statuses."
        "Immutable set of all valid content types."
        "Active HTTP methods for validation - references Method enum members."
        "Safe HTTP methods for validation - references Method enum members."
        DEFAULT_TIMEOUT: Final[float] = float(c.DEFAULT_TIMEOUT_SECONDS)
        "Default request timeout in seconds."
        "Default maximum retry attempts."
        DEFAULT_BASE_URL: Final[str] = "http://localhost:8000"
        "Default base URL for API operations."
        "API version string."
        MAX_URL_LENGTH: Final[int] = 2048
        "Maximum URL length."
        "Minimum URL length."
        MIN_PORT: Final[int] = 1
        "Minimum port number."
        MAX_PORT: Final[int] = 65535
        "Maximum port number."
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

        # ===== HTTP Protocol =====
        @unique
        class HttpProtocol(StrEnum):
            """HTTP protocol enumeration - all HTTP/HTTPS variants."""

            HTTP = "http"
            HTTPS = "https"

        # ===== Server Configuration =====

        # ===== WebSocket Protocol =====

        # ===== Server-Sent Events (SSE) Protocol =====

        # ===== HTTP Retry =====

        # ===== HTTP Client =====


c = FlextApiConstants

__all__: t.MutableSequenceOf[str] = ["FlextApiConstants", "c"]
