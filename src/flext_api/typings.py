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

    type JsonObject = dict[str, FlextTypes.ContainerValue]
    type ApiJsonValue = FlextTypes.ContainerValue

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

        type JsonObject = dict[str, FlextTypes.ContainerValue]
        type ApiJsonValue = FlextTypes.ContainerValue
        type WebData = str | bytes | dict[str, FlextTypes.ContainerValue]
        type WebHeaders = dict[str, str | list[str]]
        type WebParams = dict[str, str | list[str]]
        type ResponseList = list[dict[str, FlextTypes.ContainerValue]]
        type ResponseDict = Mapping[str, FlextTypes.ContainerValue]
        type RequestConfig = dict[
            str, str | int | bool | list[str] | dict[str, FlextTypes.ContainerValue]
        ]
        type ResponseConfig = dict[
            str, FlextTypes.ContainerValue | dict[str, FlextTypes.ContainerValue]
        ]
        type RequestBody = dict[str, FlextTypes.ContainerValue] | str | bytes
        type ResponseBody = dict[str, FlextTypes.ContainerValue] | str | bytes | None
        type HttpResponseDict = dict[
            str,
            int
            | str
            | dict[str, str]
            | dict[str, FlextTypes.ContainerValue]
            | bytes
            | None,
        ]
        "HTTP response as dictionary (status_code, headers, body, request_id)."
        type ValidationResult = dict[
            str, bool | list[str] | dict[str, FlextTypes.ContainerValue]
        ]
        type EndpointConfig = dict[
            str,
            FlextTypes.ContainerValue
            | list[str]
            | dict[str, FlextTypes.ContainerValue],
        ]
        type EndpointMetadata = dict[
            str, str | int | list[str] | dict[str, FlextTypes.ContainerValue]
        ]
        type RouteConfig = dict[
            str, str | list[str] | dict[str, FlextTypes.ContainerValue]
        ]
        type RouteData = dict[
            str,
            str
            | Callable[[], object]
            | dict[str, FlextTypes.ContainerValue]
            | FlextTypes.ContainerValue
            | None,
        ]
        "Route registration data structure."
        type SchemaValue = dict[str, FlextTypes.ContainerValue] | str
        type AuthConfig = Mapping[str, str | dict[str, FlextTypes.ContainerValue]]
        type AuthCredentials = Mapping[str, str | dict[str, FlextTypes.ContainerValue]]
        type AuthTokenData = Mapping[str, FlextTypes.ContainerValue | int | bool]
        type SecurityConfig = Mapping[
            str, bool | str | list[str] | dict[str, FlextTypes.ContainerValue]
        ]
        type ClientConfig = Mapping[
            str, str | int | dict[str, FlextTypes.ContainerValue]
        ]
        type ConnectionPool = Mapping[str, int | bool | Mapping[str, int | bool]]
        type TimeoutConfig = Mapping[str, int | float | Mapping[str, int | float]]
        type RequestKwargs = Mapping[
            str,
            Mapping[str, str]
            | Mapping[str, FlextTypes.ContainerValue]
            | Mapping[str, str | list[str]]
            | float
            | None,
        ]
        type StorageDict = dict[str, str | int | bool | None]
        type CacheDict = dict[str, str | int]
        type MetricsDict = dict[str, int]
        type ProtocolConfig = dict[
            str, bool | int | str | dict[str, FlextTypes.ContainerValue]
        ]
        type ProtocolMessage = dict[str, FlextTypes.ContainerValue] | str | bytes
        type SchemaDefinition = dict[str, FlextTypes.ContainerValue]
        type ValidationErrors = list[dict[str, str | FlextTypes.ContainerValue]]
        type ServiceConfig = dict[str, dict[str, int | float | str]]
        type ServiceHealth = dict[str, bool | str | int]
        type RequestPipeline = list[dict[str, FlextTypes.ContainerValue]]
        type ResponsePipeline = list[dict[str, FlextTypes.ContainerValue]]
        type ProcessingResult = dict[
            str, bool | list[str] | dict[str, FlextTypes.ContainerValue]
        ]
        type ErrorInfo = dict[str, int | str | dict[str, FlextTypes.ContainerValue]]
        type ErrorCategory = str
        type ErrorRecovery = dict[
            str, str | float | dict[str, FlextTypes.ContainerValue]
        ]
        type RetryStrategy = dict[str, int | float | str]
        type CircuitBreaker = dict[str, bool | int | float | str]


t = FlextApiTypes
__all__ = ["FlextApiTypes", "t"]
