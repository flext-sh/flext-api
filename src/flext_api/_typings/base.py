"""Base typings for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable

from flext_web import FlextWebTypes, p, u

from flext_api import c


class FlextApiTypingsBase:
    """Core API type aliases composed into ``t.Api`` by the typings facade."""

    type WebHeaders = FlextWebTypes.ScalarOrStrSequenceMapping
    type WebParams = FlextWebTypes.MappingKV[
        str,
        str | FlextWebTypes.StrSequence,
    ]
    type RequestBody = FlextWebTypes.JsonValue | FlextWebTypes.StrictBytes
    type ResponseBody = FlextWebTypes.JsonValue | FlextWebTypes.StrictBytes | None
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
        | Callable[..., HttpResponseDict | str | None]
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
    API_JSON_VALUE_ADAPTER: FlextWebTypes.ValueAdapter[FlextWebTypes.JsonValue] = (
        u.json_value_adapter()
    )
    BINARY_CONTENT_ADAPTER: FlextWebTypes.ValueAdapter[FlextWebTypes.StrictBytes] = (
        u.binary_content_adapter()
    )
    STR_MAPPING_ADAPTER: FlextWebTypes.ValueAdapter[FlextWebTypes.StrMapping] = (
        u.str_mapping_adapter()
    )
    HOSTNAME_ADAPTER: FlextWebTypes.ValueAdapter[FlextWebTypes.HostnameStr] = (
        u.hostname_str_adapter()
    )
    PORT_NUMBER_ADAPTER: FlextWebTypes.ValueAdapter[FlextWebTypes.PortNumber] = (
        u.port_number_adapter()
    )
    STRING_ADAPTER: FlextWebTypes.ValueAdapter[FlextWebTypes.StrictStr] = (
        u.str_adapter()
    )
    STORAGE_ENTRY_ADAPTER: FlextWebTypes.ValueAdapter[FlextWebTypes.JsonMapping] = (
        u.json_mapping_adapter()
    )
    REQUEST_BODY_ADAPTER: FlextWebTypes.ValueAdapter[RequestBody] = u.type_adapter(
        RequestBody,
    )
    RESPONSE_BODY_ADAPTER: FlextWebTypes.ValueAdapter[ResponseBody] = u.type_adapter(
        ResponseBody,
    )
    DICT_BODY_ADAPTER: FlextWebTypes.ValueAdapter[FlextWebTypes.JsonMapping] = (
        u.json_mapping_adapter()
    )
    JSON_HEADERS_ADAPTER: FlextWebTypes.ValueAdapter[FlextWebTypes.JsonMapping] = (
        u.json_mapping_adapter()
    )


__all__: list[str] = ["FlextApiTypingsBase"]
