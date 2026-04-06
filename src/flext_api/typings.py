"""FLEXT API Types - Unified domain-specific type definitions with Clean Architecture.

Single class namespace with NO aliases, NO weak types.
All types consolidated within FlextApiTypes using Python 3.13+ syntax.

Note: Protocols are in protocols.py, not here. Use p.Api.* for protocols.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from flext_cli import FlextCliTypes
from pydantic import TypeAdapter

from flext_web import FlextWebTypes


class FlextApiTypes(FlextWebTypes, FlextCliTypes):
    """Unified API type definitions extending t with composition."""

    class Api:
        """API types namespace for cross-project access."""

        type WebHeaders = Mapping[str, FlextWebTypes.Scalar | FlextWebTypes.StrSequence]
        type WebParamValue = str | FlextWebTypes.StrSequence
        type WebParams = Mapping[str, WebParamValue]
        type RequestBody = (
            FlextWebTypes.ContainerValueMapping | str | FlextWebTypes.BinaryContent
        )
        type ResponseBody = (
            FlextWebTypes.ContainerValueMapping
            | str
            | FlextWebTypes.BinaryContent
            | None
        )
        type HttpResponseDict = Mapping[
            str,
            FlextWebTypes.ContainerValue
            | FlextWebTypes.StrMapping
            | FlextWebTypes.BinaryContent
            | None,
        ]
        "HTTP response as dictionary (status_code, headers, body, request_id)."
        type RouteData = Mapping[
            str,
            FlextWebTypes.ContainerValue
            | FlextWebTypes.ResourceCallable
            | Callable[..., FlextApiTypes.Api.HttpResponseDict | str | None]
            | None,
        ]
        "Route registration data structure."
        type RequestKwargs = Mapping[
            str,
            FlextWebTypes.StrMapping
            | Mapping[str, FlextWebTypes.ContainerValue]
            | Mapping[str, FlextWebTypes.Scalar | FlextWebTypes.StrSequence]
            | float
            | None,
        ]
        type StorageDict = Mapping[str, FlextWebTypes.OptionalPrimitive]
        type CacheDict = Mapping[str, FlextWebTypes.Primitives]
        CONTAINER_VALUE_ADAPTER: TypeAdapter[FlextWebTypes.ContainerValue] = (
            TypeAdapter(
                FlextWebTypes.ContainerValue,
            )
        )
        API_JSON_VALUE_ADAPTER: TypeAdapter[FlextWebTypes.ApiJsonValue] = TypeAdapter(
            FlextWebTypes.ApiJsonValue,
        )
        BINARY_CONTENT_ADAPTER: TypeAdapter[FlextWebTypes.BinaryContent] = TypeAdapter(
            FlextWebTypes.BinaryContent,
        )
        STR_MAPPING_ADAPTER: TypeAdapter[FlextWebTypes.StrMapping] = TypeAdapter(
            FlextWebTypes.StrMapping,
        )
        HOSTNAME_ADAPTER: TypeAdapter[FlextWebTypes.HostnameStr] = TypeAdapter(
            FlextWebTypes.HostnameStr,
        )
        PORT_NUMBER_ADAPTER: TypeAdapter[FlextWebTypes.PortNumber] = TypeAdapter(
            FlextWebTypes.PortNumber,
        )
        STRING_ADAPTER: TypeAdapter[FlextWebTypes.TextValue] = TypeAdapter(
            FlextWebTypes.TextValue,
        )
        INTEGER_ADAPTER: TypeAdapter[FlextWebTypes.IntegerValue] = TypeAdapter(
            FlextWebTypes.IntegerValue,
        )
        FLOAT_ADAPTER: TypeAdapter[FlextWebTypes.FloatValue] = TypeAdapter(
            FlextWebTypes.FloatValue,
        )
        STORAGE_ENTRY_ADAPTER: TypeAdapter[Mapping[str, FlextWebTypes.ApiJsonValue]] = (
            TypeAdapter(
                Mapping[str, FlextWebTypes.ApiJsonValue],
            )
        )
        REQUEST_BODY_ADAPTER: TypeAdapter[RequestBody] = TypeAdapter(
            RequestBody,
        )

        RESPONSE_BODY_ADAPTER: TypeAdapter[ResponseBody] = TypeAdapter(
            ResponseBody,
        )
        DICT_BODY_ADAPTER: TypeAdapter[FlextWebTypes.ContainerValueMapping] = (
            TypeAdapter(
                FlextWebTypes.ContainerValueMapping,
            )
        )

        JSON_HEADERS_ADAPTER: TypeAdapter[FlextWebTypes.ContainerValueMapping] = (
            TypeAdapter(
                FlextWebTypes.ContainerValueMapping,
            )
        )


t = FlextApiTypes
__all__ = ["FlextApiTypes", "t"]
