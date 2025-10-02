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
    RequestBody = dict[str, FlextTypes.Core.JsonValue] | str | bytes
    Timeout = int | float

    # HTTP-specific type aliases
    type HttpStatusCode = int
    JsonObject = dict[str, FlextTypes.Core.JsonValue]
    HttpData = str | bytes | dict[str, FlextTypes.Core.JsonValue]
    HttpHeaders = dict[str, str | list[str]]
    HttpMethod = str  # GET, POST, PUT, DELETE, etc.
    HttpParams = dict[str, str | list[str]]
    RequestData = dict[str, FlextTypes.Core.JsonValue] | str | bytes
    ResponseData = dict[str, FlextTypes.Core.JsonValue] | str | bytes
    type StorageKey = str
    StorageValue = FlextTypes.Core.JsonValue
    TimeoutSeconds = int | float
    # =========================================================================
    # CORE API TYPES - Commonly used API type aliases extending FlextTypes.Core
    # =========================================================================

    class Core(FlextTypes.Core):
        """Core API types extending FlextTypes.Core."""

        ConnectionDict = dict[str, FlextTypes.Core.JsonValue]
        ClientConfigDict = dict[str, FlextTypes.Core.ConfigValue]
        RequestConfigDict = dict[str, FlextTypes.Core.JsonValue]
        ResponseDict = dict[str, FlextTypes.Core.JsonValue]
        MetricsDict = dict[str, int | float | str]
        CacheDict = dict[str, FlextTypes.Core.JsonValue]
        RetryInfoDict = dict[str, int | float | bool]
        StorageDict = dict[str, FlextTypes.Core.JsonValue]
        UtilityDict = dict[str, FlextTypes.Core.JsonValue]

        # HTTP operation types
        HttpRequestDict = dict[str, FlextTypes.Core.JsonValue]
        HttpResponseDict = dict[str, FlextTypes.Core.JsonValue]
        ApiSetupDict = dict[str, FlextTypes.Core.ConfigValue]
        EndpointDict = dict[str, FlextTypes.Core.JsonValue]

        # Template and structured response types
        ResponseTemplateDict = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        ErrorTemplateDict = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]

        # Model and data types
        FilterConditionsDict = dict[str, FlextTypes.Core.JsonValue]
        QueryParamsDict = dict[str, str | list[str]]
        RequestKwargsDict = dict[str, FlextTypes.Core.JsonValue]
        ContextDict = dict[str, FlextTypes.Core.JsonValue]
        DetailsDict = dict[str, FlextTypes.Core.JsonValue]
        ResponseList = list[dict[str, FlextTypes.Core.JsonValue]]

    # =========================================================================
    # HTTP REQUEST TYPES - Complex request handling types
    # =========================================================================

    class Request:
        """HTTP request complex types."""

        RequestConfiguration = dict[
            str, str | int | bool | list[str] | dict[str, FlextTypes.Core.JsonValue]
        ]
        RequestHeaders = dict[str, str | list[str]]
        RequestParameters = dict[
            str, FlextTypes.Core.JsonValue | list[FlextTypes.Core.JsonValue]
        ]
        RequestBody = dict[str, FlextTypes.Core.JsonValue] | str | bytes
        RequestMiddleware = list[dict[str, FlextTypes.Core.JsonValue]]
        RequestValidation = dict[str, list[str] | dict[str, FlextTypes.Core.JsonValue]]

    # =========================================================================
    # HTTP RESPONSE TYPES - Complex response handling types
    # =========================================================================

    class Response:
        """HTTP response complex types."""

        ResponseConfiguration = dict[
            str, FlextTypes.Core.JsonValue | dict[str, FlextTypes.Core.JsonValue]
        ]
        ResponseHeaders = dict[str, str | list[str]]
        ResponseBody = dict[str, FlextTypes.Core.JsonValue] | str | bytes
        ResponseMetadata = dict[
            str, int | float | str | dict[str, FlextTypes.Core.JsonValue]
        ]
        ResponseTransformation = list[dict[str, FlextTypes.Core.JsonValue]]
        ResponseValidation = dict[str, bool | str | list[str]]

    # =========================================================================
    # API ENDPOINT TYPES - Complex endpoint management types
    # =========================================================================

    class Endpoint:
        """API endpoint complex types."""

        EndpointConfiguration = dict[
            str,
            FlextTypes.Core.JsonValue
            | list[str]
            | dict[str, FlextTypes.Core.JsonValue],
        ]
        EndpointMetadata = dict[
            str, str | int | list[str] | dict[str, FlextTypes.Core.JsonValue]
        ]
        EndpointValidation = dict[
            str, list[str] | dict[str, FlextTypes.Core.JsonValue] | bool
        ]
        EndpointMiddleware = list[dict[str, FlextTypes.Core.JsonValue]]
        EndpointDocumentation = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        RouteConfiguration = dict[
            str, str | list[str] | dict[str, FlextTypes.Core.JsonValue]
        ]

    # =========================================================================
    # API AUTHENTICATION TYPES - Complex authentication types
    # =========================================================================

    class Authentication:
        """API authentication complex types."""

        AuthConfiguration = dict[
            str, FlextTypes.Core.ConfigValue | dict[str, FlextTypes.Core.ConfigValue]
        ]
        AuthCredentials = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        AuthTokenData = dict[str, FlextTypes.Core.JsonValue | int | bool]
        AuthProviderConfig = dict[str, FlextTypes.Core.ConfigDict]
        AuthMiddleware = list[dict[str, FlextTypes.Core.JsonValue]]
        SecurityConfiguration = dict[
            str, bool | str | list[str] | dict[str, FlextTypes.Core.ConfigValue]
        ]

    # =========================================================================
    # API CLIENT TYPES - Complex HTTP client types
    # =========================================================================

    class Client:
        """HTTP client complex types."""

        ClientConfiguration = dict[
            str, FlextTypes.Core.ConfigValue | dict[str, FlextTypes.Core.ConfigValue]
        ]
        ConnectionPool = dict[str, int | bool | dict[str, int | bool]]
        RetryConfiguration = dict[str, int | float | list[str] | bool]
        TimeoutConfiguration = dict[str, int | float | dict[str, int | float]]
        ClientMiddleware = list[dict[str, FlextTypes.Core.JsonValue]]
        SessionManagement = dict[
            str, FlextTypes.Core.JsonValue | dict[str, FlextTypes.Core.JsonValue]
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
        # ProjectType is inherited from FlextTypes.Project
        # No need to redefine it here as it would cause override issues

        # API-specific project configurations
        ApiProjectConfig = dict[str, FlextTypes.Core.ConfigValue]
        RestApiConfig = dict[str, str | int | bool | list[str]]
        GraphqlApiConfig = dict[
            str, bool | str | dict[str, FlextTypes.Core.ConfigValue]
        ]
        MicroserviceConfig = dict[str, FlextTypes.Core.ConfigValue]

    # =========================================================================
    # PROTOCOL TYPES - Protocol-specific types (Phase 1 - Transformation)
    # =========================================================================

    class Protocol:
        """Protocol-specific types for multi-protocol support.

        Types for HTTP, WebSocket, GraphQL, gRPC, SSE protocols.
        """

        # Protocol identifiers
        ProtocolName = str  # "http", "websocket", "graphql", "grpc", "sse"
        ProtocolVersion = str  # "1.1", "2.0", "3.0", etc.

        # Protocol configurations
        HttpProtocolConfig = dict[
            str, bool | int | str | dict[str, FlextTypes.Core.JsonValue]
        ]
        WebSocketProtocolConfig = dict[
            str, bool | int | str | dict[str, FlextTypes.Core.JsonValue]
        ]
        GraphQLProtocolConfig = dict[
            str, bool | str | dict[str, FlextTypes.Core.JsonValue]
        ]
        GrpcProtocolConfig = dict[
            str, bool | str | dict[str, FlextTypes.Core.JsonValue]
        ]
        SSEProtocolConfig = dict[
            str, bool | int | str | dict[str, FlextTypes.Core.JsonValue]
        ]

        # Protocol messages
        ProtocolMessage = dict[str, FlextTypes.Core.JsonValue] | str | bytes
        WebSocketMessage = dict[str, FlextTypes.Core.JsonValue] | str | bytes
        GraphQLQuery = str
        GraphQLMutation = str
        GraphQLSubscription = str
        SSEEvent = dict[str, str | FlextTypes.Core.JsonValue]

    # =========================================================================
    # SCHEMA TYPES - Schema system types (Phase 1 - Transformation)
    # =========================================================================

    class Schema:
        """Schema system types for multi-schema support.

        Types for OpenAPI, API, JSON Schema, GraphQL Schema, Protobuf.
        """

        # Schema identifiers
        SchemaType = str  # "openapi", "api", "jsonschema", "graphql", "protobuf"
        SchemaVersion = str  # "3.1.0", "2.6.0", etc.

        # Schema definitions
        OpenApiSchema = dict[str, FlextTypes.Core.JsonValue]
        ApiSchema = dict[str, FlextTypes.Core.JsonValue]
        JsonSchema = dict[str, FlextTypes.Core.JsonValue]
        GraphQLSchema = str  # SDL (Schema Definition Language)
        ProtobufSchema = str  # .proto file content

        # Schema validation
        ValidationResult = dict[
            str, bool | list[str] | dict[str, FlextTypes.Core.JsonValue]
        ]
        ValidationErrors = list[dict[str, str | FlextTypes.Core.JsonValue]]

        # Schema metadata
        SchemaMetadata = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]

    # =========================================================================
    # TRANSPORT TYPES - Transport layer types (Phase 1 - Transformation)
    # =========================================================================

    class Transport:
        """Transport layer types for network communication.

        Types for httpx, websockets, gql, grpcio transports.
        """

        # Transport identifiers
        TransportName = str  # "httpx", "websockets", "gql", "grpcio"

        # Transport configurations
        HttpTransportConfig = dict[str, bool | int | dict[str, int | bool]]
        WebSocketTransportConfig = dict[
            str, bool | int | str | dict[str, FlextTypes.Core.JsonValue]
        ]
        GraphQLTransportConfig = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        GrpcTransportConfig = dict[
            str, str | int | dict[str, FlextTypes.Core.JsonValue]
        ]

        # Connection management
        ConnectionInfo = dict[
            str, str | int | bool | dict[str, FlextTypes.Core.JsonValue]
        ]
        ConnectionStatus = str  # "connected", "disconnected", "error"

    # =========================================================================
    # PLUGIN TYPES - Plugin system types (Phase 1 - Transformation)
    # =========================================================================

    class Plugin:
        """Plugin system types for extensibility.

        Types for protocol, schema, transport, and authentication plugins.
        """

        # Plugin identifiers
        PluginName = str
        PluginVersion = str
        PluginType = str  # "protocol", "schema", "transport", "auth"

        # Plugin configurations
        PluginConfig = dict[str, FlextTypes.Core.ConfigValue]
        PluginMetadata = dict[str, str | bool | dict[str, FlextTypes.Core.JsonValue]]

        # Plugin registry
        RegistryEntry = dict[str, str | object | dict[str, FlextTypes.Core.JsonValue]]


# =============================================================================
# PUBLIC API EXPORTS - API types and classes
# =============================================================================

__all__: list[str] = [
    "FlextApiTypes",
]
