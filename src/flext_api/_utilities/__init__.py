# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api. Utilities package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from .api_pydantic import FlextApiUtilitiesApiPydantic
    from .base import FlextApiUtilitiesBase
    from .request_utils import FlextApiUtilitiesRequestUtils
    from .serializers import FlextApiUtilitiesSerializers
    from .settings_manager import FlextApiUtilitiesSettingsManager
    from .transport import FlextApiUtilitiesTransport


__all__: tuple[str, ...] = (
    "FlextApiUtilitiesApiPydantic",
    "FlextApiUtilitiesBase",
    "FlextApiUtilitiesRequestUtils",
    "FlextApiUtilitiesSerializers",
    "FlextApiUtilitiesSettingsManager",
    "FlextApiUtilitiesTransport",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".api_pydantic": ("FlextApiUtilitiesApiPydantic",),
            ".base": ("FlextApiUtilitiesBase",),
            ".request_utils": ("FlextApiUtilitiesRequestUtils",),
            ".serializers": ("FlextApiUtilitiesSerializers",),
            ".settings_manager": ("FlextApiUtilitiesSettingsManager",),
            ".transport": ("FlextApiUtilitiesTransport",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
