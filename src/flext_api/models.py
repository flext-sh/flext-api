"""FLEXT API Models - HTTP Domain Models extending flext-core.

Unified namespace class that extends flext-core FlextModels with HTTP-specific
domain entities. Provides Pydantic v2 models for HTTP operations following
Clean Architecture patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import cast
from urllib.parse import ParseResult, urlparse

from flext_core import FlextModels, u
from flext_core.models import FlextModels as FlextModelsBase
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from flext_api.constants import FlextApiConstants
from flext_api.typings import FlextApiTypes


class FlextApiBaseModel(BaseModel):
    """Base model for FlextApi with standard Pydantic v2 configuration."""

    model_config = ConfigDict(
        use_enum_values=True,
        validate_default=True,
        str_strip_whitespace=True,
        extra="forbid",
    )


class FlextApiModels(FlextModelsBase):
    """HTTP domain models for flext-api.

    Unified namespace class that aggregates all HTTP-specific domain models.
    Uses nested classes following SOLID principles for maximum maintainability.
    Provides Pydantic v2 value objects and entities for HTTP operations.

    Fully compatible with Pydantic v2 with strict type safety and validation.
    """

    # =========================================================================
    # HTTP REQUEST/RESPONSE VALUE OBJECTS (Immutable)
    # =========================================================================

    class HttpRequest(FlextModels.Value):
        """Immutable HTTP request value object.

        Represents a complete HTTP request with all necessary parameters.
        Follows Value Object pattern: immutable, compared by value, no identity.
        """

        method: FlextApiConstants.Method | str = Field(
            default=FlextApiConstants.Method.GET,
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
        body: FlextApiTypes.RequestBody = Field(
            default_factory=dict,
            description="Request body",
        )

        @field_validator("body", mode="before")
        @classmethod
        def normalize_body(cls, v: object) -> FlextApiTypes.RequestBody:
            """Normalize body - empty dict is valid."""
            if v is None:
                return {}
            if isinstance(v, dict):
                return v
            if isinstance(v, (str, bytes)):
                return v
            return {}

        query_params: FlextApiTypes.WebParams = Field(
            default_factory=dict,
            description="Query parameters",
        )
        timeout: float = Field(
            default=float(FlextApiConstants.DEFAULT_TIMEOUT),
            ge=float(FlextApiConstants.VALIDATION_LIMITS["MIN_TIMEOUT"]),
            le=float(FlextApiConstants.VALIDATION_LIMITS["MAX_TIMEOUT"]),
            description="Request timeout in seconds",
        )

        @computed_field
        def content_type(self) -> str:
            """Get content type from headers."""
            # Check Content-Type header (case-insensitive)
            header_content_type = FlextApiConstants.HEADER_CONTENT_TYPE
            if header_content_type in self.headers:
                content_type_value = self.headers[header_content_type]
                if isinstance(content_type_value, str):
                    return content_type_value
            # Check lowercase variant
            header_lower = header_content_type.lower()
            if header_lower in self.headers:
                content_type_value = self.headers[header_lower]
                if isinstance(content_type_value, str):
                    return content_type_value
            # Default from Constants
            return FlextApiConstants.ContentType.JSON

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
        body: FlextApiTypes.ResponseBody = Field(
            default_factory=dict,
            description="Response body (empty dict by default, None allowed for 204)",
        )

        @field_validator("body", mode="before")
        @classmethod
        def normalize_body(cls, v: object) -> FlextApiTypes.ResponseBody:
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
            return (
                FlextApiConstants.HTTP_SUCCESS_MIN
                <= self.status_code
                < FlextApiConstants.HTTP_SUCCESS_MAX
            )

        @computed_field
        def is_redirect(self) -> bool:
            """Check if response indicates redirect (3xx status code)."""
            return (
                FlextApiConstants.HTTP_REDIRECT_MIN
                <= self.status_code
                < FlextApiConstants.HTTP_REDIRECT_MAX
            )

        @computed_field
        def is_client_error(self) -> bool:
            """Check if response indicates client error (4xx status code)."""
            return (
                FlextApiConstants.HTTP_CLIENT_ERROR_MIN
                <= self.status_code
                < FlextApiConstants.HTTP_CLIENT_ERROR_MAX
            )

        @computed_field
        def is_server_error(self) -> bool:
            """Check if response indicates server error (5xx status code)."""
            return self.status_code >= FlextApiConstants.HTTP_SERVER_ERROR_MIN

        @computed_field
        def is_error(self) -> bool:
            """Check if response indicates any error (4xx or 5xx status code)."""
            return self.status_code >= FlextApiConstants.HTTP_ERROR_MIN

    # =========================================================================
    # URL AND PARSING MODELS
    # =========================================================================

    class Url(BaseModel):
        """URL parsing and validation model."""

        url: str = Field(
            ...,
            min_length=1,
            max_length=2048,
            description="Full URL string",
        )

        @computed_field
        def parsed(self) -> ParseResult:
            """Parse the URL."""
            return urlparse(self.url)

        @computed_field
        def scheme(self) -> str:
            """Get URL scheme (http, https, etc.)."""
            parsed_result = urlparse(self.url)
            parsed_scheme = parsed_result.scheme
            if parsed_scheme:
                return parsed_scheme
            return FlextApiConstants.HTTP.Protocol.HTTPS

        @computed_field
        def netloc(self) -> str:
            """Get network location (host:port)."""
            parsed_result = urlparse(self.url)
            parsed_netloc = parsed_result.netloc
            if parsed_netloc:
                return parsed_netloc
            return f"{FlextApiConstants.Server.DEFAULT_HOST}:{FlextApiConstants.Server.DEFAULT_PORT}"

        @computed_field
        def path(self) -> str:
            """Get URL path."""
            parsed_result = urlparse(self.url)
            parsed_path = parsed_result.path
            if parsed_path:
                return parsed_path
            return "/"

        @computed_field
        def query(self) -> str:
            """Get URL query string."""
            parsed_result = urlparse(self.url)
            parsed_query = parsed_result.query
            if parsed_query:
                return parsed_query
            return ""

        @computed_field
        def fragment(self) -> str:
            """Get URL fragment."""
            parsed_result = urlparse(self.url)
            parsed_fragment = parsed_result.fragment
            if parsed_fragment:
                return parsed_fragment
            return ""

        @computed_field
        def is_valid(self) -> bool:
            """Check if URL is valid."""
            parsed_result = urlparse(self.url)
            scheme_value = parsed_result.scheme
            netloc_value = parsed_result.netloc
            return bool(scheme_value and netloc_value)

    # =========================================================================
    # CONFIGURATION MODELS
    # =========================================================================

    class ClientConfig(BaseModel):
        """HTTP client configuration model."""

        base_url: str = Field(
            default=FlextApiConstants.DEFAULT_BASE_URL,
            max_length=FlextApiConstants.MAX_URL_LENGTH,
            description="Base URL for all requests",
        )
        timeout: float = Field(
            default=float(FlextApiConstants.DEFAULT_TIMEOUT),
            ge=float(FlextApiConstants.VALIDATION_LIMITS["MIN_TIMEOUT"]),
            le=float(FlextApiConstants.VALIDATION_LIMITS["MAX_TIMEOUT"]),
            description="Request timeout in seconds",
        )
        max_retries: int = Field(
            default=FlextApiConstants.DEFAULT_MAX_RETRIES,
            ge=int(FlextApiConstants.VALIDATION_LIMITS["MIN_RETRIES"]),
            le=int(FlextApiConstants.VALIDATION_LIMITS["MAX_RETRIES"]),
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

    class Pagination(BaseModel):
        """Pagination information model."""

        page: int = Field(
            default=1,
            ge=1,
            description="Current page number (1-based)",
        )
        page_size: int = Field(
            default=FlextApiConstants.DEFAULT_PAGE_SIZE,
            ge=FlextApiConstants.MIN_PAGE_SIZE,
            le=FlextApiConstants.MAX_PAGE_SIZE,
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

    class Error(BaseModel):
        """HTTP error response model."""

        message: str = Field(..., description="Human-readable error message")
        error_code: str = Field(default="", description="Machine-readable error code")
        status_code: int = Field(
            default=500,
            ge=100,
            le=599,
            description="HTTP status code",
        )
        details: FlextApiTypes.JsonObject = Field(
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
                FlextApiConstants.HTTP_CLIENT_ERROR_MIN
                <= self.status_code
                < FlextApiConstants.HTTP_CLIENT_ERROR_MAX
            )

        @computed_field
        def is_server_error(self) -> bool:
            """Check if error is server-side (5xx)."""
            return self.status_code >= FlextApiConstants.HTTP_SERVER_ERROR_MIN

    # =========================================================================
    # QUERY/FILTER MODELS
    # =========================================================================

    class QueryParams(BaseModel):
        """Query parameters model."""

        params: FlextApiTypes.WebParams = Field(
            default_factory=dict,
            description="Query parameters",
        )

        def get_param(self, name: str) -> str | list[str]:
            """Get query parameter value."""
            if name in self.params:
                param_value = self.params[name]
                if isinstance(param_value, (str, list)):
                    return param_value
            return ""

        def set_param(self, name: str, value: str | list[str]) -> None:
            """Set query parameter value."""
            self.params[name] = value

    class Headers(BaseModel):
        """HTTP headers model."""

        headers: dict[str, str] = Field(
            default_factory=dict,
            description="HTTP headers",
        )

        def get_header(self, name: str) -> str:
            """Get header value (case-insensitive)."""
            name_lower = name.lower()
            for key, value in self.headers.items():
                if key.lower() == name_lower and isinstance(value, str):
                    return value
            return ""

        def set_header(self, name: str, value: str) -> None:
            """Set header value."""
            self.headers[name] = value

        def remove_header(self, name: str) -> None:
            """Remove header by name (case-insensitive)."""
            # Use u.filter() for unified filtering (DSL pattern)
            keys_to_remove = cast(
                "list[str]",
                u.Collection.filter(
                    list(self.headers.keys()), lambda k: k.lower() == name.lower()
                ),
            )
            u.Collection.process(
                keys_to_remove,
                processor=lambda key: self.headers.pop(key, None),
                on_error="skip",
            )

    # =========================================================================
    # FACTORY METHODS - Model creation utilities
    # =========================================================================

    @classmethod
    def create_response(
        cls,
        status_code: int,
        body: FlextApiTypes.ResponseBody | None = None,
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
        response_body: FlextApiTypes.ResponseBody = body if body is not None else {}
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
        config_base_url = (
            base_url if base_url is not None else FlextApiConstants.DEFAULT_BASE_URL
        )
        config_timeout = (
            float(timeout)
            if timeout is not None
            else float(FlextApiConstants.DEFAULT_TIMEOUT)
        )
        config_max_retries = (
            max_retries
            if max_retries is not None
            else FlextApiConstants.DEFAULT_MAX_RETRIES
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
            default=FlextApiConstants.DEFAULT_PAGE_SIZE,
            ge=FlextApiConstants.MIN_PAGE_SIZE,
            le=FlextApiConstants.MAX_PAGE_SIZE,
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


m = FlextApiModels  # Runtime alias (not TypeAlias to avoid PYI042)

__all__ = ["FlextApiBaseModel", "FlextApiModels", "m"]
