"""FLEXT API Types - Domain-specific API type definitions.

This module provides API-specific type definitions extending FlextCore.Types.
Follows FLEXT standards:
- Domain-specific complex types only
- No simple aliases to primitive types
- Python 3.13+ syntax
- Extends FlextCore.Types properly

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from enum import StrEnum
from typing import NotRequired

from flext_core import FlextCore
from typing_extensions import TypedDict

# =============================================================================
# API-SPECIFIC TYPE VARIABLES - Domain-specific TypeVars for API operations
# =============================================================================


class FlextApiTypes(FlextCore.Types):
    """API-specific type definitions extending FlextCore.Types.

    Domain-specific type system for HTTP/API operations.
    Contains ONLY complex API-specific types, no simple aliases.
    Uses Python 3.13+ type syntax and patterns.
    """

    # =========================================================================
    # COMMON API TYPES - Frequently used API types
    # =========================================================================

    # HTTP-specific type aliases
    type JsonObject = dict[str, FlextCore.Types.JsonValue]
    type HttpData = str | bytes | JsonObject
    type HttpHeaders = dict[str, str | FlextCore.Types.StringList]
    type HttpParams = HttpHeaders
    type RequestData = HttpData
    type ResponseData = HttpData

    # =========================================================================
    # CORE API TYPES - Commonly used API type aliases extending FlextCore.Types
    # =========================================================================

    type ConnectionDict = JsonObject
    type ClientConfigDict = dict[str, FlextCore.Types.ConfigValue]
    type ResponseDict = JsonObject
    type MetricsDict = dict[str, str | int | float]
    type CacheDict = JsonObject
    type StorageDict = JsonObject
    type UtilityDict = dict[str, FlextCore.Types.JsonValue]

    # Template and structured response types
    type ResponseTemplateDict = dict[str, str | dict[str, FlextCore.Types.JsonValue]]
    type ErrorTemplateDict = dict[str, str | dict[str, FlextCore.Types.JsonValue]]

    # Model and data types
    type FilterConditionsDict = dict[str, FlextCore.Types.JsonValue]
    type QueryParamsDict = dict[str, str | FlextCore.Types.StringList]
    type RequestKwargsDict = dict[str, FlextCore.Types.JsonValue]
    type ContextDict = dict[str, FlextCore.Types.JsonValue]
    type DetailsDict = dict[str, FlextCore.Types.JsonValue]
    type ResponseList = list[dict[str, FlextCore.Types.JsonValue]]

    # =========================================================================
    # HTTP REQUEST TYPES - Complex request handling types
    # =========================================================================

    class Request:
        """HTTP request complex types."""

        RequestConfiguration = dict[
            str,
            str
            | int
            | bool
            | FlextCore.Types.StringList
            | dict[str, FlextCore.Types.JsonValue],
        ]
        RequestHeaders = dict[str, str | FlextCore.Types.StringList]
        RequestParameters = dict[
            str, FlextCore.Types.JsonValue | list[FlextCore.Types.JsonValue]
        ]
        RequestBody = dict[str, FlextCore.Types.JsonValue] | str | bytes
        RequestMiddleware = list[dict[str, FlextCore.Types.JsonValue]]
        RequestValidation = dict[
            str, FlextCore.Types.StringList | dict[str, FlextCore.Types.JsonValue]
        ]

    # =========================================================================
    # HTTP RESPONSE TYPES - Complex response handling types
    # =========================================================================

    class Response:
        """HTTP response complex types."""

        ResponseConfiguration = dict[
            str, FlextCore.Types.JsonValue | dict[str, FlextCore.Types.JsonValue]
        ]
        ResponseHeaders = dict[str, str | FlextCore.Types.StringList]
        ResponseBody = dict[str, FlextCore.Types.JsonValue] | str | bytes
        ResponseMetadata = dict[
            str, int | float | str | dict[str, FlextCore.Types.JsonValue]
        ]
        ResponseTransformation = list[dict[str, FlextCore.Types.JsonValue]]
        ResponseValidation = dict[str, bool | str | FlextCore.Types.StringList]

    # =========================================================================
    # API ENDPOINT TYPES - Complex endpoint management types
    # =========================================================================

    class Endpoint:
        """API endpoint complex types."""

        EndpointConfiguration = dict[
            str,
            FlextCore.Types.JsonValue
            | FlextCore.Types.StringList
            | dict[str, FlextCore.Types.JsonValue],
        ]
        EndpointMetadata = dict[
            str,
            str
            | int
            | FlextCore.Types.StringList
            | dict[str, FlextCore.Types.JsonValue],
        ]
        EndpointValidation = dict[
            str,
            FlextCore.Types.StringList | dict[str, FlextCore.Types.JsonValue] | bool,
        ]
        EndpointMiddleware = list[dict[str, FlextCore.Types.JsonValue]]
        EndpointDocumentation = dict[str, str | dict[str, FlextCore.Types.JsonValue]]
        RouteConfiguration = dict[
            str, str | FlextCore.Types.StringList | dict[str, FlextCore.Types.JsonValue]
        ]

    # =========================================================================
    # API AUTHENTICATION TYPES - Complex authentication types
    # =========================================================================

    class Authentication:
        """API authentication complex types."""

        AuthConfiguration = dict[
            str, FlextCore.Types.ConfigValue | dict[str, FlextCore.Types.ConfigValue]
        ]
        AuthCredentials = dict[str, str | dict[str, FlextCore.Types.JsonValue]]
        AuthTokenData = dict[str, FlextCore.Types.JsonValue | int | bool]
        AuthProviderConfig = dict[str, FlextCore.Types.ConfigDict]
        AuthMiddleware = list[dict[str, FlextCore.Types.JsonValue]]
        SecurityConfiguration = dict[
            str,
            bool
            | str
            | FlextCore.Types.StringList
            | dict[str, FlextCore.Types.ConfigValue],
        ]

    # =========================================================================
    # API CLIENT TYPES - Complex HTTP client types
    # =========================================================================

    class Client:
        """HTTP client complex types."""

        ClientConfiguration = dict[
            str, FlextCore.Types.ConfigValue | dict[str, FlextCore.Types.ConfigValue]
        ]
        ConnectionPool = dict[str, int | bool | dict[str, int | bool]]
        RetryConfiguration = dict[str, int | float | FlextCore.Types.StringList | bool]
        TimeoutConfiguration = dict[str, int | float | dict[str, int | float]]
        ClientMiddleware = list[dict[str, FlextCore.Types.JsonValue]]
        SessionManagement = dict[
            str, FlextCore.Types.JsonValue | dict[str, FlextCore.Types.JsonValue]
        ]

        class HttpKwargs(TypedDict):
            """Type definition for HTTP request kwargs."""

            params: NotRequired[FlextCore.Types.StringDict | None]
            data: NotRequired[FlextCore.Types.StringDict | None]
            json: NotRequired[FlextCore.Types.StringDict | None]
            headers: NotRequired[FlextCore.Types.StringDict | None]
            request_timeout: NotRequired[int | None]
            timeout: NotRequired[float | None]

    # =========================================================================
    # API PROJECT TYPES - Domain-specific project types extending FlextCore.Types
    # =========================================================================

    class Project(FlextCore.Types.Project):
        """API-specific project types extending FlextCore.Types.Project.

        Adds API-specific project types while inheriting generic types from FlextCore.Types.
        Follows domain separation principle: API domain owns API-specific types.
        """

        # API-specific project types extending the generic ones
        # ProjectType is inherited from FlextCore.Types.Project
        # No need to redefine it here as it would cause override issues

        # API-specific project configurations
        ApiProjectConfig = dict[str, FlextCore.Types.ConfigValue]
        RestApiConfig = dict[str, str | int | bool | FlextCore.Types.StringList]
        GraphqlApiConfig = dict[
            str, bool | str | dict[str, FlextCore.Types.ConfigValue]
        ]
        MicroserviceConfig = dict[str, FlextCore.Types.ConfigValue]

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
            str, bool | int | str | dict[str, FlextCore.Types.JsonValue]
        ]
        WebSocketProtocolConfig = dict[
            str, bool | int | str | dict[str, FlextCore.Types.JsonValue]
        ]
        GraphQLProtocolConfig = dict[
            str, bool | str | dict[str, FlextCore.Types.JsonValue]
        ]
        GrpcProtocolConfig = dict[
            str, bool | str | dict[str, FlextCore.Types.JsonValue]
        ]
        SSEProtocolConfig = dict[
            str, bool | int | str | dict[str, FlextCore.Types.JsonValue]
        ]

        # Protocol messages
        ProtocolMessage = dict[str, FlextCore.Types.JsonValue] | str | bytes
        WebSocketMessage = dict[str, FlextCore.Types.JsonValue] | str | bytes
        GraphQLQuery = str
        GraphQLMutation = str
        GraphQLSubscription = str
        SSEEvent = dict[str, str | FlextCore.Types.JsonValue]

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
        OpenApiSchema = dict[str, FlextCore.Types.JsonValue]
        ApiSchema = dict[str, FlextCore.Types.JsonValue]
        JsonSchema = dict[str, FlextCore.Types.JsonValue]
        GraphQLSchema = str  # SDL (Schema Definition Language)
        ProtobufSchema = str  # .proto file content

        # Schema validation
        ValidationResult = dict[
            str,
            bool | FlextCore.Types.StringList | dict[str, FlextCore.Types.JsonValue],
        ]
        ValidationErrors = list[dict[str, str | FlextCore.Types.JsonValue]]

        # Schema metadata
        SchemaMetadata = dict[str, str | dict[str, FlextCore.Types.JsonValue]]

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
            str, bool | int | str | dict[str, FlextCore.Types.JsonValue]
        ]
        GraphQLTransportConfig = dict[str, str | dict[str, FlextCore.Types.JsonValue]]
        GrpcTransportConfig = dict[
            str, str | int | dict[str, FlextCore.Types.JsonValue]
        ]

        # Connection management
        ConnectionInfo = dict[
            str, str | int | bool | dict[str, FlextCore.Types.JsonValue]
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
        PluginConfig = dict[str, FlextCore.Types.ConfigValue]
        PluginMetadata = dict[str, str | bool | dict[str, FlextCore.Types.JsonValue]]

        # Plugin registry
        RegistryEntry = dict[str, str | object | dict[str, FlextCore.Types.JsonValue]]

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

            >>> async def fetch_data(url: Async.HttpUrl) -> Async.HttpResponse:
            ...     response = await http_client.get(url)
            ...     return {"data": response.json(), "status": response.status_code}
            >>>
            >>> async def batch_process(
            ...     requests: Async.HttpRequestList,
            ... ) -> Async.HttpResult:
            ...     return await asyncio.gather(*[
            ...         process_request(req) for req in requests
            ...     ])

        """

        type HttpUrl = str
        type HttpMethod = str
        type HttpHeaders = dict[str, str]
        type HttpParams = dict[str, str | FlextCore.Types.StringList]
        type HttpData = str | bytes | dict[str, FlextCore.Types.JsonValue]

        type HttpRequest = dict[
            str, HttpUrl | HttpMethod | HttpHeaders | HttpParams | HttpData
        ]
        type HttpResponse = dict[str, int | HttpData | HttpHeaders | float]
        type HttpRequestList = list[HttpRequest]
        type HttpResponseList = list[HttpResponse]

        type HttpResult = dict[str, HttpResponse | Exception | str]
        type HttpBatchResult = dict[str, list[HttpResult]]

        type StreamingResponse = dict[str, bytes | str | bool]
        type StreamingChunk = dict[str, bytes | int | float]

    class ErrorHandlingTypes:
        """Enhanced error handling types for HTTP API operations.

        This namespace provides comprehensive error handling types that integrate
        with flext-core error handling patterns for robust HTTP API error management.

        Examples:
            HTTP error classification and handling:

            >>> def classify_http_error(
            ...     error: ErrorHandling.HttpError,
            ... ) -> ErrorHandling.HttpErrorCategory:
            ...     if error.status_code >= 500:
            ...         return "server_error"
            ...     elif error.status_code >= 400:
            ...         return "client_error"
            ...     return "unknown"
            >>>
            >>> def handle_http_error(
            ...     error: ErrorHandling.HttpError,
            ... ) -> ErrorHandling.HttpErrorRecovery:
            ...     if error.category == "server_error":
            ...         return {"action": "retry", "delay": 1.0}
            ...     return {"action": "fail", "message": error.message}

        """

        type HttpError = dict[str, int | str | dict[str, FlextCore.Types.JsonValue]]
        type HttpErrorCategory = str
        type HttpErrorRecovery = dict[
            str, str | float | dict[str, FlextCore.Types.JsonValue]
        ]

        type HttpErrorHandler = dict[str, HttpErrorCategory | HttpErrorRecovery]
        type HttpErrorRegistry = dict[str, HttpErrorHandler]

        type HttpRetryStrategy = dict[str, int | float | str]
        type HttpCircuitBreaker = dict[str, bool | int | float | str]

    class ServiceTypes:
        """Enhanced service layer types for HTTP API operations.

        This namespace provides comprehensive service types that integrate
        with flext-core service patterns for robust HTTP API service management.

        Examples:
            Service registration and discovery:

            >>> services: Service.HttpServiceRegistry = {
            ...     "user_service": UserService(),
            ...     "auth_service": AuthService(),
            ...     "notification_service": NotificationService(),
            ... }
            >>>
            >>> service_configs: Service.HttpServiceConfig = {
            ...     "user_service": {"timeout": 30, "retries": 3},
            ...     "auth_service": {"timeout": 15, "retries": 2},
            ... }

        """

        type HttpServiceRegistry = FlextCore.Types.Dict
        type HttpServiceConfig = dict[str, dict[str, int | float | str]]
        type HttpServiceFactory = FlextCore.Types.Dict

        # Enhanced service lifecycle types
        type HttpServiceLifecycle = str
        type HttpServiceHealth = dict[str, bool | str | int]
        type HttpServiceStatus = dict[
            str, HttpServiceLifecycle | dict[str, int | float]
        ]

        # Enhanced service communication types
        type HttpServiceEndpoint = str
        type HttpServiceProtocol = str
        type HttpServiceContract = dict[str, HttpServiceEndpoint | HttpServiceProtocol]

    class ValidationTypes:
        """Enhanced validation types for HTTP API operations.

        This namespace provides comprehensive validation types that integrate
        with flext-core validation patterns for robust HTTP API validation.

        Examples:
            HTTP request/response validation:

            >>> def validate_request_schema(
            ...     request: Validation.HttpRequestSchema,
            ... ) -> Validation.HttpValidationResult:
            ...     if not request.get("method"):
            ...         return {"valid": False, "errors": ["method required"]}
            ...     return {"valid": True, "warnings": []}
            >>>
            >>> def validate_response_schema(
            ...     response: Validation.HttpResponseSchema,
            ... ) -> Validation.HttpValidationResult:
            ...     if response.get("status_code", 200) >= 400:
            ...         return {"valid": False, "errors": ["response error"]}
            ...     return {"valid": True, "warnings": []}

        """

        type HttpRequestSchema = dict[
            str, str | int | bool | dict[str, FlextCore.Types.JsonValue]
        ]
        type HttpResponseSchema = dict[
            str, int | str | dict[str, FlextCore.Types.JsonValue]
        ]
        type HttpValidationResult = dict[str, bool | FlextCore.Types.StringList]

        type HttpFieldValidator = FlextCore.Types.Dict
        type HttpSchemaValidator = dict[str, HttpFieldValidator]

        type HttpValidationRule = dict[str, str | dict[str, FlextCore.Types.JsonValue]]
        type HttpValidationRules = list[HttpValidationRule]

    class ProcessingTypes:
        """Enhanced processing types for HTTP API operations.

        This namespace provides comprehensive processing types that integrate
        with flext-core processing patterns for robust HTTP API processing.

        Examples:
            HTTP request processing pipeline:

            >>> def process_request_pipeline(
            ...     request: Processing.HttpRequestPipeline,
            ... ) -> Processing.HttpProcessingResult:
            ...     # Validate -> Transform -> Enrich -> Respond
            ...     return {
            ...         "processed": True,
            ...         "steps": ["validation", "transformation", "enrichment"],
            ...         "result": request,
            ...     }
            >>>
            >>> def batch_process_requests(
            ...     requests: Processing.HttpRequestBatch,
            ... ) -> Processing.HttpBatchResult:
            ...     return {
            ...         "processed": len(requests),
            ...         "successful": len(requests),
            ...         "failed": 0,
            ...         "results": requests,
            ...     }

        """

        type HttpRequestPipeline = list[FlextCore.Types.Dict]
        type HttpResponsePipeline = list[FlextCore.Types.Dict]
        type HttpProcessingResult = dict[
            str, bool | FlextCore.Types.StringList | object
        ]

        type HttpRequestBatch = list[FlextCore.Types.Dict]
        type HttpResponseBatch = list[FlextCore.Types.Dict]
        type HttpBatchResult = dict[str, int | FlextCore.Types.List]

        type HttpMiddlewareConfig = dict[str, object | FlextCore.Types.Dict]
        type HttpMiddlewarePipeline = list[HttpMiddlewareConfig]


# =============================================================================
# PUBLIC API EXPORTS - API types and classes
# =============================================================================

__all__: FlextCore.Types.StringList = [
    "FlextApiTypes",
]
