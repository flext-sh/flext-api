"""FLEXT API Types - Unified domain-specific type definitions with Clean Architecture.

Single class namespace with NO aliases, NO weak types.
All types consolidated within FlextApiTypes using Python 3.13+ syntax.

Note: Protocols are in protocols.py, not here. Use p.Api.* for protocols.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable

from flext_web import p, t, u

from flext_api import c
from flext_api._typings.base import FlextApiTypingsBase
from flext_api._typings.serialization import FlextApiTypingsSerialization
from flext_api._typings.transport import FlextApiTypingsTransport


class FlextApiTypes(t):
    """Unified API type definitions extending t via MRO."""

    class Api(
        FlextApiTypingsBase,
        FlextApiTypingsSerialization,
        FlextApiTypingsTransport,
    ):
        """API types namespace for cross-project access."""

        type WebHeaders = t.ScalarOrStrSequenceMapping
        type WebParams = t.MappingKV[str, str | t.StrSequence]
        type RequestBody = t.JsonValue | t.StrictBytes
        type ResponseBody = t.JsonValue | t.StrictBytes | None
        type HttpResponseDict = t.MappingKV[
            str,
            t.JsonValue | t.StrMapping | t.JsonMapping | t.StrictBytes | None,
        ]
        "HTTP response as dictionary (status_code, headers, body, request_id)."
        type RouteData = t.MappingKV[
            str,
            t.JsonValue
            | t.ConfigurationMapping
            | t.JsonMapping
            | t.ResourceCallable
            | Callable[..., FlextApiTypes.Api.HttpResponseDict | str | None]
            | None,
        ]
        "Route registration data structure."
        type WebhookDeliveryStatus = c.Api.WebhookDeliveryStatus | str
        type WebhookAlgorithm = c.Api.WebhookAlgorithm | str
        type WebhookHandler = Callable[
            [t.JsonMapping],
            t.JsonValue | p.Result[bool] | None,
        ]
        type RequestKwargs = t.MappingKV[
            str,
            t.StrMapping | t.JsonMapping | t.ScalarOrStrSequenceMapping | float | None,
        ]
        type CacheDict = t.MappingKV[str, t.Primitives]
        API_JSON_VALUE_ADAPTER: u.type_adapter[t.JsonValue] = t.json_value_adapter()
        BINARY_CONTENT_ADAPTER: u.type_adapter[t.StrictBytes] = (
            t.binary_content_adapter()
        )
        STR_MAPPING_ADAPTER: u.type_adapter[t.StrMapping] = t.str_mapping_adapter()
        HOSTNAME_ADAPTER: u.type_adapter[t.HostnameStr] = t.hostname_str_adapter()
        PORT_NUMBER_ADAPTER: u.type_adapter[t.PortNumber] = t.port_number_adapter()
        STRING_ADAPTER: u.type_adapter[t.StrictStr] = t.str_adapter()
        INTEGER_ADAPTER: u.type_adapter[t.StrictInt] = t.int_adapter()
        FLOAT_ADAPTER: u.type_adapter[t.StrictFloat] = t.float_adapter()
        STORAGE_ENTRY_ADAPTER: u.type_adapter[t.JsonMapping] = t.json_mapping_adapter()
        REQUEST_BODY_ADAPTER: u.type_adapter[RequestBody] = u.type_adapter(RequestBody)

        RESPONSE_BODY_ADAPTER: u.type_adapter[ResponseBody] = u.type_adapter(
            ResponseBody,
        )
        DICT_BODY_ADAPTER: u.type_adapter[t.JsonMapping] = t.json_mapping_adapter()
        JSON_HEADERS_ADAPTER: u.type_adapter[t.JsonMapping] = t.json_mapping_adapter()


t = FlextApiTypes

__all__: list[str] = ["FlextApiTypes", "t"]
