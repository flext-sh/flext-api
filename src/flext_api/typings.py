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
    Headers = dict[str, str]
    RequestBody = dict[str, FlextTypes.Core.JsonValue] | str | bytes
    Timeout = int | float

    # HTTP-specific type aliases
    HttpStatusCode = int
    JsonObject = dict[str, FlextTypes.Core.JsonValue]
    HttpData = str | bytes | dict[str, FlextTypes.Core.JsonValue]
    HttpHeaders = dict[str, str | list[str]]
    HttpMethod = str  # GET, POST, PUT, DELETE, etc.
    HttpParams = dict[str, str | list[str]]
    RequestData = dict[str, FlextTypes.Core.JsonValue] | str | bytes
    ResponseData = dict[str, FlextTypes.Core.JsonValue] | str | bytes
    StorageKey = str
    StorageValue = FlextTypes.Core.JsonValue
    TimeoutSeconds = int | float
    # =========================================================================
    # CORE API TYPES - Commonly used API type aliases extending FlextTypes.Core
    # =========================================================================

    class Core(FlextTypes.Core):
        """Core API types extending FlextTypes.Core."""

        # Configuration and settings types
        ConfigDict = dict[str, FlextTypes.Core.ConfigValue | dict[str, object]]
        ConnectionDict = dict[str, object]
        ClientConfigDict = dict[str, object]
        RequestConfigDict = dict[str, object]
        ResponseDict = dict[str, object]
        MetricsDict = dict[str, object]
        CacheDict = dict[str, object]
        RetryInfoDict = dict[str, object]
        StorageDict = dict[str, object]
        UtilityDict = dict[str, object]

        # HTTP operation types
        HttpRequestDict = dict[str, object]
        HttpResponseDict = dict[str, object]
        ApiSetupDict = dict[str, object]
        EndpointDict = dict[str, object]

        # Template and structured response types
        ResponseTemplateDict = dict[str, str | dict[str, object]]
        ErrorTemplateDict = dict[str, str | dict[str, object]]

        # Model and data types
        FilterConditionsDict = dict[str, object]
        QueryParamsDict = dict[str, object]
        RequestKwargsDict = dict[str, object]
        ContextDict = dict[str, object]
        DetailsDict = dict[str, object]
        ResponseList = list[dict[str, object]]

    # =========================================================================
    # HTTP REQUEST TYPES - Complex request handling types
    # =========================================================================

    class Request:
        """HTTP request complex types."""

        RequestConfiguration = dict[
            str, str | int | bool | list[str] | dict[str, object]
        ]
        RequestHeaders = dict[str, str | list[str]]
        RequestParameters = dict[
            str, FlextTypes.Core.JsonValue | list[FlextTypes.Core.JsonValue]
        ]
        RequestBody = dict[str, FlextTypes.Core.JsonValue] | str | bytes
        RequestMiddleware = list[dict[str, FlextTypes.Core.JsonValue]]
        RequestValidation = dict[str, list[str] | dict[str, object]]

    # =========================================================================
    # HTTP RESPONSE TYPES - Complex response handling types
    # =========================================================================

    class Response:
        """HTTP response complex types."""

        ResponseConfiguration = dict[str, FlextTypes.Core.JsonValue | dict[str, object]]
        ResponseHeaders = dict[str, str | list[str]]
        ResponseBody = dict[str, FlextTypes.Core.JsonValue] | str | bytes
        ResponseMetadata = dict[str, int | float | str | dict[str, object]]
        ResponseTransformation = list[dict[str, FlextTypes.Core.JsonValue]]
        ResponseValidation = dict[str, bool | str | list[str]]

    # =========================================================================
    # API ENDPOINT TYPES - Complex endpoint management types
    # =========================================================================

    class Endpoint:
        """API endpoint complex types."""

        EndpointConfiguration = dict[
            str, FlextTypes.Core.JsonValue | list[str] | dict[str, object]
        ]
        EndpointMetadata = dict[
            str, str | int | list[str] | dict[str, FlextTypes.Core.JsonValue]
        ]
        EndpointValidation = dict[str, list[str] | dict[str, object] | bool]
        EndpointMiddleware = list[dict[str, FlextTypes.Core.JsonValue | object]]
        EndpointDocumentation = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        RouteConfiguration = dict[
            str, str | list[str] | dict[str, FlextTypes.Core.JsonValue]
        ]

    # =========================================================================
    # API AUTHENTICATION TYPES - Complex authentication types
    # =========================================================================

    class Authentication:
        """API authentication complex types."""

        AuthConfiguration = dict[str, FlextTypes.Core.ConfigValue | dict[str, object]]
        AuthCredentials = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        AuthTokenData = dict[str, FlextTypes.Core.JsonValue | int | bool]
        AuthProviderConfig = dict[str, FlextTypes.Core.ConfigDict]
        AuthMiddleware = list[dict[str, FlextTypes.Core.JsonValue]]
        SecurityConfiguration = dict[str, bool | str | list[str] | dict[str, object]]

    # =========================================================================
    # API CLIENT TYPES - Complex HTTP client types
    # =========================================================================

    class Client:
        """HTTP client complex types."""

        ClientConfiguration = dict[str, FlextTypes.Core.ConfigValue | dict[str, object]]
        ConnectionPool = dict[str, int | bool | dict[str, object]]
        RetryConfiguration = dict[str, int | float | list[str] | bool]
        TimeoutConfiguration = dict[str, int | float | dict[str, object]]
        ClientMiddleware = list[dict[str, FlextTypes.Core.JsonValue]]
        SessionManagement = dict[str, FlextTypes.Core.JsonValue | dict[str, object]]

    # =========================================================================
    # API PROJECT TYPES - Domain-specific project types extending FlextTypes
    # =========================================================================

    class Project(FlextTypes.Project):
        """API-specific project types extending FlextTypes.Project.

        Adds API-specific project types while inheriting generic types from FlextTypes.
        Follows domain separation principle: API domain owns API-specific types.
        """

        # API-specific project types extending the generic ones
        # ProjectType is inherited from FlextTypes.Project
        # No need to redefine it here as it would cause override issues

        # API-specific project configurations
        ApiProjectConfig = dict[str, FlextTypes.Core.ConfigValue | object]
        RestApiConfig = dict[str, str | int | bool | list[str]]
        GraphqlApiConfig = dict[str, bool | str | dict[str, object]]
        MicroserviceConfig = dict[str, FlextTypes.Core.ConfigValue | object]


# =============================================================================
# PUBLIC API EXPORTS - API types and classes
# =============================================================================

__all__: list[str] = [
    "FlextApiTypes",
]
