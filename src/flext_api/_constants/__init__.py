# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api. Constants package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_api._constants.api import FlextApiConstantsApi
    from flext_api._constants.api_enums import FlextApiConstantsEnums
    from flext_api._constants.api_values import FlextApiConstantsValues
    from flext_api._constants.base import FlextApiConstantsBase
    from flext_api._constants.config import FlextApiConstantsConfig


__all__: tuple[str, ...] = (
    "FlextApiConstantsApi",
    "FlextApiConstantsBase",
    "FlextApiConstantsConfig",
    "FlextApiConstantsEnums",
    "FlextApiConstantsValues",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".api": ("FlextApiConstantsApi",),
            ".api_enums": ("FlextApiConstantsEnums",),
            ".api_values": ("FlextApiConstantsValues",),
            ".base": ("FlextApiConstantsBase",),
            ".config": ("FlextApiConstantsConfig",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
