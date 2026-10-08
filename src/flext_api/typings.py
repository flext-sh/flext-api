"""FLEXT API Types - Unified domain-specific type definitions with Clean Architecture.

Single class namespace with NO aliases, NO weak types.
All types consolidated within FlextApiTypes using Python 3.13+ syntax.

Note: Protocols are in protocols.py, not here. Use p.Api.* for protocols.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from flext_web import FlextWebTypes, m, p, u

from flext_api import c
from flext_api._typings import (
    FlextApiTypingsBase,
    FlextApiTypingsSerialization,
    FlextApiTypingsTransport,
)

if TYPE_CHECKING:
    from flext_api import m


class FlextApiTypes(FlextWebTypes):
    """Unified API type definitions extending FlextWebTypes via MRO."""

    class Api(
        FlextApiTypingsBase,
        FlextApiTypingsSerialization,
        FlextApiTypingsTransport,
    ):
        """API types namespace for cross-project access."""

        type WebHeaders = FlextWebTypes.ScalarOrStrSequenceMapping
        type WebParams = FlextWebTypes.MappingKV[
            str,
            str | FlextWebTypes.StrSequence,
        ]
        type RequestBody = FlextWebTypes.JsonValue | FlextWebTypes.StrictBytes
        type ResponseBody = (
            FlextWebTypes.JsonValue | FlextWebTypes.StrictBytes | None
        )
        type HttpResponseDict = FlextWebTypes.MappingKV[
            str,
            FlextWebTypes.JsonValue
            | FlextWebTypes.StrMapping
            | FlextWebTypes.JsonMapping
            | FlextWebTypes.StrictBytes
            | None,
        ]
        "HTTP response as dictionary (status_code, headers, body, request_id)."
        type RouteData = FlextWebTypes.MappingKV[
            str,
            FlextWebTypes.JsonValue
            | FlextWebTypes.ConfigurationMapping
            | FlextWebTypes.JsonMapping
            | FlextWebTypes.ResourceCallable
            | Callable[..., FlextApiTypes.Api.HttpResponseDict | str | None]
            | None,
        ]
        "Route registration data structure."
        type WebhookDeliveryStatus = c.Api.WebhookDeliveryStatus | str
        type WebhookAlgorithm = c.Api.WebhookAlgorithm | str
        type WebhookHandler = Callable[
            [FlextWebTypes.JsonMapping],
            FlextWebTypes.JsonValue | p.Result[bool] | None,
        ]
        type RequestKwargs = FlextWebTypes.MappingKV[
            str,
            FlextWebTypes.StrMapping
            | FlextWebTypes.JsonMapping
            | FlextWebTypes.ScalarOrStrSequenceMapping
            | float
            | None,
        ]
        type CacheDict = FlextWebTypes.MappingKV[str, FlextWebTypes.Primitives]
        API_JSON_VALUE_ADAPTER: m.TypeAdapter[FlextWebTypes.JsonValue] = (
            FlextWebTypes.json_value_adapter()
        )
        BINARY_CONTENT_ADAPTER: m.TypeAdapter[FlextWebTypes.StrictBytes] = (
            FlextWebTypes.binary_content_adapter()
        )
        STR_MAPPING_ADAPTER: m.TypeAdapter[FlextWebTypes.StrMapping] = (
            FlextWebTypes.str_mapping_adapter()
        )
        HOSTNAME_ADAPTER: m.TypeAdapter[FlextWebTypes.HostnameStr] = (
            FlextWebTypes.hostname_str_adapter()
        )
        PORT_NUMBER_ADAPTER: m.TypeAdapter[FlextWebTypes.PortNumber] = (
            FlextWebTypes.port_number_adapter()
        )
        STRING_ADAPTER: m.TypeAdapter[FlextWebTypes.StrictStr] = (
            FlextWebTypes.str_adapter()
        )
        STORAGE_ENTRY_ADAPTER: m.TypeAdapter[FlextWebTypes.JsonMapping] = (
            FlextWebTypes.json_mapping_adapter()
        )
        REQUEST_BODY_ADAPTER: m.TypeAdapter[RequestBody] = u.type_adapter(RequestBody)
        RESPONSE_BODY_ADAPTER: m.TypeAdapter[ResponseBody] = u.type_adapter(
            ResponseBody,
        )
        DICT_BODY_ADAPTER: m.TypeAdapter[FlextWebTypes.JsonMapping] = (
            FlextWebTypes.json_mapping_adapter()
        )
        JSON_HEADERS_ADAPTER: m.TypeAdapter[FlextWebTypes.JsonMapping] = (
            FlextWebTypes.json_mapping_adapter()
        )


t = FlextApiTypes

__all__: list[str] = ["FlextApiTypes", "t"]
