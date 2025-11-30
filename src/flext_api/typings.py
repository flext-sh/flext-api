"""FLEXT API Types - Unified domain-specific type definitions with Clean Architecture.

Single class namespace with NO aliases, NO weak types.
All types consolidated within FlextApiTypes using Python 3.13+ syntax.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Protocol, TypeVar, runtime_checkable

from flext_core import FlextTypes

# TypeVar for generic operations
T = TypeVar("T")
U = TypeVar("U")


class FlextApiTypes(FlextTypes):
    """Unified API type definitions extending FlextTypes with composition.

    Single namespace containing ALL API types.
    NO module-level aliases, NO weak types.
    Python 3.13+ syntax with maximum code reduction.
    Only TypeVar loose outside class.
    """

    # =========================================================================
    # CORE WEB TYPES - Generic HTTP types using Mapping for immutability
    # =========================================================================

    # Direct alias for compatibility
    type JsonValue = FlextTypes.Json.JsonValue

    type JsonObject = dict[str, JsonValue]
    type WebData = str | bytes | JsonObject
    type WebHeaders = dict[str, str | list[str]]
    type WebParams = dict[str, str | list[str]]
    type ResponseList = list[JsonObject]
    type ResponseDict = Mapping[str, JsonValue]

    # =========================================================================
    # HTTP REQUEST/RESPONSE TYPES - Unified request/response types
    # =========================================================================

    type RequestConfig = dict[str, str | int | bool | list[str] | JsonObject]
    type ResponseConfig = dict[str, JsonValue | JsonObject]
    type RequestBody = JsonObject | str | bytes
    type ResponseBody = JsonObject | str | bytes | None
    type HttpResponseDict = dict[str, int | str | dict[str, str] | ResponseBody]
    """HTTP response as dictionary (status_code, headers, body, request_id)."""
    type ValidationResult = dict[str, bool | list[str] | JsonObject]

    # =========================================================================
    # ENDPOINT MANAGEMENT TYPES - Route and endpoint configuration
    # =========================================================================

    type EndpointConfig = dict[str, JsonValue | list[str] | JsonObject]
    type EndpointMetadata = dict[str, str | int | list[str] | JsonObject]
    type RouteConfig = dict[str, str | list[str] | JsonObject]

    type RouteData = dict[
        str,
        str | Callable[..., object] | dict[str, JsonValue] | JsonValue | None,
    ]
    """Route registration data structure."""

    @runtime_checkable
    class ProtocolHandler(Protocol):
        """Protocol handler interface for server registration."""

        def supports_protocol(self, protocol: str) -> bool:
            """Check if handler supports protocol."""
            ...

    # Schema types for GraphQL/OpenAPI
    type SchemaValue = JsonObject | str  # GraphQL schema string or OpenAPI dict

    # =========================================================================
    # AUTHENTICATION TYPES - Auth and security configuration
    # =========================================================================

    type AuthConfig = Mapping[str, str | JsonObject]
    type AuthCredentials = Mapping[str, str | JsonObject]
    type AuthTokenData = Mapping[str, JsonValue | int | bool]
    type SecurityConfig = Mapping[str, bool | str | list[str] | JsonObject]

    # =========================================================================
    # CLIENT TYPES - HTTP client configuration with kwargs
    # =========================================================================

    type ClientConfig = Mapping[str, str | int | JsonObject]
    type ConnectionPool = Mapping[str, int | bool | Mapping[str, int | bool]]
    type TimeoutConfig = Mapping[str, int | float | Mapping[str, int | float]]

    type RequestKwargs = Mapping[
        str,
        Mapping[str, str]
        | Mapping[str, JsonValue]
        | Mapping[str, str | list[str]]
        | float
        | None,
    ]

    # =========================================================================
    # STORAGE & CACHE TYPES - Storage backend configuration and metrics
    # =========================================================================

    type StorageDict = dict[str, str | int | bool | None]
    type CacheDict = dict[str, str | int]
    type MetricsDict = dict[str, int]

    # =========================================================================
    # PROTOCOL & SCHEMA TYPES - Multi-protocol support
    # =========================================================================

    type ProtocolConfig = dict[str, bool | int | str | JsonObject]
    type ProtocolMessage = JsonObject | str | bytes
    type SchemaDefinition = dict[str, JsonValue]
    type ValidationErrors = list[dict[str, str | JsonValue]]

    # =========================================================================
    # SERVICE & PROCESSING TYPES - Service management and pipelines
    # =========================================================================

    type ServiceConfig = dict[str, dict[str, int | float | str]]
    type ServiceHealth = dict[str, bool | str | int]

    type RequestPipeline = list[JsonObject]
    type ResponsePipeline = list[JsonObject]
    type ProcessingResult = dict[str, bool | list[str] | JsonObject]
    # Note: MiddlewareConfig inherited from FlextTypes (dict[str, object])

    # =========================================================================
    # ERROR HANDLING TYPES - Error management and recovery
    # =========================================================================

    type ErrorInfo = dict[str, int | str | JsonObject]
    type ErrorCategory = str
    type ErrorRecovery = dict[str, str | float | JsonObject]
    type RetryStrategy = dict[str, int | float | str]
    type CircuitBreaker = dict[str, bool | int | float | str]

    # =========================================================================
    # NESTED NAMESPACE CLASSES FOR MISSING TYPES
    # =========================================================================

    class RequestData:
        """Placeholder for request data type definitions."""

    class ResponseData:
        """Placeholder for response data type definitions."""

    class Schema:
        """Schema-related types for validation and introspection."""

    class Protocol:
        """Protocol-related types for multi-protocol support."""

    class Transport:
        """Transport-related types for connection management."""

    class Authentication:
        """Authentication-related types for credential management."""

    class Serialization:
        """Serialization-related types.

        Note: SerializationFormat enum moved to FlextApiConstants for consistency.
        """


__all__ = ["FlextApiTypes"]
