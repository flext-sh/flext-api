"""FLEXT API Types - Domain-specific API type definitions.

This module provides API-specific type definitions extending FlextTypes.
Follows FLEXT standards:
- Domain-specific complex types only
- No simple aliases to primitive types
- Python 3.13+ syntax
- Extends FlextTypes properly

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Literal

from flext_core import FlextTypes

# =============================================================================
# API-SPECIFIC TYPE VARIABLES - Domain-specific TypeVars for API operations
# =============================================================================


# API domain TypeVars
class FlextApiTypes(FlextTypes):
    """API-specific type definitions extending FlextTypes.

    Domain-specific type system for HTTP/API operations.
    Contains ONLY complex API-specific types, no simple aliases.
    Uses Python 3.13+ type syntax and patterns.
    """

    # =========================================================================
    # COMMON API TYPES - Frequently used API types
    # =========================================================================

    # Common HTTP types referenced throughout the codebase
    type Headers = dict[str, str | list[str]]
    type RequestBody = dict[str, FlextTypes.Core.JsonValue] | str | bytes
    type Timeout = int | float

    # HTTP-specific type aliases
    type HttpStatusCode = int
    type JsonObject = dict[str, FlextTypes.Core.JsonValue]
    type HttpData = str | bytes | dict[str, FlextTypes.Core.JsonValue]
    type HttpHeaders = dict[str, str | list[str]]
    type HttpMethod = str  # GET, POST, PUT, DELETE, etc.
    type HttpParams = dict[str, str | list[str]]
    type RequestData = dict[str, FlextTypes.Core.JsonValue] | str | bytes
    type ResponseData = dict[str, FlextTypes.Core.JsonValue] | str | bytes
    type StorageKey = str
    type StorageValue = FlextTypes.Core.JsonValue
    type TimeoutSeconds = int | float

    # =========================================================================
    # HTTP REQUEST TYPES - Complex request handling types
    # =========================================================================

    class Request:
        """HTTP request complex types."""

        type RequestConfiguration = dict[
            str, str | int | bool | list[str] | dict[str, object]
        ]
        type RequestHeaders = dict[str, str | list[str]]
        type RequestParameters = dict[
            str, FlextTypes.Core.JsonValue | list[FlextTypes.Core.JsonValue]
        ]
        type RequestBody = dict[str, FlextTypes.Core.JsonValue] | str | bytes
        type RequestMiddleware = list[dict[str, FlextTypes.Core.JsonValue]]
        type RequestValidation = dict[str, list[str] | dict[str, object]]

    # =========================================================================
    # HTTP RESPONSE TYPES - Complex response handling types
    # =========================================================================

    class Response:
        """HTTP response complex types."""

        type ResponseConfiguration = dict[
            str, FlextTypes.Core.JsonValue | dict[str, object]
        ]
        type ResponseHeaders = dict[str, str | list[str]]
        type ResponseBody = dict[str, FlextTypes.Core.JsonValue] | str | bytes
        type ResponseMetadata = dict[str, int | float | str | dict[str, object]]
        type ResponseTransformation = list[dict[str, FlextTypes.Core.JsonValue]]
        type ResponseValidation = dict[str, bool | str | list[str]]

    # =========================================================================
    # API ENDPOINT TYPES - Complex endpoint management types
    # =========================================================================

    class Endpoint:
        """API endpoint complex types."""

        type EndpointConfiguration = dict[
            str, FlextTypes.Core.JsonValue | list[str] | dict[str, object]
        ]
        type EndpointMetadata = dict[
            str, str | int | list[str] | dict[str, FlextTypes.Core.JsonValue]
        ]
        type EndpointValidation = dict[str, list[str] | dict[str, object] | bool]
        type EndpointMiddleware = list[dict[str, FlextTypes.Core.JsonValue | object]]
        type EndpointDocumentation = dict[
            str, str | dict[str, FlextTypes.Core.JsonValue]
        ]
        type RouteConfiguration = dict[
            str, str | list[str] | dict[str, FlextTypes.Core.JsonValue]
        ]

    # =========================================================================
    # API AUTHENTICATION TYPES - Complex authentication types
    # =========================================================================

    class Authentication:
        """API authentication complex types."""

        type AuthConfiguration = dict[
            str, FlextTypes.Core.ConfigValue | dict[str, object]
        ]
        type AuthCredentials = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        type AuthTokenData = dict[str, FlextTypes.Core.JsonValue | int | bool]
        type AuthProviderConfig = dict[str, FlextTypes.Core.ConfigDict]
        type AuthMiddleware = list[dict[str, FlextTypes.Core.JsonValue]]
        type SecurityConfiguration = dict[
            str, bool | str | list[str] | dict[str, object]
        ]

    # =========================================================================
    # API CLIENT TYPES - Complex HTTP client types
    # =========================================================================

    class Client:
        """HTTP client complex types."""

        type ClientConfiguration = dict[
            str, FlextTypes.Core.ConfigValue | dict[str, object]
        ]
        type ConnectionPool = dict[str, int | bool | dict[str, object]]
        type RetryConfiguration = dict[str, int | float | list[str] | bool]
        type TimeoutConfiguration = dict[str, int | float | dict[str, object]]
        type ClientMiddleware = list[dict[str, FlextTypes.Core.JsonValue]]
        type SessionManagement = dict[
            str, FlextTypes.Core.JsonValue | dict[str, object]
        ]

    # =========================================================================
    # API PROJECT TYPES - Domain-specific project types extending FlextTypes
    # =========================================================================

    class Project(FlextTypes.Project):
        """API-specific project types extending FlextTypes.Project.

        Adds API-specific project types while inheriting generic types from FlextTypes.
        Follows domain separation principle: API domain owns API-specific types.
        """

        # API-specific project types extending the generic ones
        type ProjectType = Literal[
            # Generic types inherited from FlextTypes.Project
            "library",
            "application",
            "service",
            # API-specific types
            "rest-api",
            "graphql-api",
            "microservice-api",
            "webhook-api",
            "api-gateway",
            "api-client",
            "api-server",
            "api-wrapper",
            "sdk",
            "client-library",
            "http-service",
            "json-api",
        ]

        # API-specific project configurations
        type ApiProjectConfig = dict[str, FlextTypes.Core.ConfigValue | object]
        type RestApiConfig = dict[str, str | int | bool | list[str]]
        type GraphqlApiConfig = dict[str, bool | str | dict[str, object]]
        type MicroserviceConfig = dict[str, FlextTypes.Core.ConfigValue | object]


# =============================================================================
# PUBLIC API EXPORTS - API types and classes
# =============================================================================

__all__: list[str] = [
    "FlextApiTypes",
]
