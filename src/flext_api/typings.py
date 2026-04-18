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

from flext_cli import p, t, u

from flext_api import FlextApiTypingsSerialization
from flext_web import FlextWebTypes


class FlextApiTypes(t, FlextWebTypes):
    """Unified API type definitions extending t with composition."""

    class Api(FlextApiTypingsSerialization):
        """API types namespace for cross-project access."""

        type WebHeaders = Mapping[str, t.Scalar | t.StrSequence]
        type WebParamValue = str | t.StrSequence
        type WebParams = Mapping[str, WebParamValue]
        type RequestBody = t.ContainerValueMapping | str | t.BinaryContent
        type ResponseBody = t.ContainerValueMapping | str | t.BinaryContent | None
        type HttpResponseDict = Mapping[
            str,
            t.ContainerValue | t.StrMapping | t.BinaryContent | None,
        ]
        "HTTP response as dictionary (status_code, headers, body, request_id)."
        type RouteData = Mapping[
            str,
            t.ContainerValue
            | t.ResourceCallable
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
            [t.ContainerValueMapping],
            t.ContainerValue | p.ResultLike[bool] | None,
        ]
        type RequestKwargs = Mapping[
            str,
            t.StrMapping
            | Mapping[str, t.ContainerValue]
            | Mapping[str, t.Scalar | t.StrSequence]
            | float
            | None,
        ]
        type StorageDict = Mapping[str, t.OptionalPrimitive]
        type CacheDict = Mapping[str, t.Primitives]
        CONTAINER_VALUE_ADAPTER: u.TypeAdapter[t.ContainerValue] = u.TypeAdapter(
            t.ContainerValue,
        )
        API_JSON_VALUE_ADAPTER: u.TypeAdapter[t.ApiJsonValue] = u.TypeAdapter(
            t.ApiJsonValue,
        )
        BINARY_CONTENT_ADAPTER: u.TypeAdapter[t.BinaryContent] = u.TypeAdapter(
            t.BinaryContent,
        )
        STR_MAPPING_ADAPTER: u.TypeAdapter[t.StrMapping] = u.TypeAdapter(
            t.StrMapping,
        )
        HOSTNAME_ADAPTER: u.TypeAdapter[t.HostnameStr] = u.TypeAdapter(
            t.HostnameStr,
        )
        PORT_NUMBER_ADAPTER: u.TypeAdapter[t.PortNumber] = u.TypeAdapter(
            t.PortNumber,
        )
        STRING_ADAPTER: u.TypeAdapter[t.TextValue] = u.TypeAdapter(
            t.TextValue,
        )
        INTEGER_ADAPTER: u.TypeAdapter[t.IntegerValue] = u.TypeAdapter(
            t.IntegerValue,
        )
        FLOAT_ADAPTER: u.TypeAdapter[t.FloatValue] = u.TypeAdapter(
            t.FloatValue,
        )
        STORAGE_ENTRY_ADAPTER: u.TypeAdapter[Mapping[str, t.ApiJsonValue]] = (
            u.TypeAdapter(
                Mapping[str, t.ApiJsonValue],
            )
        )
        REQUEST_BODY_ADAPTER: u.TypeAdapter[RequestBody] = u.TypeAdapter(
            RequestBody,
        )

        RESPONSE_BODY_ADAPTER: u.TypeAdapter[ResponseBody] = u.TypeAdapter(
            ResponseBody,
        )
        DICT_BODY_ADAPTER: u.TypeAdapter[t.ContainerValueMapping] = u.TypeAdapter(
            t.ContainerValueMapping,
        )

        JSON_HEADERS_ADAPTER: u.TypeAdapter[t.ContainerValueMapping] = u.TypeAdapter(
            t.ContainerValueMapping,
        )


t = FlextApiTypes

__all__: list[str] = ["FlextApiTypes", "t"]
