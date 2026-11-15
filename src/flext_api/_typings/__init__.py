# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api. Typings package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_api._typings.base import FlextApiTypingsBase
    from flext_api._typings.serialization import FlextApiTypingsSerialization
    from flext_api._typings.transport import FlextApiTypingsTransport


__all__: tuple[str, ...] = (
    "FlextApiTypingsBase",
    "FlextApiTypingsSerialization",
    "FlextApiTypingsTransport",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "FlextApiTypingsBase": ".base",
        "FlextApiTypingsSerialization": ".serialization",
        "FlextApiTypingsTransport": ".transport",
    },
    public_exports=__all__,
    deferred_members={
        "FlextApiTypingsBase": (
            "WebHeaders",
            "WebParams",
            "RequestBody",
            "ResponseBody",
            "HttpResponseDict",
            "WebhookHandler",
            "RequestKwargs",
            "CacheDict",
            "API_JSON_VALUE_ADAPTER",
            "BINARY_CONTENT_ADAPTER",
            "STR_MAPPING_ADAPTER",
            "HOSTNAME_ADAPTER",
            "PORT_NUMBER_ADAPTER",
            "STRING_ADAPTER",
            "STORAGE_ENTRY_ADAPTER",
            "REQUEST_BODY_ADAPTER",
            "RESPONSE_BODY_ADAPTER",
            "DICT_BODY_ADAPTER",
            "JSON_HEADERS_ADAPTER",
        ),
        "FlextApiTypingsSerialization": ("MsgpackBinary",),
        "FlextApiTypingsTransport": (
            "WebhookDeliveryStatus",
            "WebhookAlgorithm",
        ),
    },
)
