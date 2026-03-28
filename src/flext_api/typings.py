"""FLEXT API Types - Unified domain-specific type definitions with Clean Architecture.

Single class namespace with NO aliases, NO weak types.
All types consolidated within FlextApiTypes using Python 3.13+ syntax.

Note: Protocols are in protocols.py, not here. Use p.Api.* for protocols.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence

from flext_web import FlextWebTypes


class FlextApiTypes(FlextWebTypes):
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
    type JsonObject = Mapping[str, FlextWebTypes.ContainerValue]
    type ApiJsonValue = FlextWebTypes.ContainerValue | None

    class Api:
        """API types namespace for cross-project access.

        Provides organized access to all API types for other FLEXT projects.
        Usage: Other projects can reference `FlextWebTypes.Api.RequestData`, `FlextWebTypes.Api.ResponseData`, etc.
        This enables consistent namespace patterns for cross-project type access.

        Examples:
            from flext_api import t
            request_data: FlextWebTypes.Api.RequestData = ...
            response_data: FlextWebTypes.Api.ResponseData = ...

        Note: Namespace composition via inheritance - no aliases needed.
        Access parent namespaces directly through inheritance.

        """

        type WebData = (
            FlextWebTypes.FileContent | Mapping[str, FlextWebTypes.ContainerValue]
        )
        type WebHeaders = Mapping[str, FlextWebTypes.Scalar | FlextWebTypes.StrSequence]
        type WebParamValue = str | FlextWebTypes.StrSequence
        type WebParams = Mapping[str, WebParamValue]
        type ResponseList = Sequence[Mapping[str, FlextWebTypes.ContainerValue]]
        type ResponseDict = Mapping[str, FlextWebTypes.ContainerValue]
        type RequestConfig = Mapping[str, FlextWebTypes.ContainerValue]
        type ResponseConfig = Mapping[str, FlextWebTypes.ContainerValue]
        type RequestBody = Mapping[str, FlextWebTypes.ContainerValue] | str | bytes
        type ResponseBody = (
            Mapping[str, FlextWebTypes.ContainerValue] | str | bytes | None
        )
        type HttpResponseDict = Mapping[
            str,
            FlextWebTypes.ContainerValue | FlextWebTypes.StrMapping | bytes | None,
        ]
        "HTTP response as dictionary (status_code, headers, body, request_id)."
        type ValidationResult = Mapping[str, FlextWebTypes.ContainerValue]
        type EndpointConfig = Mapping[str, FlextWebTypes.ContainerValue]
        type EndpointMetadata = Mapping[str, FlextWebTypes.ContainerValue]
        type RouteConfig = Mapping[str, FlextWebTypes.ContainerValue]
        type RouteData = Mapping[
            str,
            FlextWebTypes.ContainerValue
            | FlextWebTypes.ResourceCallable
            | Callable[..., FlextApiTypes.Api.HttpResponseDict | str | None]
            | None,
        ]
        "Route registration data structure."
        type SchemaValue = Mapping[str, FlextWebTypes.ContainerValue] | str
        type AuthConfig = Mapping[str, FlextWebTypes.ContainerValue]
        type AuthCredentials = Mapping[str, FlextWebTypes.ContainerValue]
        type AuthTokenData = Mapping[str, FlextWebTypes.ContainerValue]
        type SecurityConfig = Mapping[str, FlextWebTypes.ContainerValue]
        type ClientConfig = Mapping[str, FlextWebTypes.ContainerValue]
        type ConnectionPool = Mapping[
            str,
            FlextWebTypes.Primitives | Mapping[str, FlextWebTypes.Primitives],
        ]
        type TimeoutConfig = Mapping[
            str,
            FlextWebTypes.Scalar | Mapping[str, FlextWebTypes.Scalar],
        ]
        type RequestKwargs = Mapping[
            str,
            FlextWebTypes.StrMapping
            | Mapping[str, FlextWebTypes.ContainerValue]
            | Mapping[str, FlextWebTypes.Scalar | FlextWebTypes.StrSequence]
            | float
            | None,
        ]
        type StorageDict = Mapping[str, FlextWebTypes.Primitives | None]
        type CacheDict = Mapping[str, FlextWebTypes.Primitives]
        type MetricsDict = Mapping[str, int]
        type ProtocolConfig = Mapping[str, FlextWebTypes.ContainerValue]
        type ProtocolMessage = Mapping[str, FlextWebTypes.ContainerValue] | str | bytes
        type SchemaDefinition = Mapping[str, FlextWebTypes.ContainerValue]
        type ValidationErrors = Sequence[Mapping[str, FlextWebTypes.ContainerValue]]
        type ServiceConfig = Mapping[str, Mapping[str, FlextWebTypes.Scalar]]
        type ServiceHealth = Mapping[str, FlextWebTypes.Primitives]
        type RequestPipeline = Sequence[Mapping[str, FlextWebTypes.ContainerValue]]
        type ResponsePipeline = Sequence[Mapping[str, FlextWebTypes.ContainerValue]]
        type ProcessingResult = Mapping[str, FlextWebTypes.ContainerValue]
        type ErrorInfo = Mapping[str, FlextWebTypes.ContainerValue]
        type ErrorCategory = str
        type ErrorRecovery = Mapping[str, FlextWebTypes.ContainerValue]
        type RetryStrategy = Mapping[str, FlextWebTypes.Scalar]
        type CircuitBreaker = Mapping[str, FlextWebTypes.Primitives]


t = FlextApiTypes
__all__ = ["FlextApiTypes", "t"]
