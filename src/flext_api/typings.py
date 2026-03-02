"""FLEXT API Types - Unified domain-specific type definitions with Clean Architecture.

Single class namespace with NO aliases, NO weak types.
All types consolidated within FlextApiTypes using Python 3.13+ syntax.

Note: Protocols are in protocols.py, not here. Use p.Api.* for protocols.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from flext_core import FlextTypes
from flext_web import FlextWebTypes


class FlextApiTypes(FlextWebTypes):
    """Unified API type definitions extending t with composition.

    Single namespace containing ALL API types.
    NO module-level aliases, NO weak types.
    Python 3.13+ syntax with maximum code reduction.
    Only TypeVar loose outside class.
    """

    # Core type aliases for forward reference resolution removed per refactoring rules

    class Api:
        """API types namespace for cross-project access.

        Provides organized access to all API types for other FLEXT projects.
        Usage: Other projects can reference `t.Api.RequestData`, `t.Api.ResponseData`, etc.
        This enables consistent namespace patterns for cross-project type access.

        Examples:
            from flext_api import t
            request_data: t.Api.RequestData = ...
            response_data: t.Api.ResponseData = ...

        Note: Namespace composition via inheritance - no aliases needed.
        Access parent namespaces directly through inheritance.

        """

        # =========================================================================
        # CORE WEB TYPES - Generic HTTP types using Mapping for immutability
        # =========================================================================

        # Use parent's JsonValue via inheritance - no alias needed
        # Access via t.JsonValue or use directly from parent

        # Reference to top-level JsonObject for namespace consistency removed
        type WebData = str | bytes | dict[str, FlextTypes.GeneralValueType]
        type WebHeaders = dict[str, str | list[str]]
        type WebParams = dict[str, str | list[str]]
        type ResponseList = list[dict[str, FlextTypes.GeneralValueType]]
        type ResponseDict = Mapping[str, FlextTypes.JsonValue]

        # =========================================================================
        # HTTP REQUEST/RESPONSE TYPES - Unified request/response types
        # =========================================================================

        type RequestConfig = dict[
            str,
            str | int | bool | list[str] | dict[str, FlextTypes.GeneralValueType],
        ]
        type ResponseConfig = dict[
            str, FlextTypes.JsonValue | dict[str, FlextTypes.GeneralValueType]
        ]
        type RequestBody = dict[str, FlextTypes.GeneralValueType] | str | bytes
        type ResponseBody = dict[str, FlextTypes.GeneralValueType] | str | bytes | None
        type HttpResponseDict = dict[
            str,
            int
            | str
            | dict[str, str]
            | dict[str, FlextTypes.GeneralValueType]
            | bytes
            | None,
        ]
        """HTTP response as dictionary (status_code, headers, body, request_id)."""
        type ValidationResult = dict[
            str, bool | list[str] | dict[str, FlextTypes.GeneralValueType]
        ]

        # =========================================================================
        # ENDPOINT MANAGEMENT TYPES - Route and endpoint configuration
        # =========================================================================

        type EndpointConfig = dict[
            str,
            FlextTypes.JsonValue | list[str] | dict[str, FlextTypes.GeneralValueType],
        ]
        type EndpointMetadata = dict[
            str,
            str | int | list[str] | dict[str, FlextTypes.GeneralValueType],
        ]
        type RouteConfig = dict[
            str, str | list[str] | dict[str, FlextTypes.GeneralValueType]
        ]

        type RouteData = dict[
            str,
            str
            | Callable[[], object]
            | dict[str, FlextTypes.JsonValue]
            | FlextTypes.JsonValue
            | None,
        ]
        """Route registration data structure."""

        # Note: ProtocolHandler moved to protocols.py -> p.Api.Server.ProtocolHandler

        # Schema types for GraphQL/OpenAPI
        type SchemaValue = (
            dict[str, FlextTypes.GeneralValueType] | str
        )  # GraphQL schema string or OpenAPI dict

        # =========================================================================
        # AUTHENTICATION TYPES - Auth and security configuration
        # =========================================================================

        type AuthConfig = Mapping[str, str | dict[str, FlextTypes.GeneralValueType]]
        type AuthCredentials = Mapping[
            str, str | dict[str, FlextTypes.GeneralValueType]
        ]
        type AuthTokenData = Mapping[str, FlextTypes.JsonValue | int | bool]
        type SecurityConfig = Mapping[
            str,
            bool | str | list[str] | dict[str, FlextTypes.GeneralValueType],
        ]

        # =========================================================================
        # CLIENT TYPES - HTTP client configuration with kwargs
        # =========================================================================

        type ClientConfig = Mapping[
            str, str | int | dict[str, FlextTypes.GeneralValueType]
        ]
        type ConnectionPool = Mapping[str, int | bool | Mapping[str, int | bool]]
        type TimeoutConfig = Mapping[str, int | float | Mapping[str, int | float]]

        type RequestKwargs = Mapping[
            str,
            Mapping[str, str]
            | Mapping[str, FlextTypes.JsonValue]
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

        type ProtocolConfig = dict[
            str, bool | int | str | dict[str, FlextTypes.GeneralValueType]
        ]
        type ProtocolMessage = dict[str, FlextTypes.GeneralValueType] | str | bytes
        type SchemaDefinition = dict[str, FlextTypes.GeneralValueType]
        type ValidationErrors = list[dict[str, str | FlextTypes.JsonValue]]

        # =========================================================================
        # SERVICE & PROCESSING TYPES - Service management and pipelines
        # =========================================================================

        type ServiceConfig = dict[str, dict[str, int | float | str]]
        type ServiceHealth = dict[str, bool | str | int]

        type RequestPipeline = list[dict[str, FlextTypes.GeneralValueType]]
        type ResponsePipeline = list[dict[str, FlextTypes.GeneralValueType]]
        type ProcessingResult = dict[
            str, bool | list[str] | dict[str, FlextTypes.GeneralValueType]
        ]
        # Note: MiddlewareConfig inherited from t (dict[str, t.GeneralValueType])

        # =========================================================================
        # ERROR HANDLING TYPES - Error management and recovery
        # =========================================================================

        type ErrorInfo = dict[str, int | str | dict[str, FlextTypes.GeneralValueType]]
        type ErrorCategory = str
        type ErrorRecovery = dict[
            str, str | float | dict[str, FlextTypes.GeneralValueType]
        ]
        type RetryStrategy = dict[str, int | float | str]
        type CircuitBreaker = dict[str, bool | int | float | str]


t = FlextApiTypes
__all__ = ["FlextApiTypes", "t"]
