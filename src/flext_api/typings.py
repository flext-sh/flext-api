"""FLEXT API Types - HTTP-specific type system extending FlextTypes with hierarchical organization.

Unified HTTP type system extending flext-core FlextTypes with HTTP-specific domains
following Python 3.13+ syntax, strict hierarchical organization, and flext-core
foundation patterns for type-safe HTTP operations.

Module Role in Architecture:
    FlextApiTypes extends FlextTypes for HTTP-specific type definitions, following
    flext-core patterns with hierarchical nested classes, centralized type
    organization, and elimination of type duplication.

FlextApiTypes Architecture:
    FlextApiTypes(FlextTypes):              # Extends flext-core base types
        # HTTP Protocol Types:
        Http.Method = Literal["GET", "POST", "PUT", "DELETE", ...]
        Http.Status = int
        Http.Headers = dict[str, str]
        Http.QueryParams = dict[str, str | list[str]]

        # HTTP Request Types:
        Request.Body = str | bytes | dict[str, object] | None
        Request.Params = dict[str, str | int | float | bool]
        Request.FormData = dict[str, str | bytes]

        # HTTP Response Types:
        Response.Data = object
        Response.Json = dict[str, object] | list[object]
        Response.Content = bytes

        # HTTP Client Types:
        Client.Config = dict[str, object]
        Client.Timeout = float | tuple[float, float]
        Client.Plugin = object

Python 3.13+ Features:
    - Type statement syntax for performance optimization
    - Discriminated unions with Pydantic integration
    - Generic type parameters with proper constraints
    - Runtime-checkable protocols for type safety
    - Hierarchical organization following flext-core patterns

Integration with flext-core:
    - Extends FlextTypes for unified type hierarchy
    - Uses FlextResult patterns for type-safe operations
    - Follows flext-core hierarchical organization principles
    - Eliminates type duplication through inheritance
    - Maintains consistency with flext-core naming conventions

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from typing import Literal, Protocol, TypeVar, runtime_checkable

from flext_core import FlextResult, FlextTypes

# =============================================================================
# FLEXT-CORE COMPATIBLE TYPE VARIABLES - Use flext-core patterns
# =============================================================================

# Use flext-core type variables directly (T, U, V, K, R already defined in flext-core)
# HTTP-specific type variables extending flext-core foundation
HttpMethodT = TypeVar("HttpMethodT", bound=str)  # HTTP method types
HttpStatusT = TypeVar("HttpStatusT", bound=int)  # HTTP status code types
RequestBodyT = TypeVar("RequestBodyT", bound="str | bytes | dict[str, object] | None")
ResponseDataT = TypeVar("ResponseDataT", bound=object)
PluginT = TypeVar("PluginT", bound=object)  # Plugin instance types

# =============================================================================
# HTTP PROTOCOL INTERFACES - Runtime-checkable protocols for type safety
# =============================================================================


class FlextApiTypes(FlextTypes):
    """HTTP API type system extending flext-core FlextTypes with hierarchical organization.

    Unified type system following flext-core patterns with hierarchical nested classes,
    Python 3.13+ type syntax, and elimination of type duplication through inheritance
    from FlextTypes foundation.

    Architecture Principles:
        - Single Responsibility: HTTP-specific type definitions only
        - Open/Closed: Easy to extend with new HTTP patterns
        - Liskov Substitution: Consistent interface across all HTTP type categories
        - Interface Segregation: Clients depend only on HTTP types they use
        - Dependency Inversion: HTTP types depend on flext-core abstractions

    Integration with flext-core:
        - Extends FlextTypes for unified type hierarchy
        - Uses FlextResult patterns for type-safe HTTP operations
        - Follows flext-core hierarchical organization principles
        - Eliminates type duplication through proper inheritance
        - Maintains consistency with flext-core naming conventions

    HTTP Type Categories (use directly without aliases):
        - Http: HttpMethod, HttpStatus, HttpHeaders - USE DIRECTLY
        - Request: RequestBody, RequestParams, AuthCredentials - USE DIRECTLY
        - Response: ResponseData, JsonResponse, BinaryContent - USE DIRECTLY
        - Client: TimeoutConfig, RetryCount, ClientConfig - USE DIRECTLY
        - Plugin: BeforeRequestCallback, PluginInstance - USE DIRECTLY
        - Cache: CacheKey, CacheValue, TimeToLive - USE DIRECTLY
        - HttpValidation: RequestValidator, ValidationResult - USE DIRECTLY
        - Factory: ClientFactory, RequestBuilder - USE DIRECTLY
    """

    # =========================================================================
    # HTTP PROTOCOL TYPES - Core HTTP definitions using Python 3.13+ syntax
    # =========================================================================

    class Http:
        """Core HTTP protocol types - use directly without aliases.

        Use estes tipos diretamente no código:
        - Literal["GET", "POST", ...] instead of Http.Method
        - int instead of Http.Status
        - dict[str, str] instead of Http.Headers
        """

        # Direct type definitions for HTTP protocol
        HttpMethod = Literal[
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "PATCH",
            "HEAD",
            "OPTIONS",
            "TRACE",
            "CONNECT",
        ]
        HttpStatus = int
        HttpHeaders = dict[str, str]
        HeaderValue = str | list[str]
        QueryParameters = dict[str, str | int | float | bool | list[str]]

        # URL components
        HttpUrl = str
        UrlPath = str
        UrlScheme = Literal["http", "https"]
        PortNumber = int

    # =========================================================================
    # HTTP REQUEST TYPES - Request-specific definitions
    # =========================================================================

    class Request:
        """HTTP request types - use directly in code.

        Use diretamente:
        - str | bytes | dict[str, object] | None para request body
        - dict[str, str | int | float | bool] para params
        """

        # Direct HTTP request types
        RequestBody = str | bytes | dict[str, object] | list[object] | None
        RequestParams = dict[str, str | int | float | bool]
        RequestData = str | bytes | dict[str, object] | list[object] | None
        FormData = dict[str, str | bytes]
        FileUpload = dict[str, bytes | tuple[str, bytes]]

        # Authentication - use directly
        AuthCredentials = tuple[str, str] | str | None
        AuthToken = str
        ApiKey = str

    # =========================================================================
    # API INTEGRATION TYPES - API-specific definitions
    # =========================================================================

    class Api:
        """API integration types - use directly in API methods."""

        # API request data types
        RequestData = str | bytes | dict[str, object] | list[object] | None
        ResponseData = object
        ApiResponse = dict[str, object]

    # =========================================================================
    # HTTP RESPONSE TYPES - Response-specific definitions
    # =========================================================================

    class Response:
        """HTTP response types - use directly without abstraction.

        Use diretamente:
        - object para response data genérica
        - dict[str, object] | list[object] para JSON
        - bytes para content binário
        """

        # Direct HTTP response types
        ResponseData = object
        JsonResponse = (
            dict[str, object] | list[object] | str | int | float | bool | None
        )
        ApiResponse = dict[str, object]  # Alias for tests
        TextResponse = str
        BinaryContent = bytes

        # Response metadata - use directly
        StatusCode = int
        ReasonPhrase = str
        ContentEncoding = str | None

    # =========================================================================
    # HTTP CLIENT TYPES - Client configuration and setup
    # =========================================================================

    class Client:
        """HTTP client types - use directly in configurations.

        Use diretamente nos configs do client:
        - float | tuple[float, float] para timeout
        - int para retries e pool size
        - dict[str, object] para configuração
        """

        # Direct client configuration types
        TimeoutConfig = float | tuple[float, float] | tuple[float, float, float] | None
        RetryCount = int
        ConnectionPoolSize = int
        BackoffFactor = float

        # SSL configuration - use directly
        SslContext = object
        SslVerification = bool | str

        # Client management - use directly
        ClientConfig = dict[str, object]
        ClientConfigDict = dict[str, object]
        ClientInstance = object

    # =========================================================================
    # HTTP PLUGIN TYPES - Plugin system for extensibility
    # =========================================================================

    class Plugin:
        """Plugin system types - use direct callable signatures.

        Use diretamente as signatures dos callbacks:
        - Callable[...] para before_request, after_response, on_error
        - object para plugin instances
        """

        # Direct plugin callback types
        BeforeRequestCallback = Callable[
            [
                str,
                str,
                dict[str, str],
                str | bytes | dict[str, object] | list[object] | None,
            ],
            Awaitable[
                FlextResult[
                    tuple[
                        dict[str, str],
                        str | bytes | dict[str, object] | list[object] | None,
                    ]
                ]
            ],
        ]

        AfterResponseCallback = Callable[
            [object, dict[str, str], int],
            Awaitable[FlextResult[object]],
        ]

        ErrorHandlerCallback = Callable[
            [Exception, str, str],
            Awaitable[FlextResult[object]],
        ]

        # Direct plugin management
        PluginInstance = object
        PluginConfig = dict[str, object]

    # =========================================================================
    # HTTP CACHE TYPES - Caching system definitions
    # =========================================================================

    class Cache:
        """Cache types - use direct types in cache implementations.

        Use diretamente:
        - str para cache keys
        - tuple[object, dict[str, str], int] para cached values
        - int para TTL em segundos
        """

        # Direct cache types
        CacheKey = str
        CacheValue = tuple[object, dict[str, str], int]
        TimeToLive = int

        # Direct storage types
        CacheStorage = Mapping[str, tuple[object, dict[str, str], int]]
        CacheConfig = dict[str, object]

    # =========================================================================
    # HTTP VALIDATION TYPES - Request/response validation
    # =========================================================================

    class HttpValidation:
        """Validation types - use direct validator signatures.

        Use diretamente:
        - Callable[[RequestBody], FlextResult[RequestBody]] para request validators
        - Callable[[object], FlextResult[object]] para response validators
        - FlextResult[T] para validation results
        """

        # Direct validation types
        RequestValidator = Callable[
            [str | bytes | dict[str, object] | list[object] | None],
            FlextResult[str | bytes | dict[str, object] | list[object] | None],
        ]
        ResponseValidator = Callable[[object], FlextResult[object]]
        HeaderValidator = Callable[[dict[str, str]], FlextResult[dict[str, str]]]

        # Direct validation results
        ValidationResult = FlextResult[object]
        ValidationError = str

    # =========================================================================
    # HTTP FACTORY TYPES - Factory and builder patterns
    # =========================================================================

    class Factory:
        """Factory types - use direct factory signatures.

        Use diretamente:
        - Callable[[dict[str, object]], FlextResult[object]] para factories
        - Callable[[Config], FlextResult[Instance]] para builders
        """

        # Direct factory types
        ClientFactory = Callable[[dict[str, object]], FlextResult[object]]
        PluginFactory = Callable[[dict[str, object]], FlextResult[object]]

        # Direct builder types
        RequestBuilder = Callable[
            [dict[str, object]],
            FlextResult[str | bytes | dict[str, object] | list[object] | None],
        ]
        ResponseBuilder = Callable[[object], FlextResult[object]]

    # =============================================================================
    # HTTP PROTOCOLS - Runtime-checkable protocols for type safety
    # =============================================================================

    @runtime_checkable
    class HttpRequestProtocol(Protocol):
        """Protocol for HTTP request objects with type safety."""

        def get_method(self) -> str: ...
        def get_url(self) -> str: ...
        def get_headers(self) -> dict[str, str]: ...
        def get_body(self) -> str | bytes | dict[str, object] | None: ...

    @runtime_checkable
    class HttpResponseProtocol(Protocol):
        """Protocol for HTTP response objects with type safety."""

        def get_status_code(self) -> int: ...
        def get_headers(self) -> dict[str, str]: ...
        def get_data(self) -> object: ...
        def get_json(self) -> dict[str, object] | list[object]: ...

    @runtime_checkable
    class HttpClientConfigProtocol(Protocol):
        """Protocol for HTTP client configuration with type safety."""

        def get(self, key: str, default: object = None) -> object: ...
        def items(self) -> object: ...
        def keys(self) -> object: ...


__all__: list[str] = [
    "FlextApiTypes",
]
