# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api. Utilities package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from types import MappingProxyType

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from .api_pydantic import FlextApiUtilitiesApiPydantic
    from .client import FlextApiClient
    from .client_codec import FlextApiClientCodecMixin
    from .client_request import FlextApiClientRequestMixin
    from .request_utils import FlextApiUtilitiesRequestUtils
    from .serializers import FlextApiUtilitiesSerializers
    from .settings_manager import FlextApiUtilitiesSettingsManager
__all__: tuple[str, ...] = (
    "FlextApiClient",
    "FlextApiClientCodecMixin",
    "FlextApiClientRequestMixin",
    "FlextApiUtilitiesApiPydantic",
    "FlextApiUtilitiesRequestUtils",
    "FlextApiUtilitiesSerializers",
    "FlextApiUtilitiesSettingsManager",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".api_pydantic": ("FlextApiUtilitiesApiPydantic",),
            ".client": ("FlextApiClient",),
            ".client_codec": ("FlextApiClientCodecMixin",),
            ".client_request": ("FlextApiClientRequestMixin",),
            ".request_utils": ("FlextApiUtilitiesRequestUtils",),
            ".serializers": ("FlextApiUtilitiesSerializers",),
            ".settings_manager": ("FlextApiUtilitiesSettingsManager",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
