"""Centralized typings facade for flext-api.

- Extends flext-core types
- Add API-specific type aliases and Protocols here
- Python 3.13+ type patterns
"""

from __future__ import annotations

from flext_core import FlextResult, FlextTypes as CoreFlextTypes

# =============================================================================
# PYTHON 3.13+ TYPE ALIASES - Modern type system patterns
# =============================================================================

# API-specific type aliases using Python 3.13+ syntax
type ConfigDict = dict[str, object]  # Not dict[str, Any] - be specific
type ResultDict = dict[str, object]
type HeadersDict = dict[str, str]
type QueryParams = dict[str, str | int | float | bool]
type ValidationResult = FlextResult[bool]
type ServiceResponse = FlextResult[dict[str, object]]

# HTTP-specific type aliases
type HttpMethod = str  # "GET" | "POST" | "PUT" | "DELETE" | "PATCH"
type HttpStatusCode = int  # 200, 404, 500, etc.
type HttpUrl = str  # Valid HTTP/HTTPS URL
type ContentType = str  # "application/json", "text/html", etc.

# Plugin and middleware type aliases
type PluginConfig = dict[str, object]
type MiddlewareChain = list[object]  # Will be typed more specifically later
type CacheKey = str
type CacheTtl = int  # Seconds

# Builder pattern type aliases
type QueryFilter = dict[str, object]
type SortOrder = str  # "asc" | "desc"
type PageSize = int
type PageNumber = int

# =============================================================================
# FLEXT API TYPES EXTENSION
# =============================================================================


class FlextTypes(CoreFlextTypes):
    """API domain-specific types extending flext-core patterns."""

    # Inherit all Core types and add API-specific ones
    class Api:
        """API-specific type definitions."""

        Config = ConfigDict
        Result = ResultDict
        Headers = HeadersDict
        QueryParams = QueryParams
        ValidationResult = ValidationResult
        ServiceResponse = ServiceResponse

        HttpMethod = HttpMethod
        HttpStatusCode = HttpStatusCode
        HttpUrl = HttpUrl
        ContentType = ContentType

        PluginConfig = PluginConfig
        MiddlewareChain = MiddlewareChain
        CacheKey = CacheKey
        CacheTtl = CacheTtl

        QueryFilter = QueryFilter
        SortOrder = SortOrder
        PageSize = PageSize
        PageNumber = PageNumber


__all__ = [
    "CacheKey",
    "CacheTtl",
    "ConfigDict",
    "ContentType",
    "FlextTypes",
    "HeadersDict",
    "HttpMethod",
    "HttpStatusCode",
    "HttpUrl",
    "MiddlewareChain",
    "PageNumber",
    "PageSize",
    "PluginConfig",
    "QueryFilter",
    "QueryParams",
    "ResultDict",
    "ServiceResponse",
    "SortOrder",
    "ValidationResult",
]
