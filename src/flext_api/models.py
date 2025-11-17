"""FLEXT API Models - HTTP Domain Models extending flext-core.

Unified namespace class that extends flext-core FlextModels with HTTP-specific
domain entities. Provides Pydantic v2 models for HTTP operations following
Clean Architecture patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from urllib.parse import ParseResult, urlparse

from flext_core import FlextModels
from pydantic import BaseModel, Field, computed_field

from flext_api.constants import FlextApiConstants
from flext_api.typings import FlextApiTypes


class FlextApiModels:
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

        method: str = Field(
            default=FlextApiConstants.Method.GET,
            min_length=3,
            max_length=8,
            description="HTTP method (GET, POST, PUT, DELETE, PATCH, etc.)",
            pattern=r"^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|CONNECT|TRACE)$",
        )
        url: str = Field(..., min_length=1, max_length=2048, description="Request URL")
        headers: dict[str, str] = Field(
            default_factory=dict, description="HTTP request headers"
        )
        body: FlextApiTypes.RequestBody | None = Field(
            default=None, description="Request body"
        )
        query_params: FlextApiTypes.WebParams | None = Field(
            default=None, description="Query parameters"
        )
        timeout: float = Field(
            default=30.0, ge=0.1, le=300.0, description="Request timeout in seconds"
        )

        @computed_field
        def content_type(self) -> str | None:
            """Get content type from headers."""
            if "Content-Type" in self.headers:
                content_type_value = self.headers["Content-Type"]
                if isinstance(content_type_value, str):
                    return content_type_value
            if "content-type" in self.headers:
                content_type_value = self.headers["content-type"]
                if isinstance(content_type_value, str):
                    return content_type_value
            return None

    class HttpResponse(FlextModels.Value):
        """Immutable HTTP response value object.

        Represents a complete HTTP response with all returned data.
        Follows Value Object pattern: immutable, compared by value, no identity.
        """

        status_code: int = Field(
            ..., ge=100, le=599, description="HTTP status code (100-599)"
        )
        headers: dict[str, str] = Field(
            default_factory=dict, description="HTTP response headers"
        )
        body: FlextApiTypes.ResponseBody | None = Field(
            default=None, description="Response body"
        )
        request_id: str | None = Field(
            default=None, description="Associated request ID for tracking"
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
            ..., min_length=1, max_length=2048, description="Full URL string"
        )

        @computed_field
        def parsed(self) -> ParseResult:
            """Parse the URL."""
            return urlparse(self.url)

        @computed_field
        def scheme(self) -> str | None:
            """Get URL scheme (http, https, etc.)."""
            parsed_result = self.parsed
            parsed_scheme = parsed_result.scheme
            if parsed_scheme:
                return parsed_scheme
            return None

        @computed_field
        def netloc(self) -> str | None:
            """Get network location (host:port)."""
            parsed_netloc = self.parsed.netloc
            if parsed_netloc:
                return parsed_netloc
            return None

        @computed_field
        def path(self) -> str | None:
            """Get URL path."""
            parsed_path = self.parsed.path
            if parsed_path:
                return parsed_path
            return None

        @computed_field
        def query(self) -> str | None:
            """Get URL query string."""
            parsed_query = self.parsed.query
            if parsed_query:
                return parsed_query
            return None

        @computed_field
        def fragment(self) -> str | None:
            """Get URL fragment."""
            parsed_fragment = self.parsed.fragment
            if parsed_fragment:
                return parsed_fragment
            return None

        @computed_field
        def is_valid(self) -> bool:
            """Check if URL is valid."""
            scheme_value = self.scheme
            netloc_value = self.netloc
            return bool(scheme_value and netloc_value)

    # =========================================================================
    # CONFIGURATION MODELS
    # =========================================================================

    class ClientConfig(BaseModel):
        """HTTP client configuration model."""

        base_url: str = Field(
            default="", max_length=2048, description="Base URL for all requests"
        )
        timeout: float = Field(
            default=30.0, ge=0.1, le=300.0, description="Request timeout in seconds"
        )
        max_retries: int = Field(
            default=3, ge=0, le=10, description="Maximum retry attempts"
        )
        headers: dict[str, str] = Field(
            default_factory=dict, description="Default headers for all requests"
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

        page: int = Field(default=1, ge=1, description="Current page number (1-based)")
        page_size: int = Field(default=20, ge=1, le=1000, description="Items per page")
        total_items: int | None = Field(
            default=None, ge=0, description="Total number of items"
        )
        total_pages: int | None = Field(
            default=None, ge=0, description="Total number of pages"
        )

        @computed_field
        def has_next(self) -> bool:
            """Check if there are more pages."""
            if self.total_pages is None:
                return True
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
        error_code: str | None = Field(
            default=None, description="Machine-readable error code"
        )
        status_code: int = Field(
            default=500, ge=100, le=599, description="HTTP status code"
        )
        details: FlextApiTypes.JsonObject | None = Field(
            default=None, description="Additional error details"
        )
        request_id: str | None = Field(
            default=None, description="Associated request ID for tracking"
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
            default_factory=dict, description="Query parameters"
        )

        def get_param(self, name: str) -> str | list[str] | None:
            """Get query parameter value."""
            if name in self.params:
                return self.params[name]
            return None

        def set_param(self, name: str, value: str | list[str]) -> None:
            """Set query parameter value."""
            self.params[name] = value

    class Headers(BaseModel):
        """HTTP headers model."""

        headers: dict[str, str] = Field(
            default_factory=dict, description="HTTP headers"
        )

        def get_header(self, name: str) -> str | None:
            """Get header value (case-insensitive)."""
            name_lower = name.lower()
            for key, value in self.headers.items():
                if key.lower() == name_lower and isinstance(value, str):
                    return value
            return None

        def set_header(self, name: str, value: str) -> None:
            """Set header value."""
            self.headers[name] = value

        def remove_header(self, name: str) -> None:
            """Remove header by name (case-insensitive)."""
            keys_to_remove = [k for k in self.headers if k.lower() == name.lower()]
            for key in keys_to_remove:
                del self.headers[key]

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
        body: Response body (JSON, string, bytes, or None)
        headers: Response headers dictionary
        request_id: Associated request ID for tracking

        Returns:
        HttpResponse instance

        """
        # Use model defaults - no fallbacks
        response_headers: dict[str, str] = {}
        if headers is not None:
            response_headers = headers

        return cls.HttpResponse(
            status_code=status_code,
            body=body,
            headers=response_headers,
            request_id=request_id,
        )

    @classmethod
    def create_config(
        cls,
        base_url: str = "",
        timeout: float = 30.0,
        max_retries: int = 3,
        headers: dict[str, str] | None = None,
        verify_ssl: bool | None = None,
    ) -> FlextApiModels.ClientConfig:
        """Create ClientConfig from parameters.

        Args:
        base_url: Base URL for all requests
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
        headers: Default headers for all requests
        verify_ssl: Verify SSL certificates

        Returns:
        ClientConfig instance

        """
        # Use model defaults - no fallbacks
        config_headers: dict[str, str] = {}
        if headers is not None:
            config_headers = headers

        config_verify_ssl = True
        if verify_ssl is not None:
            config_verify_ssl = verify_ssl

        return cls.ClientConfig(
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            headers=config_headers,
            verify_ssl=config_verify_ssl,
        )

    class HttpPagination(FlextModels.Value):
        """HTTP pagination value object for list responses.

        Immutable pagination metadata for paginated API responses.
        """

        page: int = Field(default=1, ge=1, description="Current page number")
        page_size: int = Field(default=20, ge=1, le=1000, description="Items per page")
        total_items: int | None = Field(
            default=None, ge=0, description="Total number of items"
        )
        total_pages: int | None = Field(
            default=None, ge=0, description="Total number of pages"
        )

        @computed_field
        def offset(self) -> int:
            """Calculate offset from page and page_size."""
            return (self.page - 1) * self.page_size

        @computed_field
        def has_next(self) -> bool:
            """Check if next page exists."""
            if self.total_pages is None:
                return False
            return self.page < self.total_pages

        @computed_field
        def has_previous(self) -> bool:
            """Check if previous page exists."""
            return self.page > 1


__all__ = ["FlextApiModels"]
