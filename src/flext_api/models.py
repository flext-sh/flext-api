"""FLEXT API Models - HTTP Domain Models extending flext-core.

Unified namespace class that extends flext-core FlextModels with HTTP-specific
domain entities. Provides Pydantic v2 models for HTTP operations following
Clean Architecture patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time
from typing import Self
from urllib.parse import ParseResult, urlparse

from flext_core import FlextModels
from pydantic import Field, computed_field, field_validator

from flext_api.constants import c
from flext_api.typings import t
from flext_api.utilities import u


class FlextApiModels(FlextModels):
    """HTTP domain models for flext-api.

    Unified namespace class that aggregates all HTTP-specific domain models.
    Uses nested classes following SOLID principles for maximum maintainability.
    Provides Pydantic v2 value objects and entities for HTTP operations.

    Fully compatible with Pydantic v2 with strict type safety and validation.
    """

    def __init_subclass__(cls, **kwargs: t.GeneralValueType) -> None:
        """Warn when FlextApiModels is subclassed directly."""
        super().__init_subclass__(**kwargs)
        u.Deprecation.warn_once(
            f"subclass:{cls.__name__}",
            "Subclassing FlextApiModels is deprecated. Use FlextModels.Api instead.",
        )

    # =========================================================================
    # HTTP REQUEST/RESPONSE VALUE OBJECTS (Immutable)
    # =========================================================================

    class HttpRequest(FlextModels.Value):
        """Immutable HTTP request value object.

        Represents a complete HTTP request with all necessary parameters.
        Follows Value Object pattern: immutable, compared by value, no identity.
        """

        method: c.Api.Method | str = Field(
            default="GET",
            min_length=3,
            max_length=8,
            description="HTTP method (GET, POST, PUT, DELETE, PATCH, etc.)",
            pattern=r"^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|CONNECT|TRACE)$",
        )
        url: str = Field(..., min_length=1, max_length=2048, description="Request URL")
        headers: dict[str, str] = Field(
            default_factory=dict,
            description="HTTP request headers",
        )
        body: t.Api.RequestBody = Field(
            default_factory=dict,
            description="Request body",
        )

        @field_validator("body", mode="before")
        @classmethod
        def normalize_body(cls, v: t.GeneralValueType) -> t.Api.RequestBody:
            """Normalize body - empty dict is valid."""
            if v is None:
                return {}
            if isinstance(v, dict):
                return v
            if isinstance(v, (str, bytes)):
                return v
            return {}

        query_params: t.Api.WebParams = Field(
            default_factory=dict,
            description="Query parameters",
        )
        timeout: float = Field(
            default=float(c.Api.DEFAULT_TIMEOUT),
            ge=float(c.Api.VALIDATION_LIMITS["MIN_TIMEOUT"]),
            le=float(c.Api.VALIDATION_LIMITS["MAX_TIMEOUT"]),
            description="Request timeout in seconds",
        )

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
        """Immutable HTTP response value object.

        Represents a complete HTTP response with all returned data.
        Follows Value Object pattern: immutable, compared by value, no identity.
        """

        status_code: int = Field(
            ...,
            ge=100,
            le=599,
            description="HTTP status code (100-599)",
        )
        headers: dict[str, str] = Field(
            default_factory=dict,
            description="HTTP response headers",
        )
        body: t.Api.ResponseBody = Field(
            default_factory=dict,
            description="Response body (empty dict by default, None allowed for 204)",
        )

        @field_validator("body", mode="before")
        @classmethod
        def normalize_body(cls, v: t.GeneralValueType) -> t.Api.ResponseBody:
            """Normalize body - None is valid for empty responses (e.g., 204), default is empty dict."""
            if v is None:
                return None  # Explicit None is valid (e.g., for 204 responses)
            if isinstance(v, dict):
                return v
            if isinstance(v, (str, bytes)):
                return v
            # Default to empty dict if not specified
            return {}

        request_id: str = Field(
            default="",
            description="Associated request ID for tracking",
        )

        @computed_field
        def is_success(self) -> bool:
            """Check if response indicates success (2xx status code)."""
            return c.Api.HTTP_SUCCESS_MIN <= self.status_code < c.Api.HTTP_SUCCESS_MAX

        @computed_field
        def is_redirect(self) -> bool:
            """Check if response indicates redirect (3xx status code)."""
            return c.Api.HTTP_REDIRECT_MIN <= self.status_code < c.Api.HTTP_REDIRECT_MAX

        @computed_field
        def is_client_error(self) -> bool:
            """Check if response indicates client error (4xx status code)."""
            return (
                c.Api.HTTP_CLIENT_ERROR_MIN
                <= self.status_code
                < c.Api.HTTP_CLIENT_ERROR_MAX
            )

        @computed_field
        def is_server_error(self) -> bool:
            """Check if response indicates server error (5xx status code)."""
            return self.status_code >= c.Api.HTTP_SERVER_ERROR_MIN

        @computed_field
        def is_error(self) -> bool:
            """Check if response indicates any error (4xx or 5xx status code)."""
            return self.status_code >= c.Api.HTTP_ERROR_MIN

    # =========================================================================
    # URL AND PARSING MODELS
    # =========================================================================

    class Url(FlextModels.Value):
        """URL parsing and validation model (immutable value object)."""

        url: str = Field(
            ...,
            min_length=1,
            max_length=2048,
            description="Full URL string",
        )

        @property
        def _parsed_url(self) -> ParseResult:
            """Parse URL on demand (immutable, no caching needed)."""
            return urlparse(self.url)

        @computed_field
        def parsed(self) -> ParseResult:
            """Parse the URL."""
            return self._parsed_url

        @computed_field
        def scheme(self) -> str:
            """Get URL scheme (http, https, etc.)."""
            parsed_scheme = self._parsed_url.scheme
            if parsed_scheme:
                return parsed_scheme
            return c.Api.HTTP.Protocol.HTTPS

        @computed_field
        def netloc(self) -> str:
            """Get network location (host:port)."""
            parsed_netloc = self._parsed_url.netloc
            if parsed_netloc:
                return parsed_netloc
            return f"{c.Api.Server.DEFAULT_HOST}:{c.Api.Server.DEFAULT_PORT}"

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

    # =========================================================================
    # CONFIGURATION MODELS
    # =========================================================================

    class ClientConfig(FlextModels.Value):
        """HTTP client configuration model (immutable value object)."""

        base_url: str = Field(
            default=c.Api.DEFAULT_BASE_URL,
            max_length=c.Api.MAX_URL_LENGTH,
            description="Base URL for all requests",
        )
        timeout: float = Field(
            default=float(c.Api.DEFAULT_TIMEOUT),
            ge=float(c.Api.VALIDATION_LIMITS["MIN_TIMEOUT"]),
            le=float(c.Api.VALIDATION_LIMITS["MAX_TIMEOUT"]),
            description="Request timeout in seconds",
        )
        max_retries: int = Field(
            default=c.Api.DEFAULT_MAX_RETRIES,
            ge=int(c.Api.VALIDATION_LIMITS["MIN_RETRIES"]),
            le=int(c.Api.VALIDATION_LIMITS["MAX_RETRIES"]),
            description="Maximum retry attempts",
        )
        headers: dict[str, str] = Field(
            default_factory=dict,
            description="Default headers for all requests",
        )
        verify_ssl: bool = Field(default=True, description="Verify SSL certificates")

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
        """Pagination information model for HTTP operations (immutable value object)."""

        page: int = Field(
            default=1,
            ge=1,
            description="Current page number (1-based)",
        )
        page_size: int = Field(
            default=c.Pagination.DEFAULT_PAGE_SIZE,
            ge=c.Pagination.MIN_PAGE_SIZE,
            le=c.Pagination.MAX_PAGE_SIZE,
            description="Items per page",
        )
        total_items: int = Field(default=0, ge=0, description="Total number of items")
        total_pages: int = Field(default=0, ge=0, description="Total number of pages")

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
        """HTTP error response model (immutable value object)."""

        message: str = Field(..., description="Human-readable error message")
        error_code: str = Field(default="", description="Machine-readable error code")
        status_code: int = Field(
            default=500,
            ge=100,
            le=599,
            description="HTTP status code",
        )
        details: t.Api.JsonObject = Field(
            default_factory=dict,
            description="Additional error details",
        )
        request_id: str = Field(
            default="",
            description="Associated request ID for tracking",
        )

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
        """Query parameters model (immutable value object)."""

        params: t.Api.WebParams = Field(
            default_factory=dict,
            description="Query parameters",
        )

        def get_param(self, name: str) -> str | list[str]:
            """Get query parameter value."""
            if name in self.params:
                return self.params[name]
            return ""

        def with_param(self, name: str, value: str | list[str]) -> Self:
            """Return new instance with updated parameter (functional pattern)."""
            updated_params = {**self.params, name: value}
            return self.model_copy(update={"params": updated_params})

    class Headers(FlextModels.Value):
        """HTTP headers model (immutable value object)."""

        headers: dict[str, str] = Field(
            default_factory=dict,
            description="HTTP headers",
        )

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

            keys_to_remove = u.Collection.filter(
                list(self.headers.keys()),
                matches_header_key,
            )
            updated_headers = {
                k: v for k, v in self.headers.items() if k not in keys_to_remove
            }
            return self.model_copy(update={"headers": updated_headers})

    # =========================================================================
    # FACTORY METHODS - Model creation utilities
    # =========================================================================

    @classmethod
    def create_response(
        cls,
        status_code: int,
        body: t.Api.ResponseBody | None = None,
        headers: dict[str, str] | None = None,
        request_id: str | None = None,
    ) -> FlextApiModels.HttpResponse:
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
        response_headers: dict[str, str] = headers if headers is not None else {}
        response_id: str = request_id if request_id is not None else ""

        return cls.HttpResponse(
            status_code=status_code,
            body=response_body,
            headers=response_headers,
            request_id=response_id,
        )

    @classmethod
    def create_config(
        cls,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        headers: dict[str, str] | None = None,
        *,
        verify_ssl: bool = True,
    ) -> FlextApiModels.ClientConfig:
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
        config_base_url = base_url if base_url is not None else c.Api.DEFAULT_BASE_URL
        config_timeout = (
            float(timeout) if timeout is not None else float(c.Api.DEFAULT_TIMEOUT)
        )
        config_max_retries = (
            max_retries if max_retries is not None else c.Api.DEFAULT_MAX_RETRIES
        )
        config_headers: dict[str, str] = headers if headers is not None else {}

        return cls.ClientConfig(
            base_url=config_base_url,
            timeout=config_timeout,
            max_retries=config_max_retries,
            headers=config_headers,
            verify_ssl=verify_ssl,
        )

    class HttpPagination(FlextModels.Value):
        """HTTP pagination value object for list responses.

        Immutable pagination metadata for paginated API responses.
        """

        page: int = Field(default=1, ge=1, description="Current page number")
        page_size: int = Field(
            default=c.Pagination.DEFAULT_PAGE_SIZE,
            ge=c.Pagination.MIN_PAGE_SIZE,
            le=c.Pagination.MAX_PAGE_SIZE,
            description="Items per page",
        )
        total_items: int = Field(default=0, ge=0, description="Total number of items")
        total_pages: int = Field(default=0, ge=0, description="Total number of pages")

        @computed_field
        def offset(self) -> int:
            """Calculate offset from page and page_size."""
            return (self.page - 1) * self.page_size

        @computed_field
        def has_next(self) -> bool:
            """Check if next page exists."""
            if self.total_pages == 0:
                return False
            return self.page < self.total_pages

        @computed_field
        def has_previous(self) -> bool:
            """Check if previous page exists."""
            return self.page > 1

    # =========================================================================
    # STORAGE MODELS
    # =========================================================================

    class Storage:
        """Storage-related models namespace."""

        class Metadata(FlextModels.Value):
            """Internal metadata for stored values (using Pydantic for validation)."""

            value: t.GeneralValueType
            timestamp: str
            ttl: int | None = None
            created_at: float = Field(default_factory=time.time)

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


m = FlextApiModels  # Runtime alias (not TypeAlias to avoid PYI042)


__all__ = ["FlextApiModels", "m"]
