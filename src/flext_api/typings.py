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

from flext_web import FlextWebTypings, m, u

from flext_api import c
from flext_api._typings import (
    FlextApiTypingsBase,
    FlextApiTypingsSerialization,
    FlextApiTypingsTransport,
)

if TYPE_CHECKING:
    from flext_api import m, p


class FlextApiTypes(FlextWebTypings):
    """Unified API type definitions extending t via MRO."""

    class Api(
        FlextApiTypingsBase,
        FlextApiTypingsSerialization,
        FlextApiTypingsTransport,
    ):
        """API types namespace for cross-project access."""

        type WebHeaders = FlextWebTypings.ScalarOrStrSequenceMapping
        type WebParams = FlextWebTypings.MappingKV[
            str,
            str | FlextWebTypings.StrSequence,
        ]
        type RequestBody = FlextWebTypings.JsonValue | FlextWebTypings.StrictBytes
        type ResponseBody = (
            FlextWebTypings.JsonValue | FlextWebTypings.StrictBytes | None
        )
        type HttpResponseDict = FlextWebTypings.MappingKV[
            str,
            FlextWebTypings.JsonValue
            | FlextWebTypings.StrMapping
            | FlextWebTypings.JsonMapping
            | FlextWebTypings.StrictBytes
            | None,
        ]
        "HTTP response as dictionary (status_code, headers, body, request_id)."
        type RouteData = FlextWebTypings.MappingKV[
            str,
            FlextWebTypings.JsonValue
            | FlextWebTypings.ConfigurationMapping
            | FlextWebTypings.JsonMapping
            | FlextWebTypings.ResourceCallable
            | Callable[..., FlextApiTypes.Api.HttpResponseDict | str | None]
            | None,
        ]
        "Route registration data structure."
        type WebhookDeliveryStatus = c.Api.WebhookDeliveryStatus | str
        type WebhookAlgorithm = c.Api.WebhookAlgorithm | str
        type WebhookHandler = Callable[
            [FlextWebTypings.JsonMapping],
            FlextWebTypings.JsonValue | p.Result[bool] | None,
        ]
        type RequestKwargs = FlextWebTypings.MappingKV[
            str,
            FlextWebTypings.StrMapping
            | FlextWebTypings.JsonMapping
            | FlextWebTypings.ScalarOrStrSequenceMapping
            | float
            | None,
        ]
        type CacheDict = FlextWebTypings.MappingKV[str, FlextWebTypings.Primitives]
        API_JSON_VALUE_ADAPTER: m.TypeAdapter[FlextWebTypings.JsonValue] = (
            FlextWebTypings.json_value_adapter()
        )
        BINARY_CONTENT_ADAPTER: m.TypeAdapter[FlextWebTypings.StrictBytes] = (
            FlextWebTypings.binary_content_adapter()
        )
        STR_MAPPING_ADAPTER: m.TypeAdapter[FlextWebTypings.StrMapping] = (
            FlextWebTypings.str_mapping_adapter()
        )
        HOSTNAME_ADAPTER: m.TypeAdapter[FlextWebTypings.HostnameStr] = (
            FlextWebTypings.hostname_str_adapter()
        )
        PORT_NUMBER_ADAPTER: m.TypeAdapter[FlextWebTypings.PortNumber] = (
            FlextWebTypings.port_number_adapter()
        )
        STRING_ADAPTER: m.TypeAdapter[FlextWebTypings.StrictStr] = (
            FlextWebTypings.str_adapter()
        )
        STORAGE_ENTRY_ADAPTER: m.TypeAdapter[FlextWebTypings.JsonMapping] = (
            FlextWebTypings.json_mapping_adapter()
        )
        REQUEST_BODY_ADAPTER: m.TypeAdapter[RequestBody] = u.type_adapter(RequestBody)
        RESPONSE_BODY_ADAPTER: m.TypeAdapter[ResponseBody] = u.type_adapter(
            ResponseBody,
        )
        DICT_BODY_ADAPTER: m.TypeAdapter[FlextWebTypings.JsonMapping] = (
            FlextWebTypings.json_mapping_adapter()
        )
        JSON_HEADERS_ADAPTER: m.TypeAdapter[FlextWebTypings.JsonMapping] = (
            FlextWebTypings.json_mapping_adapter()
        )


t = FlextApiTypes

__all__: list[str] = ["FlextApiTypes", "t"]
