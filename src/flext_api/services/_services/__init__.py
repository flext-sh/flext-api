# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api.services. Services package.

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


__all__: tuple[str, ...] = (
    "FlextApiClientAsyncRequest",
    "FlextApiClientBaseRequest",
    "FlextApiClientCodec",
    "FlextApiClientRequest",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextApiClientAsyncRequest": ".async_request",
        "FlextApiClientBaseRequest": ".base_request",
        "FlextApiClientCodec": ".codec",
        "FlextApiClientRequest": ".request",
    }),
    public_exports=__all__,
)
