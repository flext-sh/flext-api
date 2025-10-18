"""FLEXT API Models - Domain-agnostic HTTP models.

Generic Pydantic models for HTTP operations following flext-core patterns.
Completely domain-agnostic and reusable across any HTTP application.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Any
from urllib.parse import ParseResult, urlparse

from pydantic import BaseModel, Field


class FlextApiModels:
    """Generic FLEXT API models with Pydantic validation.

    Domain-agnostic API models following flext-core patterns.
    Uses advanced Pydantic patterns for validation and type safety.
    """

    class UrlModel(BaseModel):
        """Generic URL model for validation and parsing."""

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

    class HttpResponse(BaseModel):
        """Generic HTTP response model with Pydantic validation."""

        status_code: int = Field(..., ge=100, le=599, description="HTTP status code")
        headers: dict[str, Any] = Field(default_factory=dict, description="Response headers")
        body: Any | None = Field(default=None, description="Response body")
        content_type: str | None = Field(default=None, description="Content type")

    class HttpRequest(BaseModel):
        """Generic HTTP request model with Pydantic validation."""

        method: str = Field(..., min_length=3, max_length=8, description="HTTP method")
        url: str = Field(..., description="Request URL")
        headers: dict[str, Any] = Field(default_factory=dict, description="Request headers")
        body: Any | None = Field(default=None, description="Request body")
        timeout: float = Field(default=30.0, ge=0.1, le=300.0, description="Request timeout")

    class HttpQuery(BaseModel):
        """Generic HTTP query parameters model with Pydantic validation."""

        filter_conditions: dict[str, Any] = Field(default_factory=dict, description="Filter conditions")
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

    class ClientConfig(BaseModel):
        """Generic client configuration model with Pydantic validation."""

        base_url: str = Field(..., description="Base URL for HTTP requests")
        timeout: float = Field(default=30.0, ge=0.1, le=300.0, description="Request timeout")
        headers: dict[str, Any] = Field(default_factory=dict, description="Default HTTP headers")


__all__ = ["FlextApiModels"]
