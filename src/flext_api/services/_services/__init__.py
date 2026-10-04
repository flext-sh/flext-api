# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api.services. Services package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_api.services._services.async_request import (
        FlextApiClientAsyncRequestMixin,
    )
    from flext_api.services._services.base_request import FlextApiClientBaseRequestMixin
    from flext_api.services._services.codec import FlextApiClientCodecMixin
    from flext_api.services._services.request import FlextApiClientRequestMixin


__all__: tuple[str, ...] = (
    "FlextApiClientAsyncRequestMixin",
    "FlextApiClientBaseRequestMixin",
    "FlextApiClientCodecMixin",
    "FlextApiClientRequestMixin",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".async_request": ("FlextApiClientAsyncRequestMixin",),
            ".base_request": ("FlextApiClientBaseRequestMixin",),
            ".codec": ("FlextApiClientCodecMixin",),
            ".request": ("FlextApiClientRequestMixin",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
