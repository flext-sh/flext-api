"""FLEXT API Types - Unified domain-specific type definitions with Clean Architecture.

from flext_core import FlextTypes as Types

Single class namespace with NO aliases, NO weak types.
All types consolidated within FlextApiTypes using Python 3.13+ syntax.

Note: Protocols are in protocols.py, not here. Use p.Api.* for protocols.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import (
    Callable,
    Mapping,
)
from typing import Literal

from flext_cli import p, t, u
from flext_web import FlextWebTypes

from flext_api import FlextApiTypingsSerialization


class FlextApiTypes(FlextWebTypes):
    """Unified API type definitions extending t with composition."""

    class Api(FlextApiTypingsSerialization):
        """API types namespace for cross-project access."""

        type WebHeaders = t.ScalarOrStrSequenceMapping
        type WebParams = Mapping[str, str | t.StrSequence]
        type RequestBody = t.JsonMapping | str | t.StrictBytes
        type ResponseBody = t.JsonMapping | str | t.StrictBytes | None
        type HttpResponseDict = Mapping[
            str,
            t.JsonValue | t.StrMapping | t.JsonMapping | t.StrictBytes | None,
        ]
        "HTTP response as dictionary (status_code, headers, body, request_id)."
        type RouteData = Mapping[
            str,
            t.JsonValue
            | t.ConfigurationMapping
            | t.JsonMapping
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
            [t.JsonMapping],
            t.JsonValue | p.ResultLike[bool] | None,
        ]
        type RequestKwargs = Mapping[
            str,
            t.StrMapping | t.JsonMapping | t.ScalarOrStrSequenceMapping | float | None,
        ]
        type CacheDict = Mapping[str, t.Primitives]
        CONTAINER_VALUE_ADAPTER: u.TypeAdapter[t.JsonValue] = u.TypeAdapter(
            t.JsonValue,
        )
        API_JSON_VALUE_ADAPTER: u.TypeAdapter[t.JsonValue] = u.TypeAdapter(
            t.JsonValue,
        )
        BINARY_CONTENT_ADAPTER: u.TypeAdapter[t.StrictBytes] = u.TypeAdapter(
            t.StrictBytes,
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
        STRING_ADAPTER: u.TypeAdapter[t.StrictStr] = u.TypeAdapter(
            t.StrictStr,
        )
        INTEGER_ADAPTER: u.TypeAdapter[t.StrictInt] = u.TypeAdapter(
            t.StrictInt,
        )
        FLOAT_ADAPTER: u.TypeAdapter[t.StrictFloat] = u.TypeAdapter(
            t.StrictFloat,
        )
        STORAGE_ENTRY_ADAPTER: u.TypeAdapter[t.JsonMapping] = u.TypeAdapter(
            t.JsonMapping,
        )
        REQUEST_BODY_ADAPTER: u.TypeAdapter[RequestBody] = u.TypeAdapter(
            RequestBody,
        )

        RESPONSE_BODY_ADAPTER: u.TypeAdapter[ResponseBody] = u.TypeAdapter(
            ResponseBody,
        )
        DICT_BODY_ADAPTER: u.TypeAdapter[t.JsonMapping] = u.TypeAdapter(
            t.JsonMapping,
        )

        JSON_HEADERS_ADAPTER: u.TypeAdapter[t.JsonMapping] = u.TypeAdapter(
            t.JsonMapping,
        )


t = FlextApiTypes

__all__: list[str] = ["FlextApiTypes", "t"]
