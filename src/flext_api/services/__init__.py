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
    from flext_api.services._services.async_request import (
        FlextApiClientAsyncRequestMixin,
    )
    from flext_api.services._services.base_request import FlextApiClientBaseRequestMixin
    from flext_api.services._services.codec import FlextApiClientCodecMixin
    from flext_api.services._services.request import FlextApiClientRequestMixin
    from flext_api.services.async_client import FlextApiAsyncClient
    from flext_api.services.base_client import FlextApiClientBase
    from flext_api.services.client import FlextApiClient


__all__: tuple[str, ...] = (
    "FlextApiAsyncClient",
    "FlextApiClient",
    "FlextApiClientAsyncRequestMixin",
    "FlextApiClientBase",
    "FlextApiClientBaseRequestMixin",
    "FlextApiClientCodecMixin",
    "FlextApiClientRequestMixin",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextApiAsyncClient": ".async_client",
        "FlextApiClient": ".client",
        "FlextApiClientAsyncRequestMixin": "._services.async_request",
        "FlextApiClientBase": ".base_client",
        "FlextApiClientBaseRequestMixin": "._services.base_request",
        "FlextApiClientCodecMixin": "._services.codec",
        "FlextApiClientRequestMixin": "._services.request",
    }),
    public_exports=__all__,
)
