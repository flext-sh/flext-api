"""FLEXT API Types - Unified domain-specific type definitions with Clean Architecture.

Single class namespace with NO aliases, NO weak types.
All types consolidated within FlextApiTypes using Python 3.13+ syntax.

Note: Protocols are in protocols.py, not here. Use p.Api.* for protocols.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Literal

from flext_cli import FlextCliProtocols, FlextCliTypes, u

from flext_api._typings.serialization import FlextApiTypingsSerialization
from flext_web import FlextWebTypes


class FlextApiTypes(FlextWebTypes, FlextCliTypes):
    """Unified API type definitions extending t with composition."""

    class Api(FlextApiTypingsSerialization):
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
        type WebhookDeliveryStatus = Literal[
            "delivered",
            "delivered_after_retry",
            "failed",
        ]
        type WebhookAlgorithm = Literal["sha256", "sha512"]
        type WebhookHandler = Callable[
            [FlextWebTypes.ContainerValueMapping],
            FlextWebTypes.ContainerValue | FlextCliProtocols.ResultLike[bool] | None,
        ]
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
        CONTAINER_VALUE_ADAPTER: u.TypeAdapter[FlextWebTypes.ContainerValue] = (
            u.TypeAdapter(
                FlextWebTypes.ContainerValue,
            )
        )
        API_JSON_VALUE_ADAPTER: u.TypeAdapter[FlextWebTypes.ApiJsonValue] = (
            u.TypeAdapter(
                FlextWebTypes.ApiJsonValue,
            )
        )
        BINARY_CONTENT_ADAPTER: u.TypeAdapter[FlextWebTypes.BinaryContent] = (
            u.TypeAdapter(
                FlextWebTypes.BinaryContent,
            )
        )
        STR_MAPPING_ADAPTER: u.TypeAdapter[FlextWebTypes.StrMapping] = u.TypeAdapter(
            FlextWebTypes.StrMapping,
        )
        HOSTNAME_ADAPTER: u.TypeAdapter[FlextWebTypes.HostnameStr] = u.TypeAdapter(
            FlextWebTypes.HostnameStr,
        )
        PORT_NUMBER_ADAPTER: u.TypeAdapter[FlextWebTypes.PortNumber] = u.TypeAdapter(
            FlextWebTypes.PortNumber,
        )
        STRING_ADAPTER: u.TypeAdapter[FlextWebTypes.TextValue] = u.TypeAdapter(
            FlextWebTypes.TextValue,
        )
        INTEGER_ADAPTER: u.TypeAdapter[FlextWebTypes.IntegerValue] = u.TypeAdapter(
            FlextWebTypes.IntegerValue,
        )
        FLOAT_ADAPTER: u.TypeAdapter[FlextWebTypes.FloatValue] = u.TypeAdapter(
            FlextWebTypes.FloatValue,
        )
        STORAGE_ENTRY_ADAPTER: u.TypeAdapter[
            Mapping[str, FlextWebTypes.ApiJsonValue]
        ] = u.TypeAdapter(
            Mapping[str, FlextWebTypes.ApiJsonValue],
        )
        REQUEST_BODY_ADAPTER: u.TypeAdapter[RequestBody] = u.TypeAdapter(
            RequestBody,
        )

        RESPONSE_BODY_ADAPTER: u.TypeAdapter[ResponseBody] = u.TypeAdapter(
            ResponseBody,
        )
        DICT_BODY_ADAPTER: u.TypeAdapter[FlextWebTypes.ContainerValueMapping] = (
            u.TypeAdapter(
                FlextWebTypes.ContainerValueMapping,
            )
        )

        JSON_HEADERS_ADAPTER: u.TypeAdapter[FlextWebTypes.ContainerValueMapping] = (
            u.TypeAdapter(
                FlextWebTypes.ContainerValueMapping,
            )
        )


t = FlextApiTypes
__all__: list[str] = ["FlextApiTypes", "t"]
