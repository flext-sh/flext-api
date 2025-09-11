"""FLEXT API Types - HTTP-specific type system extending FlextTypes with hierarchical organization.

Unified HTTP type system extending flext-core FlextTypes with HTTP-specific domains
following Python 3.13+ syntax, strict hierarchical organization, and flext-core
foundation patterns for type-safe HTTP operations.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from typing import Protocol, TypeVar, runtime_checkable

from flext_core import FlextResult, FlextTypes

# FlextApiConstants imported when needed to avoid circular imports


class FlextApiTypes(FlextTypes):
    """HTTP API type system extending flext-core FlextTypes with hierarchical organization."""

    # =========================================================================

    # =========================================================================
    class HttpTypeVars:
        """Generic type variables for HTTP components."""

        HttpMethodT = TypeVar("HttpMethodT", bound=str)
        HttpStatusT = TypeVar("HttpStatusT", bound=int)
        RequestBodyT = TypeVar(
            "RequestBodyT", bound="str | bytes | FlextTypes.Core.Dict | None"
        )
        ResponseDataT = TypeVar("ResponseDataT", bound=object)
        PluginT = TypeVar("PluginT", bound=object)

    # =========================================================================
    # HTTP PROTOCOL TYPES - Core HTTP definitions using Python 3.13+ syntax
    # =========================================================================

    class Http:
        """Core HTTP protocol types - use directly without aliases."""

    # Direct type definitions for HTTP protocol
    HttpMethod = str  # Will be constrained by constants at runtime
    HttpStatus = int
    HttpHeaders = dict[str, str]  # HTTP headers as dict
    HeaderValue = str | FlextTypes.Core.StringList
    QueryParameters = dict[str, str | int | float | bool | FlextTypes.Core.StringList]

    # URL components
    HttpUrl = str
    UrlPath = str
    UrlScheme = str  # Will be constrained by constants at runtime
    PortNumber = int

    # =========================================================================
    # HTTP REQUEST TYPES - Request-specific definitions
    # =========================================================================

    class Request:
        """HTTP request types - use directly in code.

        Use diretamente:
        - str | bytes | FlextTypes.Core.Dict | None para request body
        - dict[str, str | int | float | bool] para params
        """

        # Direct HTTP request types
        RequestBody = str | bytes | FlextTypes.Core.Dict | FlextTypes.Core.List | None
        RequestParams = dict[str, str | int | float | bool]
        RequestData = str | bytes | FlextTypes.Core.Dict | FlextTypes.Core.List | None
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
        RequestData = str | bytes | FlextTypes.Core.Dict | FlextTypes.Core.List | None
        ResponseData = object
        ApiResponse = FlextTypes.Core.Dict

    # =========================================================================
    # HTTP RESPONSE TYPES - Response-specific definitions
    # =========================================================================

    class Response:
        """HTTP response types - use directly without abstraction.

        Use diretamente:
        - object para response data genérica
        - FlextTypes.Core.Dict | FlextTypes.Core.List para JSON
        - bytes para content binário
        """

        # Direct HTTP response types
        ResponseData = object
        JsonResponse = (
            FlextTypes.Core.Dict
            | FlextTypes.Core.List
            | str
            | int
            | float
            | bool
            | None
        )
        ApiResponse = FlextTypes.Core.Dict
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
        - FlextTypes.Core.Dict para configuração
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
        ClientConfig = FlextTypes.Core.Dict
        ClientConfigDict = FlextTypes.Core.Dict
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
                FlextTypes.Core.Headers,
                str | bytes | FlextTypes.Core.Dict | FlextTypes.Core.List | None,
            ],
            Awaitable[
                FlextResult[
                    tuple[
                        FlextTypes.Core.Headers,
                        str
                        | bytes
                        | FlextTypes.Core.Dict
                        | FlextTypes.Core.List
                        | None,
                    ]
                ]
            ],
        ]

        AfterResponseCallback = Callable[
            [object, FlextTypes.Core.Headers, int],
            Awaitable[FlextResult[object]],
        ]

        ErrorHandlerCallback = Callable[
            [Exception, str, str],
            Awaitable[FlextResult[object]],
        ]

        # Direct plugin management
        PluginInstance = object
        PluginConfig = FlextTypes.Core.Dict

    # =========================================================================
    # HTTP CACHE TYPES - Caching system definitions
    # =========================================================================

    class Cache:
        """Cache types - use direct types in cache implementations.

        Use diretamente:
        - str para cache keys
        - tuple[object, FlextTypes.Core.Headers, int] para cached values
        - int para TTL em segundos
        """

        # Direct cache types
        CacheKey = str
        CacheValue = tuple[object, FlextTypes.Core.Headers, int]
        TimeToLive = int

        # Direct storage types
        CacheStorage = Mapping[str, tuple[object, FlextTypes.Core.Headers, int]]
        CacheConfig = FlextTypes.Core.Dict

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
            [str | bytes | FlextTypes.Core.Dict | FlextTypes.Core.List | None],
            FlextResult[
                str | bytes | FlextTypes.Core.Dict | FlextTypes.Core.List | None
            ],
        ]
        ResponseValidator = Callable[[object], FlextResult[object]]
        HeaderValidator = Callable[
            [FlextTypes.Core.Headers], FlextResult[FlextTypes.Core.Headers]
        ]

        # Direct validation results
        ValidationResult = FlextResult[object]
        ValidationError = str

    # =========================================================================
    # HTTP FACTORY TYPES - Factory and builder patterns
    # =========================================================================

    class Factory:
        """Factory types - use direct factory signatures.

        Use diretamente:
        - Callable[[FlextTypes.Core.Dict], FlextResult[object]] para factories
        - Callable[[Config], FlextResult[Instance]] para builders
        """

        # Direct factory types
        ClientFactory = Callable[[FlextTypes.Core.Dict], FlextResult[object]]
        PluginFactory = Callable[[FlextTypes.Core.Dict], FlextResult[object]]

        # Direct builder types
        RequestBuilder = Callable[
            [FlextTypes.Core.Dict],
            FlextResult[
                str | bytes | FlextTypes.Core.Dict | FlextTypes.Core.List | None
            ],
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
        def get_headers(self) -> FlextTypes.Core.Headers: ...
        def get_body(self) -> str | bytes | FlextTypes.Core.Dict | None: ...

    @runtime_checkable
    class HttpResponseProtocol(Protocol):
        """Protocol for HTTP response objects with type safety."""

        def get_status_code(self) -> int: ...
        def get_headers(self) -> FlextTypes.Core.Headers: ...
        def get_data(self) -> object: ...
        def get_json(self) -> FlextTypes.Core.Dict | FlextTypes.Core.List: ...

    @runtime_checkable
    class HttpClientConfigProtocol(Protocol):
        """Protocol for HTTP client configuration with type safety."""

        def get(self, key: str, default: object = None) -> object: ...
        def items(self) -> object: ...
        def keys(self) -> object: ...


__all__: FlextTypes.Core.StringList = [
    "FlextApiTypes",
]
