# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api. Constants package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from .api import FlextApiConstantsApi
    from .api_enums import FlextApiConstantsEnums
    from .api_values import FlextApiConstantsValues
    from .base import FlextApiConstantsBase
    from .config import FlextApiConstantsConfig


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
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
