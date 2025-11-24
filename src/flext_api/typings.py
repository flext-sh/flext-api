"""FLEXT API Types - Unified domain-specific type definitions with Clean Architecture.

Single class namespace with NO aliases, NO weak types.
All types consolidated within FlextApiTypes using Python 3.13+ syntax.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import NotRequired

from flext_core import FlextTypes
from typing_extensions import TypedDict

from flext_api.constants import Unit


class FlextApiTypes(FlextTypes):
    """Unified API type definitions with aggressive consolidation.

    Single namespace containing ALL API types.
    NO module-level aliases, NO weak types.
    Python 3.13+ syntax with maximum code reduction.
    """

    # =========================================================================
    # CORE WEB TYPES - Generic HTTP types (use directly everywhere)
    # =========================================================================

    type JsonObject = dict[str, FlextTypes.JsonValue]
    type WebData = str | bytes | JsonObject
    type WebHeaders = dict[str, str | list[str]]
    type WebParams = dict[str, str | list[str]]
    type ResponseList = list[JsonObject]
    type ResponseDict = dict[str, FlextTypes.JsonValue]

    # =========================================================================
    # HTTP REQUEST/RESPONSE TYPES - Unified request/response types
    # =========================================================================

    type RequestConfig = dict[str, str | int | bool | list[str] | JsonObject]
    type ResponseConfig = dict[str, FlextTypes.JsonValue | JsonObject]
    type RequestBody = JsonObject | str | bytes
    type ResponseBody = JsonObject | str | bytes | None
    type ValidationResult = dict[str, bool | list[str] | JsonObject]

    # =========================================================================
    # ENDPOINT MANAGEMENT TYPES - Route and endpoint configuration
    # =========================================================================

    type EndpointConfig = dict[str, FlextTypes.JsonValue | list[str] | JsonObject]
    type EndpointMetadata = dict[str, str | int | list[str] | JsonObject]
    type RouteConfig = dict[str, str | list[str] | JsonObject]

    # =========================================================================
    # AUTHENTICATION TYPES - Auth and security configuration
    # =========================================================================

    type AuthConfig = dict[str, str | JsonObject]
    type AuthCredentials = dict[str, str | JsonObject]
    type AuthTokenData = dict[str, FlextTypes.JsonValue | int | bool]
    type SecurityConfig = dict[str, bool | str | list[str] | JsonObject]

    # =========================================================================
    # CLIENT TYPES - HTTP client configuration with kwargs
    # =========================================================================

    type ClientConfig = dict[str, str | int | JsonObject]
    type ConnectionPool = dict[str, int | bool | dict[str, int | bool]]
    type TimeoutConfig = dict[str, int | float | dict[str, int | float]]

    class RequestKwargs(TypedDict):
        """HTTP request kwargs with modern types."""

        params: NotRequired[dict[str, str] | None]
        data: NotRequired[dict[str, str] | None]
        json: NotRequired[dict[str, FlextTypes.JsonValue] | None]
        headers: NotRequired[dict[str, str | list[str]] | None]
        timeout: NotRequired[float | None]

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
    type SchemaDefinition = dict[str, FlextTypes.JsonValue]
    type ValidationErrors = list[dict[str, str | FlextTypes.JsonValue]]

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


__all__ = ["FlextApiTypes", "Unit"]
