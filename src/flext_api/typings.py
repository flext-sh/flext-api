"""FLEXT API Types - Unified domain-specific type definitions with Clean Architecture.

Single class namespace with NO aliases, NO weak types.
All types consolidated within FlextApiTypes using Python 3.13+ syntax.

Note: Protocols are in protocols.py, not here. Use p.Api.* for protocols.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence

from flext_core import FlextTypes


class FlextApiTypes(FlextTypes):
    """Unified API type definitions extending t with composition.

    Single namespace containing ALL API types.
    NO module-level aliases, NO weak types.
    Python 3.13+ syntax with maximum code reduction.
    Only TypeVar loose outside class.
    """

    # Class-level forwarding aliases (canonical definitions in Api namespace)
    type Pair[LeftT, RightT] = tuple[LeftT, RightT]
    type Triple[FirstT, SecondT, ThirdT] = tuple[FirstT, SecondT, ThirdT]
    type VariadicTuple[ItemT] = tuple[ItemT, ...]
    type IntPair = Pair[int, int]
    type JsonObject = Mapping[str, FlextTypes.ContainerValue]
    type ApiJsonValue = FlextTypes.ContainerValue | None

    class Api:
        """API types namespace for cross-project access.

        Provides organized access to all API types for other FLEXT projects.
        Usage: Other projects can reference `FlextTypes.Api.RequestData`, `FlextTypes.Api.ResponseData`, etc.
        This enables consistent namespace patterns for cross-project type access.

        Examples:
            from flext_api import t
            request_data: FlextTypes.Api.RequestData = ...
            response_data: FlextTypes.Api.ResponseData = ...

        Note: Namespace composition via inheritance - no aliases needed.
        Access parent namespaces directly through inheritance.

        """

        type WebData = FlextTypes.FileContent | Mapping[str, FlextTypes.ContainerValue]
        type WebHeaders = Mapping[str, FlextTypes.Scalar | FlextTypes.StrSequence]
        type WebParamValue = str | FlextTypes.StrSequence
        type WebParams = Mapping[str, WebParamValue]
        type ResponseList = Sequence[Mapping[str, FlextTypes.ContainerValue]]
        type ResponseDict = Mapping[str, FlextTypes.ContainerValue]
        type RequestConfig = Mapping[str, FlextTypes.ContainerValue]
        type ResponseConfig = Mapping[str, FlextTypes.ContainerValue]
        type RequestBody = Mapping[str, FlextTypes.ContainerValue] | str | bytes
        type ResponseBody = Mapping[str, FlextTypes.ContainerValue] | str | bytes | None
        type HttpResponseDict = Mapping[
            str,
            FlextTypes.ContainerValue | FlextTypes.StrMapping | bytes | None,
        ]
        "HTTP response as dictionary (status_code, headers, body, request_id)."
        type ValidationResult = Mapping[str, FlextTypes.ContainerValue]
        type EndpointConfig = Mapping[str, FlextTypes.ContainerValue]
        type EndpointMetadata = Mapping[str, FlextTypes.ContainerValue]
        type RouteConfig = Mapping[str, FlextTypes.ContainerValue]
        type RouteData = Mapping[
            str,
            FlextTypes.ContainerValue
            | FlextTypes.ResourceCallable
            | Callable[..., FlextApiTypes.Api.HttpResponseDict | str | None]
            | None,
        ]
        "Route registration data structure."
        type SchemaValue = Mapping[str, FlextTypes.ContainerValue] | str
        type AuthConfig = Mapping[str, FlextTypes.ContainerValue]
        type AuthCredentials = Mapping[str, FlextTypes.ContainerValue]
        type AuthTokenData = Mapping[str, FlextTypes.ContainerValue]
        type SecurityConfig = Mapping[str, FlextTypes.ContainerValue]
        type ClientConfig = Mapping[str, FlextTypes.ContainerValue]
        type ConnectionPool = Mapping[
            str,
            FlextTypes.Primitives | Mapping[str, FlextTypes.Primitives],
        ]
        type TimeoutConfig = Mapping[
            str,
            FlextTypes.Scalar | Mapping[str, FlextTypes.Scalar],
        ]
        type RequestKwargs = Mapping[
            str,
            FlextTypes.StrMapping
            | Mapping[str, FlextTypes.ContainerValue]
            | Mapping[str, FlextTypes.Scalar | FlextTypes.StrSequence]
            | float
            | None,
        ]
        type StorageDict = Mapping[str, FlextTypes.Primitives | None]
        type CacheDict = Mapping[str, FlextTypes.Primitives]
        type MetricsDict = Mapping[str, int]
        type ProtocolConfig = Mapping[str, FlextTypes.ContainerValue]
        type ProtocolMessage = Mapping[str, FlextTypes.ContainerValue] | str | bytes
        type SchemaDefinition = Mapping[str, FlextTypes.ContainerValue]
        type ValidationErrors = Sequence[Mapping[str, FlextTypes.ContainerValue]]
        type ServiceConfig = Mapping[str, Mapping[str, FlextTypes.Scalar]]
        type ServiceHealth = Mapping[str, FlextTypes.Primitives]
        type RequestPipeline = Sequence[Mapping[str, FlextTypes.ContainerValue]]
        type ResponsePipeline = Sequence[Mapping[str, FlextTypes.ContainerValue]]
        type ProcessingResult = Mapping[str, FlextTypes.ContainerValue]
        type ErrorInfo = Mapping[str, FlextTypes.ContainerValue]
        type ErrorCategory = str
        type ErrorRecovery = Mapping[str, FlextTypes.ContainerValue]
        type RetryStrategy = Mapping[str, FlextTypes.Scalar]
        type CircuitBreaker = Mapping[str, FlextTypes.Primitives]


t = FlextApiTypes
__all__ = ["FlextApiTypes", "t"]
