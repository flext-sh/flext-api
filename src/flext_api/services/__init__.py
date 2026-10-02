# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api.services package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_api.services import _services
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
    "_services",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            "._services": ("_services",),
            "._services.async_request": ("FlextApiClientAsyncRequestMixin",),
            "._services.base_request": ("FlextApiClientBaseRequestMixin",),
            "._services.codec": ("FlextApiClientCodecMixin",),
            "._services.request": ("FlextApiClientRequestMixin",),
            ".async_client": ("FlextApiAsyncClient",),
            ".base_client": ("FlextApiClientBase",),
            ".client": ("FlextApiClient",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
