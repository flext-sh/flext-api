"""FLEXT API Types - Project-Specific Type Extensions.

Extends the standardized flext-core type system with API-specific types
while maintaining compatibility with the ecosystem-wide type standards.

Architecture:
    Foundation Layer (flext-core) → Project Layer (flext-api) → Application Layer

Design Patterns:
    - Inherit from FlextTypes.Core for base patterns
    - Extend with API-specific domain types
    - Maintain backward compatibility during migration
    - Use semantic prefixes for logical grouping

Usage:
    from flext_api.types import APITypes

    # Project-specific types
    endpoint: APITypes.HTTP.Endpoint = "/api/v1/users"
    response: APITypes.HTTP.Response[User] = create_response(user)

    # Core ecosystem types still available
    result: FlextTypes.Core.Result[User] = FlextResult.ok(user)

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Generic, TypeVar

from flext_core.semantic_types import FlextTypes

# =============================================================================
# PROJECT TYPE VARIABLES
# =============================================================================

T_Response = TypeVar("T_Response")
T_Request = TypeVar("T_Request")
T_Payload = TypeVar("T_Payload")

# Legacy compatibility
TData = TypeVar("TData")

# =============================================================================
# API-SPECIFIC TYPE SYSTEM
# =============================================================================


class APITypes:
    """API-specific type system extending flext-core foundation."""

    # Import core types for convenience
    Core = FlextTypes.Core

    class HTTP:
        """HTTP and REST API specific types."""

        # HTTP method and endpoint types
        type Method = str  # GET, POST, PUT, DELETE, etc.
        type Endpoint = str  # /api/v1/resource
        type StatusCode = int  # 200, 404, 500, etc.
        type ContentType = str  # application/json, text/html

        # Request/Response types with generics
        class Request(Generic[T_Request]):
            """Generic HTTP request type."""

        class Response(Generic[T_Response]):
            """Generic HTTP response type."""

        # Header and query types
        type Headers = dict[str, str]
        type QueryParams = dict[str, str | list[str]]
        type PathParams = dict[str, str]

        # Authentication types
        type AuthToken = str
        type APIKey = str
        type BearerToken = str

    class Validation:
        """API validation and error types."""

        # Error response types
        type ErrorCode = str
        type ErrorMessage = str
        type ErrorDetails = FlextTypes.Core.JsonDict

        # Validation types
        type ValidationErrors = dict[str, list[str]]
        type FieldError = dict[str, str]

    class Serialization:
        """Data serialization types."""

        # JSON types
        type JSONData = FlextTypes.Core.JsonDict
        type JSONArray = list[object]
        type JSONString = str

        # Schema types
        type SchemaVersion = str
        type SchemaDefinition = FlextTypes.Core.JsonDict


# =============================================================================
# COMPATIBILITY LAYER
# =============================================================================


class APITypesCompat:
    """Compatibility aliases for migration from old API type patterns."""

    # Legacy HTTP aliases
    HTTPMethod = APITypes.HTTP.Method
    HTTPEndpoint = APITypes.HTTP.Endpoint
    HTTPStatusCode = APITypes.HTTP.StatusCode
    HTTPHeaders = APITypes.HTTP.Headers

    # Legacy response aliases
    APIResponse = APITypes.HTTP.Response
    APIRequest = APITypes.HTTP.Request

    # Legacy validation aliases
    ValidationError = APITypes.Validation.ValidationErrors


# =============================================================================
# MIGRATION HELPERS
# =============================================================================


def get_api_types() -> FlextTypes.Core.JsonDict:
    """Get all API-specific type definitions.

    Returns:
        Dictionary of API type names mapped to their type definitions

    """
    return {
        "Method": APITypes.HTTP.Method,
        "Endpoint": APITypes.HTTP.Endpoint,
        "StatusCode": APITypes.HTTP.StatusCode,
        "Request": APITypes.HTTP.Request,
        "Response": APITypes.HTTP.Response,
        "Headers": APITypes.HTTP.Headers,
        "QueryParams": APITypes.HTTP.QueryParams,
        "ValidationErrors": APITypes.Validation.ValidationErrors,
        "JSONData": APITypes.Serialization.JSONData,
    }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "APITypes",
    "APITypesCompat",
    "TData",  # Legacy compatibility
    "T_Payload",
    "T_Request",
    "T_Response",
    "get_api_types",
]
