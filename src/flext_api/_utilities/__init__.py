# @generated AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api. Utilities package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from .api_pydantic import (
        FlextApiUtilitiesApiPydantic as FlextApiUtilitiesApiPydantic,
    )
    from .client import FlextApiClient as FlextApiClient
    from .client_codec import FlextApiClientCodecMixin as FlextApiClientCodecMixin
    from .client_request import FlextApiClientRequestMixin as FlextApiClientRequestMixin
    from .request_utils import (
        FlextApiUtilitiesRequestUtils as FlextApiUtilitiesRequestUtils,
    )
    from .serializers import (
        FlextApiUtilitiesSerializers as FlextApiUtilitiesSerializers,
    )
    from .settings_manager import (
        FlextApiUtilitiesSettingsManager as FlextApiUtilitiesSettingsManager,
    )

_LAZY_MODULES: dict[str, tuple[str, ...]] = {
    ".api_pydantic": ("FlextApiUtilitiesApiPydantic",),
    ".client": ("FlextApiClient",),
    ".client_codec": ("FlextApiClientCodecMixin",),
    ".client_request": ("FlextApiClientRequestMixin",),
    ".request_utils": ("FlextApiUtilitiesRequestUtils",),
    ".serializers": ("FlextApiUtilitiesSerializers",),
    ".settings_manager": ("FlextApiUtilitiesSettingsManager",),
}


_LAZY_ALIAS_GROUPS: dict[str, tuple[tuple[str, str], ...]] = {}


_LAZY_IMPORTS = build_lazy_import_map(
    _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
)

_PUBLIC_EXPORTS: tuple[str, ...] = (
    "FlextApiClient",
    "FlextApiClientCodecMixin",
    "FlextApiClientRequestMixin",
    "FlextApiUtilitiesApiPydantic",
    "FlextApiUtilitiesRequestUtils",
    "FlextApiUtilitiesSerializers",
    "FlextApiUtilitiesSettingsManager",
)

__all__: tuple[str, ...] = tuple(_PUBLIC_EXPORTS)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
