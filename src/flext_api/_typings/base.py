"""Base typings for flext-api — stand-in for facade MRO composition.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import ClassVar

from flext_web import FlextWebTypes, p, u

from flext_api._typings.adapters import FlextApiTypingsAdapters


class FlextApiTypingsBase(FlextApiTypingsAdapters):
    """Core API type aliases composed into ``t.Api`` by the typings facade."""

    type WebHeaders = FlextWebTypes.ScalarOrStrSequenceMapping
    type WebParams = Mapping[
        str,
        str | Sequence[str],
    ]
    type RequestBody = FlextWebTypes.JsonValue | FlextWebTypes.StrictBytes
    type ResponseBody = FlextWebTypes.JsonValue | FlextWebTypes.StrictBytes | None
    type HttpResponseDict = Mapping[
        str,
        FlextWebTypes.JsonValue
        | Mapping[str, str]
        | FlextWebTypes.JsonMapping
        | FlextWebTypes.StrictBytes
        | None,
    ]
    "HTTP response as dictionary (status_code, headers, body, request_id)."
    type WebhookHandler = Callable[
        [FlextWebTypes.JsonMapping],
        FlextWebTypes.JsonValue | p.Result[bool] | None,
    ]
    type RequestKwargs = Mapping[
        str,
        Mapping[str, str]
        | FlextWebTypes.JsonMapping
        | FlextWebTypes.ScalarOrStrSequenceMapping
        | float
        | None,
    ]
    type CacheDict = Mapping[str, FlextWebTypes.Primitives]
    API_JSON_VALUE_ADAPTER: ClassVar[
        FlextWebTypes.ValueAdapter[FlextWebTypes.JsonValue]
    ] = u.json_value_adapter()
    BINARY_CONTENT_ADAPTER: ClassVar[
        FlextWebTypes.ValueAdapter[FlextWebTypes.StrictBytes]
    ] = u.binary_content_adapter()
    STR_MAPPING_ADAPTER: ClassVar[FlextWebTypes.ValueAdapter[Mapping[str, str]]] = (
        u.str_mapping_adapter()
    )
    HOSTNAME_ADAPTER: ClassVar[
        FlextWebTypes.ValueAdapter[FlextWebTypes.HostnameStr]
    ] = u.hostname_str_adapter()
    PORT_NUMBER_ADAPTER: ClassVar[
        FlextWebTypes.ValueAdapter[FlextWebTypes.PortNumber]
    ] = u.port_number_adapter()
    STRING_ADAPTER: ClassVar[FlextWebTypes.ValueAdapter[FlextWebTypes.StrictStr]] = (
        u.str_adapter()
    )
    STORAGE_ENTRY_ADAPTER: ClassVar[
        FlextWebTypes.ValueAdapter[FlextWebTypes.JsonMapping]
    ] = u.json_mapping_adapter()
    REQUEST_BODY_ADAPTER: ClassVar[FlextWebTypes.ValueAdapter[RequestBody]] = (
        u.type_adapter(
            RequestBody,
        )
    )
    RESPONSE_BODY_ADAPTER: ClassVar[FlextWebTypes.ValueAdapter[ResponseBody]] = (
        u.type_adapter(
            ResponseBody,
        )
    )
    DICT_BODY_ADAPTER: ClassVar[
        FlextWebTypes.ValueAdapter[FlextWebTypes.JsonMapping]
    ] = u.json_mapping_adapter()
    JSON_HEADERS_ADAPTER: ClassVar[
        FlextWebTypes.ValueAdapter[FlextWebTypes.JsonMapping]
    ] = u.json_mapping_adapter()


__all__: list[str] = ["FlextApiTypingsBase"]
