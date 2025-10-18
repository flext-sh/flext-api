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

from enum import StrEnum
from typing import NotRequired

from flext_core import FlextTypes
from typing_extensions import TypedDict

# =============================================================================
# API-SPECIFIC TYPE VARIABLES - Domain-specific TypeVars for API operations
# =============================================================================


class FlextApiTypes(FlextTypes):
    """API-specific type definitions extending FlextTypes.

    Domain-specific type system for HTTP/API operations.
    Contains ONLY complex API-specific types, no simple aliases.
    Uses Python 3.13+ type syntax and patterns.
    """

    # =========================================================================
    # COMMON API TYPES - Frequently used API types
    # =========================================================================

    # HTTP-specific type aliases
    type JsonObject = dict[str, FlextTypes.JsonValue]
    type FlextWebData = str | bytes | JsonObject
    type FlextWebHeaders = dict[str, str | list[str]]
    type FlextWebParams = FlextWebHeaders
    type RequestData = FlextWebData
    type ResponseData = FlextWebData

    # =========================================================================
    # CORE API TYPES - Commonly used API type aliases extending FlextTypes
    # =========================================================================

    type ConnectionDict = JsonObject
    type ClientConfigDict = dict[str, object]
    type ResponseDict = JsonObject
    type MetricsDict = dict[str, str | int | float]
    type CacheDict = JsonObject
    type StorageDict = JsonObject
    type UtilityDict = dict[str, FlextTypes.JsonValue]

    # Template and structured response types
    type ResponseTemplateDict = dict[str, str | dict[str, FlextTypes.JsonValue]]
    type ErrorTemplateDict = dict[str, str | dict[str, FlextTypes.JsonValue]]

    # Model and data types
    type FilterConditionsDict = dict[str, FlextTypes.JsonValue]
    type QueryParamsDict = dict[str, str | list[str]]
    type RequestKwargsDict = dict[str, FlextTypes.JsonValue]
    type ContextDict = dict[str, FlextTypes.JsonValue]
    type DetailsDict = dict[str, FlextTypes.JsonValue]
    type ResponseList = list[dict[str, FlextTypes.JsonValue]]

    # =========================================================================
    # HTTP REQUEST TYPES - Complex request handling types
    # =========================================================================

    class Request:
        """HTTP request complex types."""

        RequestConfiguration = dict[
            str,
            str | int | bool | list[str] | dict[str, FlextTypes.JsonValue],
        ]
        RequestHeaders = dict[str, str | list[str]]
        RequestParameters = dict[str, FlextTypes.JsonValue | list[FlextTypes.JsonValue]]
        RequestBody = dict[str, FlextTypes.JsonValue] | str | bytes
        RequestMiddleware = list[dict[str, FlextTypes.JsonValue]]
        RequestValidation = dict[str, list[str] | dict[str, FlextTypes.JsonValue]]

    # =========================================================================
    # HTTP RESPONSE TYPES - Complex response handling types
    # =========================================================================

    class Response:
        """HTTP response complex types."""

        ResponseConfiguration = dict[
            str, FlextTypes.JsonValue | dict[str, FlextTypes.JsonValue]
        ]
        ResponseHeaders = dict[str, str | list[str]]
        ResponseBody = dict[str, FlextTypes.JsonValue] | str | bytes
        ResponseMetadata = dict[
            str, int | float | str | dict[str, FlextTypes.JsonValue]
        ]
        ResponseTransformation = list[dict[str, FlextTypes.JsonValue]]
        ResponseValidation = dict[str, bool | str | list[str]]

    # =========================================================================
    # API ENDPOINT TYPES - Complex endpoint management types
    # =========================================================================

    class Endpoint:
        """API endpoint complex types."""

        EndpointConfiguration = dict[
            str,
            FlextTypes.JsonValue | list[str] | dict[str, FlextTypes.JsonValue],
        ]
        EndpointMetadata = dict[
            str,
            str | int | list[str] | dict[str, FlextTypes.JsonValue],
        ]
        EndpointValidation = dict[
            str,
            list[str] | dict[str, FlextTypes.JsonValue] | bool,
        ]
        EndpointMiddleware = list[dict[str, FlextTypes.JsonValue]]
        EndpointDocumentation = dict[str, str | dict[str, FlextTypes.JsonValue]]
        RouteConfiguration = dict[
            str, str | list[str] | dict[str, FlextTypes.JsonValue]
        ]

    # =========================================================================
    # API AUTHENTICATION TYPES - Complex authentication types
    # =========================================================================

    class Authentication:
        """API authentication complex types."""

        AuthConfiguration = dict[str, object | dict[str, object]]
        AuthCredentials = dict[str, str | dict[str, FlextTypes.JsonValue]]
        AuthTokenData = dict[str, FlextTypes.JsonValue | int | bool]
        AuthProviderConfig = dict[str, FlextTypes.ConfigDict]
        AuthMiddleware = list[dict[str, FlextTypes.JsonValue]]
        SecurityConfiguration = dict[
            str,
            bool | str | list[str] | dict[str, object],
        ]

    # =========================================================================
    # API CLIENT TYPES - Complex HTTP client types
    # =========================================================================

    class Client:
        """HTTP client complex types."""

        ClientConfiguration = dict[str, object | dict[str, object]]
        ConnectionPool = dict[str, int | bool | dict[str, int | bool]]
        RetryConfiguration = dict[str, int | float | list[str] | bool]
        TimeoutConfiguration = dict[str, int | float | dict[str, int | float]]
        ClientMiddleware = list[dict[str, FlextTypes.JsonValue]]
        SessionManagement = dict[
            str, FlextTypes.JsonValue | dict[str, FlextTypes.JsonValue]
        ]

        class FlextWebKwargs(TypedDict):
            """Type definition for HTTP request kwargs."""

            params: NotRequired[dict[str, str] | None]
            data: NotRequired[dict[str, str] | None]
            json: NotRequired[dict[str, str] | None]
            headers: NotRequired[dict[str, str] | None]
            request_timeout: NotRequired[int | None]
            timeout: NotRequired[float | None]

    # =========================================================================
    # API PROJECT TYPES - Domain-specific project types extending FlextTypes
    # =========================================================================

    class Project(FlextTypes):
        """API-specific project types extending FlextTypes.

        Adds API-specific project types while inheriting generic types from FlextTypes.
        Follows domain separation principle: API domain owns API-specific types.
        """

        # API-specific project types extending the generic ones
        # ProjectType is inherited from FlextTypes
        # No need to redefine it here as it would cause override issues

        # API-specific project configurations
        ApiProjectConfig = dict[str, object]
        RestApiConfig = dict[str, str | int | bool | list[str]]
        GraphqlApiConfig = dict[str, bool | str | dict[str, object]]
        MicroserviceConfig = dict[str, object]

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
        FlextWebProtocolConfig = dict[
            str, bool | int | str | dict[str, FlextTypes.JsonValue]
        ]
        WebSocketProtocolConfig = dict[
            str, bool | int | str | dict[str, FlextTypes.JsonValue]
        ]
        GraphQLProtocolConfig = dict[str, bool | str | dict[str, FlextTypes.JsonValue]]
        GrpcProtocolConfig = dict[str, bool | str | dict[str, FlextTypes.JsonValue]]
        SSEProtocolConfig = dict[
            str, bool | int | str | dict[str, FlextTypes.JsonValue]
        ]

        # Protocol messages
        ProtocolMessage = dict[str, FlextTypes.JsonValue] | str | bytes
        WebSocketMessage = dict[str, FlextTypes.JsonValue] | str | bytes
        GraphQLQuery = str
        GraphQLMutation = str
        GraphQLSubscription = str
        SSEEvent = dict[str, str | FlextTypes.JsonValue]

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
        OpenApiSchema = dict[str, FlextTypes.JsonValue]
        ApiSchema = dict[str, FlextTypes.JsonValue]
        JsonSchema = dict[str, FlextTypes.JsonValue]
        GraphQLSchema = str  # SDL (Schema Definition Language)
        ProtobufSchema = str  # .proto file content

        # Schema validation
        ValidationResult = dict[
            str,
            bool | list[str] | dict[str, FlextTypes.JsonValue],
        ]
        ValidationErrors = list[dict[str, str | FlextTypes.JsonValue]]

        # Schema metadata
        SchemaMetadata = dict[str, str | dict[str, FlextTypes.JsonValue]]

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
        FlextWebTransportConfig = dict[str, bool | int | dict[str, int | bool]]
        WebSocketTransportConfig = dict[
            str, bool | int | str | dict[str, FlextTypes.JsonValue]
        ]
        GraphQLTransportConfig = dict[str, str | dict[str, FlextTypes.JsonValue]]
        GrpcTransportConfig = dict[str, str | int | dict[str, FlextTypes.JsonValue]]

        # Connection management
        ConnectionInfo = dict[str, str | int | bool | dict[str, FlextTypes.JsonValue]]
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
        PluginConfig = dict[str, object]
        PluginMetadata = dict[str, str | bool | dict[str, FlextTypes.JsonValue]]

        # Plugin registry
        RegistryEntry = dict[str, str | object | dict[str, FlextTypes.JsonValue]]

    # =========================================================================
    # SERIALIZATION TYPES - Serialization format types
    # =========================================================================

    class Serialization:
        """Serialization-related types."""

        class SerializationFormat(StrEnum):
            """Supported serialization formats."""

            JSON = "json"
            MSGPACK = "msgpack"
            CBOR = "cbor"
            CUSTOM = "custom"

    # =========================================================================
    # ENHANCED API TYPES - Advanced flext-core integration types
    # =========================================================================

    class AsyncTypes:
        """Enhanced async types for HTTP API operations with flext-core integration.

        This namespace provides advanced async types that integrate with flext-core
        async patterns for modern HTTP API development.

        Examples:
            Async HTTP operations with proper typing:

            >>> async def fetch_data(
            ...     url: Async.FlextWebUrl,
            ... ) -> Async.FlextApiModels.HttpResponse:
            ...     response = await http_client.get(url)
            ...     return {"data": response.json(), "status": response.status_code}
            >>>
            >>> async def batch_process(
            ...     requests: Async.FlextWebRequestList,
            ... ) -> Async.FlextWebResult:
            ...     return await asyncio.gather(*[
            ...         process_request(req) for req in requests
            ...     ])

        """

    class ErrorHandlingTypes:
        """Enhanced error handling types for HTTP API operations.

        This namespace provides comprehensive error handling types that integrate
        with flext-core error handling patterns for robust HTTP API error management.

        Examples:
            HTTP error classification and handling:

            >>> def classify_http_error(
            ...     error: FlextApiModels.FlextWebError,
            ... ) -> FlextApiModels.FlextWebErrorCategory:
            ...     if error.status_code >= 500:
            ...         return "server_error"
            ...     elif error.status_code >= 400:
            ...         return "client_error"
            ...     return "unknown"
            >>>
            >>> def handle_http_error(
            ...     error: FlextApiModels.FlextWebError,
            ... ) -> FlextApiModels.FlextWebErrorRecovery:
            ...     if error.category == "server_error":
            ...         return {"action": "retry", "delay": 1.0}
            ...     return {"action": "fail", "message": error.message}

        """

        type FlextWebError = dict[str, int | str | dict[str, FlextTypes.JsonValue]]
        type FlextWebErrorCategory = str
        type FlextWebErrorRecovery = dict[
            str, str | float | dict[str, FlextTypes.JsonValue]
        ]

        type FlextWebErrorHandler = dict[
            str, FlextWebErrorCategory | FlextWebErrorRecovery
        ]
        type FlextWebErrorRegistry = dict[str, FlextWebErrorHandler]

        type FlextWebRetryStrategy = dict[str, int | float | str]
        type FlextWebCircuitBreaker = dict[str, bool | int | float | str]

    class ServiceTypes:
        """Enhanced service layer types for HTTP API operations.

        This namespace provides comprehensive service types that integrate
        with flext-core service patterns for robust HTTP API service management.

        Examples:
            Service registration and discovery:

            >>> services: FlextApiModels.FlextWebServiceRegistry = {
            ...     "user_service": UserService(),
            ...     "auth_service": AuthService(),
            ...     "notification_service": NotificationService(),
            ... }
            >>>
            >>> service_configs: FlextApiModels.FlextWebServiceConfig = {
            ...     "user_service": {"timeout": 30, "retries": 3},
            ...     "auth_service": {"timeout": 15, "retries": 2},
            ... }

        """

        type FlextWebServiceRegistry = dict[str, object]
        type FlextWebServiceConfig = dict[str, dict[str, int | float | str]]
        type FlextWebServiceFactory = dict[str, object]

        # Enhanced service lifecycle types
        type FlextWebServiceLifecycle = str
        type FlextWebServiceHealth = dict[str, bool | str | int]
        type FlextWebServiceStatus = dict[
            str, FlextWebServiceLifecycle | dict[str, int | float]
        ]

        # Enhanced service communication types
        type FlextWebServiceEndpoint = str
        type FlextWebServiceProtocol = str
        type FlextWebServiceContract = dict[
            str, FlextWebServiceEndpoint | FlextWebServiceProtocol
        ]

    class ValidationTypes:
        """Enhanced validation types for HTTP API operations.

        This namespace provides comprehensive validation types that integrate
        with flext-core validation patterns for robust HTTP API validation.

        Examples:
            HTTP request/response validation:

            >>> def validate_request_schema(
            ...     request: FlextApiModels.FlextWebRequestSchema,
            ... ) -> FlextApiModels.FlextWebValidationResult:
            ...     if not request.get("method"):
            ...         return {"valid": False, "errors": ["method required"]}
            ...     return {"valid": True, "warnings": []}
            >>>
            >>> def validate_response_schema(
            ...     response: FlextApiModels.FlextWebResponseSchema,
            ... ) -> FlextApiModels.FlextWebValidationResult:
            ...     if response.get("status_code", 200) >= 400:
            ...         return {"valid": False, "errors": ["response error"]}
            ...     return {"valid": True, "warnings": []}

        """

        type FlextWebRequestSchema = dict[
            str, str | int | bool | dict[str, FlextTypes.JsonValue]
        ]
        type FlextWebResponseSchema = dict[
            str, int | str | dict[str, FlextTypes.JsonValue]
        ]
        type FlextWebValidationResult = dict[str, bool | list[str]]

        type FlextWebFieldValidator = dict[str, object]
        type FlextWebSchemaValidator = dict[str, FlextWebFieldValidator]

        type FlextWebValidationRule = dict[str, str | dict[str, FlextTypes.JsonValue]]
        type FlextWebValidationRules = list[FlextWebValidationRule]

    class ProcessingTypes:
        """Enhanced processing types for HTTP API operations.

        This namespace provides comprehensive processing types that integrate
        with flext-core processing patterns for robust HTTP API processing.

        Examples:
            HTTP request processing pipeline:

            >>> def process_request_pipeline(
            ...     request: FlextApiModels.FlextWebRequestPipeline,
            ... ) -> FlextApiModels.FlextWebProcessingResult:
            ...     # Validate -> Transform -> Enrich -> Respond
            ...     return {
            ...         "processed": True,
            ...         "steps": ["validation", "transformation", "enrichment"],
            ...         "result": request,
            ...     }
            >>>
            >>> def batch_process_requests(
            ...     requests: FlextApiModels.FlextWebRequestBatch,
            ... ) -> FlextApiModels.FlextWebBatchResult:
            ...     return {
            ...         "processed": len(requests),
            ...         "successful": len(requests),
            ...         "failed": 0,
            ...         "results": requests,
            ...     }

        """

        type FlextWebRequestPipeline = list[dict[str, object]]
        type FlextWebResponsePipeline = list[dict[str, object]]
        type FlextWebProcessingResult = dict[str, bool | list[str] | object]

        type FlextWebRequestBatch = list[dict[str, object]]
        type FlextWebResponseBatch = list[dict[str, object]]
        type FlextWebBatchResult = dict[str, int | list[object]]

        type FlextWebMiddlewareConfig = dict[str, object | dict[str, object]]
        type FlextWebMiddlewarePipeline = list[FlextWebMiddlewareConfig]


# =============================================================================
# PUBLIC API EXPORTS - API types and classes
# =============================================================================

__all__: list[str] = [
    "FlextApiTypes",
]
