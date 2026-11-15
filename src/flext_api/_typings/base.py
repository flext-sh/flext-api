"""Base typings for flext-api — stand-in for facade MRO composition.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence

from flext_web import FlextWebTypes, p

from flext_api._utilities.adapters import FlextApiTypingsAdapters


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


__all__: list[str] = ["FlextApiTypingsBase"]
