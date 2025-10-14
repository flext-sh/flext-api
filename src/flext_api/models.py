"""FLEXT API Models - Data models only (constants/types come from constants & typings).

Remove duplicates: use directly `FlextApiConstants` and `FlextApiTypes` instead of
classes internal constants/field/endpoints/status. This module now exposes
only models (Request/Response/Config/Query/Storage/URL) following flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from urllib.parse import ParseResult, urlparse

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class FlextApiModels:
    """Flext API models - Pydantic models only.

    Contains all API-specific Pydantic models as nested classes.
    Uses FlextCore patterns and types.
    """

    class HttpRequest(BaseModel):
        """HTTP request model."""

        method: str = Field(..., description="HTTP method")
        url: str = Field(..., description="Request URL")
        headers: dict[str, str] = Field(
            default_factory=dict, description="Request headers"
        )
        body: bytes | None = Field(default=None, description="Request body")
        timeout: int = Field(default=30, description="Request timeout")

    class HttpResponse(BaseModel):
        """HTTP response model."""

        status_code: int = Field(..., description="HTTP status code")
        headers: dict[str, str] = Field(
            default_factory=dict, description="Response headers"
        )
        body: bytes | None = Field(default=None, description="Response body")
        content_type: str | None = Field(default=None, description="Content type")

    class ClientConfig(BaseModel):
        """Client configuration model."""

        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
        )

        base_url: str = Field(..., description="Base URL for API calls")
        timeout: int = Field(default=30, ge=1, description="Default timeout")
        headers: dict[str, str] = Field(
            default_factory=dict, description="Default headers"
        )

    class HttpQuery(BaseModel):
        """HTTP query parameters model."""

        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
        )

        filter_conditions: dict[str, str] = Field(
            default_factory=dict, description="Filter conditions"
        )
        sort_fields: list[str] = Field(default_factory=list, description="Sort fields")
        page_number: int = Field(default=1, ge=1, description="Page number")
        page_size: int = Field(default=20, ge=1, le=100, description="Page size")

        def to_query_params(self) -> dict[str, object]:
            """Convert to query parameters dict."""
            return {
                "filters": self.filter_conditions,
                "sort": self.sort_fields,
                "page": self.page_number,
                "size": self.page_size,
            }

    class UrlModel(BaseModel):
        """URL model for validation and parsing."""

        url: str = Field(..., description="Full URL string")

        @property
        def parsed_url(self) -> ParseResult:
            """Parse the URL."""
            return urlparse(self.url)

        @property
        def scheme(self) -> str:
            """Get URL scheme."""
            return self.parsed_url.scheme

        @property
        def netloc(self) -> str:
            """Get network location."""
            return self.parsed_url.netloc

        @property
        def path(self) -> str:
            """Get URL path."""
            return self.parsed_url.path

        @property
        def query(self) -> str:
            """Get URL query."""
            return self.parsed_url.query

        @property
        def fragment(self) -> str:
            """Get URL fragment."""
            return self.parsed_url.fragment


__all__ = [
    "FlextApiModels",
]
