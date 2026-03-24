"""FLEXT API Models - HTTP Domain Models extending flext-core.

Unified namespace class that extends flext-core FlextModels with HTTP-specific
domain entities. Provides Pydantic v2 models for HTTP operations following
Clean Architecture patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time
from collections.abc import Mapping, Sequence
from typing import Annotated, ClassVar, Self
from urllib.parse import ParseResult, urlparse

from flext_core import FlextModels
from flext_web import FlextWebModels
from pydantic import (
    BeforeValidator,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
)

from flext_api import c, t, u


def _normalize_request_body(v: t.ApiJsonValue) -> t.Api.RequestBody:
    """Normalize body - empty dict is valid."""
    if v is None:
        return {}
    return u.Api.RequestUtils.to_request_body(v)


def _normalize_response_body(v: t.ApiJsonValue) -> t.Api.ResponseBody:
    """Normalize body - None is valid for empty responses (e.g., 204), default is empty dict."""
    if v is None:
        return None  # Explicit None is valid (e.g., for 204 responses)
    return u.Api.RequestUtils.to_request_body(v)


class FlextApiModels(FlextWebModels):
    """HTTP domain models for flext-api.

    Unified namespace class that aggregates all HTTP-specific domain models.
    Uses nested classes following SOLID principles for maximum maintainability.
    Provides Pydantic v2 value objects and entities for HTTP operations.

    Fully compatible with Pydantic v2 with strict type safety and validation.
    """

    class Api:
        """Api Models."""

        # =========================================================================
        # HTTP REQUEST/RESPONSE VALUE OBJECTS (Immutable)
        # =========================================================================

        class HttpRequest(FlextModels.Value):
            """Immutable HTTP request value t.NormalizedValue.

            Represents a complete HTTP request with all necessary parameters.
            Follows Value Object pattern: immutable, compared by value, no identity.
            """

            method: Annotated[
                c.Api.Method | str,
                Field(
                    default="GET",
                    description="HTTP method (GET, POST, PUT, DELETE, PATCH, etc.)",
                    pattern=r"^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|CONNECT|TRACE)$",
                ),
            ]
            url: Annotated[
                t.NonEmptyStr,
                Field(
                    ...,
                    max_length=c.Api.MAX_URL_LENGTH,
                    description="Request URL",
                ),
            ]
            headers: Annotated[
                Mapping[str, str],
                Field(
                    default_factory=dict,
                    description="HTTP request headers",
                ),
            ]
            body: Annotated[
                Annotated[
                    t.Api.RequestBody,
                    BeforeValidator(_normalize_request_body),
                ],
                Field(
                    default_factory=dict,
                    description="Request body",
                ),
            ]

            query_params: Annotated[
                t.Api.WebParams,
                Field(
                    default_factory=dict,
                    description="Query parameters",
                ),
            ]
            timeout: Annotated[
                t.PositiveTimeout,
                Field(
                    default=float(c.Api.DEFAULT_TIMEOUT),
                    description="Request timeout in seconds",
                ),
            ]

            @computed_field
            def content_type(self) -> str:
                """Get content type from headers."""
                # Check Content-Type header (case-insensitive)
                header_content_type = c.Api.HEADER_CONTENT_TYPE
                if header_content_type in self.headers:
                    return self.headers[header_content_type]
                # Check lowercase variant
                if header_content_type.lower() in self.headers:
                    return self.headers[header_content_type.lower()]
                # Default from Constants
                return c.Api.ContentType.JSON

        class HttpResponse(FlextModels.Value):
            """Immutable HTTP response value t.NormalizedValue.

            Represents a complete HTTP response with all returned data.
            Follows Value Object pattern: immutable, compared by value, no identity.
            """

            status_code: Annotated[
                t.HttpStatusCode,
                Field(
                    ...,
                    description=f"HTTP status code ({c.Api.HTTP_STATUS_MIN}-{c.Api.HTTP_STATUS_MAX})",
                ),
            ]
            headers: Annotated[
                Mapping[str, str],
                Field(
                    default_factory=dict,
                    description="HTTP response headers",
                ),
            ]
            body: Annotated[
                Annotated[
                    t.Api.ResponseBody,
                    BeforeValidator(_normalize_response_body),
                ],
                Field(
                    default_factory=dict,
                    description="Response body (empty dict by default, None allowed for 204)",
                ),
            ]

            request_id: Annotated[
                str,
                Field(
                    default="",
                    description="Associated request ID for tracking",
                ),
            ]

            @computed_field
            def is_client_error(self) -> bool:
                """Check if response indicates client error (4xx status code)."""
                return (
                    c.Api.HTTP_CLIENT_ERROR_MIN
                    <= self.status_code
                    < c.Api.HTTP_CLIENT_ERROR_MAX
                )

            @computed_field
            def is_error(self) -> bool:
                """Check if response indicates any error (4xx or 5xx status code)."""
                return self.status_code >= c.Api.HTTP_ERROR_MIN

            @computed_field
            def is_redirect(self) -> bool:
                """Check if response indicates redirect (3xx status code)."""
                return (
                    c.Api.HTTP_REDIRECT_MIN
                    <= self.status_code
                    < c.Api.HTTP_REDIRECT_MAX
                )

            @computed_field
            def is_server_error(self) -> bool:
                """Check if response indicates server error (5xx status code)."""
                return self.status_code >= c.Api.HTTP_SERVER_ERROR_MIN

            @computed_field
            def is_success(self) -> bool:
                """Check if response indicates success (2xx status code)."""
                return (
                    c.Api.HTTP_SUCCESS_MIN <= self.status_code < c.Api.HTTP_SUCCESS_MAX
                )

        # =========================================================================
        # URL AND PARSING MODELS
        # =========================================================================

        class Url(FlextModels.Value):
            """URL parsing and validation model (immutable value t.NormalizedValue)."""

            url: Annotated[
                t.NonEmptyStr,
                Field(
                    ...,
                    max_length=c.Api.MAX_URL_LENGTH,
                    description="Full URL string",
                ),
            ]

            @property
            def _parsed_url(self) -> ParseResult:
                """Parse URL on demand (immutable, no caching needed)."""
                return urlparse(self.url)

            @computed_field
            def fragment(self) -> str:
                """Get URL fragment."""
                parsed_fragment = self._parsed_url.fragment
                if parsed_fragment:
                    return parsed_fragment
                return ""

            @computed_field
            def is_valid(self) -> bool:
                """Check if URL is valid."""
                scheme_value = self._parsed_url.scheme
                netloc_value = self._parsed_url.netloc
                return bool(scheme_value and netloc_value)

            @computed_field
            def netloc(self) -> str:
                """Get network location (host:port)."""
                parsed_netloc = self._parsed_url.netloc
                if parsed_netloc:
                    return parsed_netloc
                return f"{c.Api.Server.DEFAULT_HOST}:{c.Api.Server.DEFAULT_PORT}"

            @computed_field
            def parsed(self) -> ParseResult:
                """Parse the URL."""
                return self._parsed_url

            @computed_field
            def path(self) -> str:
                """Get URL path."""
                parsed_path = self._parsed_url.path
                if parsed_path:
                    return parsed_path
                return "/"

            @computed_field
            def query(self) -> str:
                """Get URL query string."""
                parsed_query = self._parsed_url.query
                if parsed_query:
                    return parsed_query
                return ""

            @computed_field
            def scheme(self) -> str:
                """Get URL scheme (http, https, etc.)."""
                parsed_scheme = self._parsed_url.scheme
                if parsed_scheme:
                    return parsed_scheme
                return c.Api.HTTP.Protocol.HTTPS

        # =========================================================================
        # CONFIGURATION MODELS
        # =========================================================================

        class ClientConfig(FlextModels.Value):
            """HTTP client configuration model (immutable value t.NormalizedValue)."""

            base_url: Annotated[
                str,
                Field(
                    default=c.Api.DEFAULT_BASE_URL,
                    max_length=c.Api.MAX_URL_LENGTH,
                    description="Base URL for all requests",
                ),
            ]
            timeout: Annotated[
                t.PositiveTimeout,
                Field(
                    default=float(c.Api.DEFAULT_TIMEOUT),
                    description="Request timeout in seconds",
                ),
            ]
            max_retries: Annotated[
                t.RetryCount,
                Field(
                    default=c.DEFAULT_MAX_RETRY_ATTEMPTS,
                    description="Maximum retry attempts",
                ),
            ]
            headers: Annotated[
                Mapping[str, str],
                Field(
                    default_factory=dict,
                    description="Default headers for all requests",
                ),
            ]
            verify_ssl: Annotated[
                bool,
                Field(
                    default=True,
                    description="Verify SSL certificates",
                ),
            ]

            @computed_field
            def is_configured(self) -> bool:
                """Check if configuration is valid."""
                if not self.base_url:
                    return False
                return self.timeout > 0

        # =========================================================================
        # PAGINATION MODELS
        # =========================================================================

        class PaginationInfo(FlextModels.Value):
            """Pagination information model for HTTP operations (immutable value t.NormalizedValue)."""

            page: Annotated[
                t.PositiveInt,
                Field(
                    default=1,
                    description="Current page number (1-based)",
                ),
            ]
            page_size: Annotated[
                t.BatchSize,
                Field(
                    default=c.DEFAULT_PAGE_SIZE,
                    description="Items per page",
                ),
            ]
            total_items: Annotated[
                t.NonNegativeInt,
                Field(
                    default=0,
                    description="Total number of items",
                ),
            ]
            total_pages: Annotated[
                t.NonNegativeInt,
                Field(
                    default=0,
                    description="Total number of pages",
                ),
            ]

            @computed_field
            def has_next(self) -> bool:
                """Check if there are more pages."""
                if self.total_pages == 0:
                    return False
                return self.page < self.total_pages

            @computed_field
            def has_previous(self) -> bool:
                """Check if there are previous pages."""
                return self.page > 1

            @computed_field
            def offset(self) -> int:
                """Calculate offset for database queries."""
                return (self.page - 1) * self.page_size

        # =========================================================================
        # ERROR MODELS
        # =========================================================================

        class Error(FlextModels.Value):
            """HTTP error response model (immutable value t.NormalizedValue)."""

            message: Annotated[
                str,
                Field(..., description="Human-readable error message"),
            ]
            error_code: Annotated[
                str,
                Field(
                    default="",
                    description="Machine-readable error code",
                ),
            ]
            status_code: Annotated[
                t.HttpStatusCode,
                Field(
                    default=c.Api.HTTP_SERVER_ERROR_MIN,
                    description="HTTP status code",
                ),
            ]
            details: Annotated[
                t.Api.JsonObject,
                Field(
                    default_factory=dict,
                    description="Additional error details",
                ),
            ]
            request_id: Annotated[
                str,
                Field(
                    default="",
                    description="Associated request ID for tracking",
                ),
            ]

            @computed_field
            def is_client_error(self) -> bool:
                """Check if error is client-side (4xx)."""
                return (
                    c.Api.HTTP_CLIENT_ERROR_MIN
                    <= self.status_code
                    < c.Api.HTTP_CLIENT_ERROR_MAX
                )

            @computed_field
            def is_server_error(self) -> bool:
                """Check if error is server-side (5xx)."""
                return self.status_code >= c.Api.HTTP_SERVER_ERROR_MIN

        # =========================================================================
        # QUERY/FILTER MODELS
        # =========================================================================

        class QueryParams(FlextModels.Value):
            """Query parameters model (immutable value t.NormalizedValue)."""

            params: Annotated[
                t.Api.WebParams,
                Field(
                    default_factory=dict,
                    description="Query parameters",
                ),
            ]

            def get_param(self, name: str) -> t.Api.WebParamValue:
                """Get query parameter value."""
                if name in self.params:
                    return self.params[name]
                return ""

            def with_param(self, name: str, value: str | Sequence[str]) -> Self:
                """Return new instance with updated parameter (functional pattern)."""
                updated_params = {**self.params, name: value}
                return self.model_copy(update={"params": updated_params})

        class Headers(FlextModels.Value):
            """HTTP headers model (immutable value t.NormalizedValue)."""

            headers: Annotated[
                Mapping[str, str],
                Field(
                    default_factory=dict,
                    description="HTTP headers",
                ),
            ]

            def get_header(self, name: str) -> str:
                """Get header value (case-insensitive)."""
                for key, value in self.headers.items():
                    if key.lower() == name.lower():
                        return value
                return ""

            def with_header(self, name: str, value: str) -> Self:
                """Return new instance with updated header (functional pattern)."""
                updated_headers = {**self.headers, name: value}
                return self.model_copy(update={"headers": updated_headers})

            def without_header(self, name: str) -> Self:
                """Return new instance without header (case-insensitive, functional pattern)."""

                # Use u.filter() for unified filtering (DSL pattern)
                def matches_header_key(k: str) -> bool:
                    return k.lower() == name.lower()

                keys_to_remove = u.filter(
                    list(self.headers.keys()),
                    matches_header_key,
                )
                updated_headers = {
                    k: v for k, v in self.headers.items() if k not in keys_to_remove
                }
                return self.model_copy(update={"headers": updated_headers})

        @classmethod
        def create_config(
            cls,
            base_url: str | None = None,
            timeout: float | None = None,
            max_retries: int | None = None,
            headers: Mapping[str, str] | None = None,
            *,
            verify_ssl: bool = True,
        ) -> FlextApiModels.Api.ClientConfig:
            """Create ClientConfig from parameters.

            Args:
            base_url: Base URL for all requests (uses Constants default if None)
            timeout: Request timeout in seconds (uses Constants default if None)
            max_retries: Maximum retry attempts (uses Constants default if None)
            headers: Default headers for all requests (None for empty dict)
            verify_ssl: Verify SSL certificates

            Returns:
            ClientConfig instance with defaults from Constants

            """
            # Use Constants defaults when None - Config has priority but uses Constants as base
            config_base_url = (
                base_url if base_url is not None else c.Api.DEFAULT_BASE_URL
            )
            config_timeout = (
                float(timeout) if timeout is not None else float(c.Api.DEFAULT_TIMEOUT)
            )
            config_max_retries = (
                max_retries if max_retries is not None else c.DEFAULT_MAX_RETRY_ATTEMPTS
            )
            if headers is None:
                config_headers: Mapping[str, str] = {}
            else:
                config_headers = dict(headers.items())

            return cls.ClientConfig(
                base_url=config_base_url,
                timeout=config_timeout,
                max_retries=config_max_retries,
                headers=config_headers,
                verify_ssl=verify_ssl,
            )

        # =========================================================================
        # FACTORY METHODS - Model creation utilities
        # =========================================================================

        @classmethod
        def create_response(
            cls,
            status_code: int,
            body: t.Api.ResponseBody | None = None,
            headers: Mapping[str, str] | None = None,
            request_id: str | None = None,
        ) -> FlextApiModels.Api.HttpResponse:
            """Create HttpResponse from parameters.

            Args:
            status_code: HTTP status code
            body: Response body (JSON, string, bytes, or None for empty dict)
            headers: Response headers dictionary (None for empty dict)
            request_id: Associated request ID for tracking (None for empty string)

            Returns:
            HttpResponse instance with defaults from model

            """
            # Use model defaults - body defaults to empty dict, not None
            response_body: t.Api.ResponseBody = body if body is not None else {}
            if headers is None:
                response_headers: Mapping[str, str] = {}
            else:
                response_headers = dict(headers.items())
            response_id: str = request_id if request_id is not None else ""

            return cls.HttpResponse(
                status_code=status_code,
                body=response_body,
                headers=response_headers,
                request_id=response_id,
            )

        # =========================================================================
        # SCHEMA FIELD MODELS - Moved from schemas/_shared.py
        # =========================================================================

        class DictField(FlextModels.Value):
            """Pydantic model for validating dictionary fields (immutable value t.NormalizedValue)."""

            value: Annotated[
                Mapping[str, t.ContainerValue],
                Field(default_factory=dict, description="Dictionary value"),
            ]

        class StringField(FlextModels.Value):
            """Pydantic model for validating string fields (immutable value t.NormalizedValue)."""

            value: Annotated[str, Field(..., description="String value")]

        class IntField(FlextModels.Value):
            """Pydantic model for validating integer fields (immutable value t.NormalizedValue)."""

            value: Annotated[int, Field(..., description="Integer value")]

        # =========================================================================
        # PRIVATE INTERNAL MODELS (moved from protocol_impls for MRO compliance)
        # =========================================================================

        class _HttpRequestCallArgs(FlextModels.Value):
            """Internal model for validating HTTP request call arguments."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                arbitrary_types_allowed=True
            )

            method: Annotated[str, Field(..., description="HTTP method")]
            url: Annotated[str, Field(..., description="Request URL")]
            headers: Annotated[
                Mapping[str, str],
                Field(default_factory=dict, description="HTTP headers"),
            ]
            params: Annotated[
                Mapping[str, str],
                Field(default_factory=dict, description="Query parameters"),
            ]
            json_body: Annotated[
                t.Container | None,
                Field(default=None, description="JSON request body"),
            ]
            content: Annotated[
                bytes | None,
                Field(default=None, description="Raw content body"),
            ]
            timeout: Annotated[
                float | None,
                Field(default=None, description="Request timeout"),
            ]

        class _MappingBodyModel(FlextModels.Value):
            """Internal model for wrapping mapping body data."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                arbitrary_types_allowed=True
            )

            body: Annotated[
                Mapping[str, t.ContainerValue],
                Field(..., description="Request body as mapping"),
            ]

        class _HttpClientRequestOptions(FlextModels.Value):
            """Internal model for HTTP client request options."""

            model_config: ClassVar[ConfigDict] = ConfigDict(
                arbitrary_types_allowed=True
            )

            params: Annotated[
                Mapping[str, str] | None,
                Field(default=None, description="Query parameters"),
            ]
            json_data: Annotated[
                t.Container | None,
                Field(default=None, description="JSON body"),
            ]
            content: Annotated[
                bytes | None,
                Field(default=None, description="Raw content body"),
            ]
            data: Annotated[
                Mapping[str, t.ContainerValue] | None,
                Field(default=None, description="Form data"),
            ]
            timeout: Annotated[
                float | None,
                Field(default=None, description="Request timeout"),
            ]
            headers: Annotated[
                Mapping[str, str],
                Field(default_factory=dict, description="Request headers"),
            ]

        class _HeadersRequest(FlextModels.Value):
            """Encapsulates RFC header constraint for requests."""

            headers: Annotated[Mapping[str, str], Field(default_factory=dict)]

        class _MethodRequest(FlextModels.Value):
            """Encapsulates RFC method constraint for requests."""

            method: Annotated[str, Field(min_length=1)]

            @field_validator("method")
            @classmethod
            def _validate_method(cls, value: str) -> str:
                method_upper = value.upper()
                valid_methods = {
                    "GET",
                    "POST",
                    "PUT",
                    "DELETE",
                    "PATCH",
                    "HEAD",
                    "OPTIONS",
                    "TRACE",
                    "CONNECT",
                }
                if method_upper not in valid_methods:
                    msg = f"Invalid HTTP method: {method_upper} (RFC 7231)"
                    raise ValueError(msg)
                return method_upper

        class _TimeoutRequest(FlextModels.Value):
            """Encapsulates timeout constraints for RFC request URLs."""

            timeout: Annotated[t.PositiveTimeout, Field(...)]

        class _UrlRequest(FlextModels.Value):
            """Encapsulates URL validation constraints for RFC requests."""

            url: Annotated[str, Field(min_length=1)]

            @field_validator("url")
            @classmethod
            def _validate_url(cls, value: str) -> str:
                if not value.strip():
                    msg = "URL cannot be empty (RFC 7230)"
                    raise ValueError(msg)
                if not value.startswith(("http://", "https://")):
                    msg = "URL must start with http:// or https://"
                    raise ValueError(msg)
                return value

        class _StatusCodeValue(FlextModels.Value):
            """Validates status code values according to RFC conventions."""

            status_code: Annotated[t.HttpStatusCode, Field(...)]

        class _SendRequestSseOptions(FlextModels.Value):
            """Options for SSE request sending behavior."""

            method: Annotated[str, Field(default="GET", min_length=1)]
            max_events: Annotated[t.PositiveInt, Field(default=1)]
            auto_reconnect: Annotated[bool | None, Field(default=None)]
            reconnect_max_attempts: Annotated[
                t.NonNegativeInt | None, Field(default=None)
            ]
            reconnect_backoff_factor: Annotated[
                t.PositiveFloat | None, Field(default=None)
            ]
            retry_timeout: Annotated[t.NonNegativeInt | None, Field(default=None)]

        class _SendRequestWsOptions(FlextModels.Value):
            """Options for sending a WebSocket message request."""

            message: Annotated[str | bytes | None, Field(default=None)]
            message_type: Annotated[
                str,
                Field(default="text", min_length=1),
            ]

        class _InboundMessage(FlextModels.Value):
            """Model for inbound WebSocket messages."""

            message: str | bytes

        # =========================================================================
        # STORAGE MODELS
        # =========================================================================

        class Storage:
            """Storage-related models namespace."""

            class Metadata(FlextModels.Value):
                """Internal metadata for stored values (using Pydantic for validation)."""

                value: t.ApiJsonValue
                timestamp: str
                ttl: float | int | None = None
                created_at: Annotated[float, Field(default_factory=time.time)]

                def is_expired(self) -> bool:
                    """Check if entry has expired using Pydantic-validated TTL."""
                    if self.ttl is None:
                        return False
                    elapsed = time.time() - self.created_at
                    return elapsed > self.ttl

            class Stats(FlextModels.Value):
                """Storage statistics using Pydantic (automatic validation)."""

                total_operations: int = 0
                cache_hits: int = 0
                cache_misses: int = 0
                hit_ratio: float = 0.0
                storage_size: int = 0
                memory_usage: int = 0
                namespace: str = "flext"

    # =========================================================================
    # CLASS-LEVEL ALIASES FOR FLAT NAMESPACE ACCESS
    # =========================================================================
    # Expose nested Api models at root level for convenient access
    HttpRequest = Api.HttpRequest
    HttpResponse = Api.HttpResponse
    ClientConfig = Api.ClientConfig
    Url = Api.Url
    PaginationInfo = Api.PaginationInfo
    Error = Api.Error
    QueryParams = Api.QueryParams
    Headers = Api.Headers
    DictField = Api.DictField
    StringField = Api.StringField
    IntField = Api.IntField
    Storage = Api.Storage
    create_config = Api.create_config
    create_response = Api.create_response


__all__ = ["FlextApiModels", "m"]

m = FlextApiModels
