"""FLEXT API Types - Unified domain-specific type definitions with Clean Architecture.

Single class namespace with NO aliases, NO weak types.
All types consolidated within FlextApiTypes using Python 3.13+ syntax.

Note: Protocols are in protocols.py, not here. Use p.Api.* for protocols.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping

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
        type WebData = FlextTypes.FileContent | dict[str, FlextTypes.ContainerValue]
        type WebHeaders = dict[str, FlextTypes.Scalar | list[str]]
        type WebParamValue = str | list[str]
        type WebParams = dict[str, WebParamValue]
        type ResponseList = list[dict[str, FlextTypes.ContainerValue]]
        type ResponseDict = Mapping[str, FlextTypes.ContainerValue]
        type RequestConfig = dict[
            str,
            FlextTypes.Primitives | list[str] | dict[str, FlextTypes.ContainerValue],
        ]
        type ResponseConfig = dict[
            str, FlextTypes.ContainerValue | dict[str, FlextTypes.ContainerValue]
        ]
        type RequestBody = dict[str, FlextTypes.ContainerValue] | str | bytes
        type ResponseBody = dict[str, FlextTypes.ContainerValue] | str | bytes | None
        type HttpResponseDict = dict[
            str,
            FlextTypes.Primitives
            | dict[str, str]
            | dict[str, FlextTypes.ContainerValue]
            | bytes
            | None,
        ]
        "HTTP response as dictionary (status_code, headers, body, request_id)."
        type ValidationResult = dict[
            str,
            FlextTypes.Primitives | list[str] | dict[str, FlextTypes.ContainerValue],
        ]
        type EndpointConfig = dict[
            str,
            FlextTypes.ContainerValue
            | list[str]
            | dict[str, FlextTypes.ContainerValue],
        ]
        type EndpointMetadata = dict[
            str,
            FlextTypes.Primitives | list[str] | dict[str, FlextTypes.ContainerValue],
        ]
        type RouteConfig = dict[
            str, FlextTypes.Scalar | list[str] | dict[str, FlextTypes.ContainerValue]
        ]
        type RouteData = dict[
            str,
            str
            | FlextTypes.ResourceCallable
            | dict[str, FlextTypes.ContainerValue]
            | FlextTypes.ContainerValue
            | None,
        ]
        "Route registration data structure."
        type SchemaValue = dict[str, FlextTypes.ContainerValue] | str
        type AuthConfig = Mapping[
            str, FlextTypes.Scalar | dict[str, FlextTypes.ContainerValue]
        ]
        type AuthCredentials = Mapping[
            str, FlextTypes.Scalar | dict[str, FlextTypes.ContainerValue]
        ]
        type AuthTokenData = Mapping[str, FlextTypes.ContainerValue]
        type SecurityConfig = Mapping[
            str,
            FlextTypes.Primitives | list[str] | dict[str, FlextTypes.ContainerValue],
        ]
        type ClientConfig = Mapping[
            str, FlextTypes.Primitives | dict[str, FlextTypes.ContainerValue]
        ]
        type ConnectionPool = Mapping[
            str, FlextTypes.Primitives | Mapping[str, FlextTypes.Primitives]
        ]
        type TimeoutConfig = Mapping[
            str, FlextTypes.Scalar | Mapping[str, FlextTypes.Scalar]
        ]
        type RequestKwargs = Mapping[
            str,
            Mapping[str, str]
            | Mapping[str, FlextTypes.ContainerValue]
            | Mapping[str, FlextTypes.Scalar | list[str]]
            | float
            | None,
        ]
        type StorageDict = dict[str, FlextTypes.Primitives | None]
        type CacheDict = dict[str, FlextTypes.Primitives]
        type MetricsDict = dict[str, int]
        type ProtocolConfig = dict[
            str, FlextTypes.Primitives | dict[str, FlextTypes.ContainerValue]
        ]
        type ProtocolMessage = dict[str, FlextTypes.ContainerValue] | str | bytes
        type SchemaDefinition = dict[str, FlextTypes.ContainerValue]
        type ValidationErrors = list[dict[str, FlextTypes.ContainerValue]]
        type ServiceConfig = dict[str, dict[str, FlextTypes.Scalar]]
        type ServiceHealth = dict[str, FlextTypes.Primitives]
        type RequestPipeline = list[dict[str, FlextTypes.ContainerValue]]
        type ResponsePipeline = list[dict[str, FlextTypes.ContainerValue]]
        type ProcessingResult = dict[
            str,
            FlextTypes.Primitives | list[str] | dict[str, FlextTypes.ContainerValue],
        ]
        type ErrorInfo = dict[
            str, FlextTypes.Primitives | dict[str, FlextTypes.ContainerValue]
        ]
        type ErrorCategory = str
        type ErrorRecovery = dict[
            str, FlextTypes.Scalar | dict[str, FlextTypes.ContainerValue]
        ]
        type RetryStrategy = dict[str, FlextTypes.Scalar]
        type CircuitBreaker = dict[str, FlextTypes.Primitives]


t = FlextApiTypes
__all__ = ["FlextApiTypes", "t"]
