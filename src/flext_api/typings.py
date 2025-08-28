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
    """Main API types class inheriting from FlextTypes with API-specific extensions.

    This is the SINGLE consolidated types class following FLEXT patterns.
    All API types are defined here with proper hierarchical organization.
    """

    # =============================================================================
    # API-SPECIFIC TYPE HIERARCHIES
    # =============================================================================

    class HTTP:
        """HTTP and REST API specific types."""

        # Type aliases using Python 3.13+ syntax
        type Method = str  # GET, POST, PUT, DELETE, etc.
        type Endpoint = str  # /api/v1/resource
        type StatusCode = int  # 200, 404, 500, etc.
        type ContentType = str  # application/json, text/html
        type Url = str  # Valid HTTP/HTTPS URL

        # Header and request types
        type Headers = dict[str, str]
        type QueryParams = dict[str, str | int | float | bool]
        type PathParams = dict[str, str]

        # Authentication types
        type AuthToken = str
        type APIKey = str
        type BearerToken = str

    class Api:
        """Core API types for requests/responses."""

        type Config = dict[str, object]
        type Result = dict[str, object]
        type ValidationResult = FlextResult[bool]
        type ServiceResponse = FlextResult[dict[str, object]]

    class Plugin:
        """Plugin system types."""

        type Config = dict[str, object]
        type MiddlewareChain = list[object]
        type CacheKey = str
        type CacheTtl = int  # Seconds

    class Builder:
        """Builder pattern types."""

        type QueryFilter = dict[str, object]
        type SortOrder = str  # "asc" | "desc"
        type PageSize = int
        type PageNumber = int

    class Validation:
        """API validation and error types."""

        type ErrorCode = str
        type ErrorMessage = str
        type ErrorDetails = CoreFlextTypes.Core.JsonDict
        type ValidationErrors = dict[str, list[str]]
        type FieldError = dict[str, str]


# Backward compatibility type aliases (temporary during migration)
ConfigDict = dict[str, object]
ResultDict = dict[str, object]
HeadersDict = dict[str, str]
QueryParams = dict[str, str | int | float | bool]
ValidationResult = FlextResult[bool]
ServiceResponse = FlextResult[dict[str, object]]
HttpMethod = str
HttpStatusCode = int
HttpUrl = str
ContentType = str
PluginConfig = dict[str, object]
MiddlewareChain = list[object]
CacheKey = str
CacheTtl = int
QueryFilter = dict[str, object]
SortOrder = str
PageSize = int
PageNumber = int

__all__ = [
    # Backward compatibility aliases (sorted)
    "CacheKey",
    "CacheTtl",
    "ConfigDict",
    "ContentType",
    # Main consolidated types class (first)
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
