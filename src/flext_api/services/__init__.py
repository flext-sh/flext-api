# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api.services package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_api.services._services.async_request import FlextApiClientAsyncRequest
    from flext_api.services._services.base_request import FlextApiClientBaseRequest
    from flext_api.services._services.codec import FlextApiClientCodec
    from flext_api.services._services.request import FlextApiClientRequest
    from flext_api.services.async_client import FlextApiAsyncClient
    from flext_api.services.base_client import FlextApiClientBase
    from flext_api.services.client import FlextApiClient


__all__: tuple[str, ...] = (
    "FlextApiAsyncClient",
    "FlextApiClient",
    "FlextApiClientAsyncRequest",
    "FlextApiClientBase",
    "FlextApiClientBaseRequest",
    "FlextApiClientCodec",
    "FlextApiClientRequest",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextApiAsyncClient": ".async_client",
        "FlextApiClient": ".client",
        "FlextApiClientAsyncRequest": "._services.async_request",
        "FlextApiClientBase": ".base_client",
        "FlextApiClientBaseRequest": "._services.base_request",
        "FlextApiClientCodec": "._services.codec",
        "FlextApiClientRequest": "._services.request",
    }),
    public_exports=__all__,
)
