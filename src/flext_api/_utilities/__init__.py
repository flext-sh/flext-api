# AUTO-GENERATED FILE — Regenerate with: make gen
"""Utilities package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_api._utilities.api_pydantic import (
        FlextApiUtilitiesApiPydantic as FlextApiUtilitiesApiPydantic,
    )
    from flext_api._utilities.client import FlextApiClient as FlextApiClient
    from flext_api._utilities.client_codec import (
        FlextApiClientCodecMixin as FlextApiClientCodecMixin,
    )
    from flext_api._utilities.client_request import (
        FlextApiClientRequestMixin as FlextApiClientRequestMixin,
    )
    from flext_api._utilities.request_utils import (
        FlextApiUtilitiesRequestUtils as FlextApiUtilitiesRequestUtils,
    )
    from flext_api._utilities.serializers import (
        FlextApiUtilitiesSerializers as FlextApiUtilitiesSerializers,
    )
    from flext_api._utilities.settings_manager import (
        FlextApiUtilitiesSettingsManager as FlextApiUtilitiesSettingsManager,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".api_pydantic": ("FlextApiUtilitiesApiPydantic",),
        ".client": ("FlextApiClient",),
        ".client_codec": ("FlextApiClientCodecMixin",),
        ".client_request": ("FlextApiClientRequestMixin",),
        ".request_utils": ("FlextApiUtilitiesRequestUtils",),
        ".serializers": ("FlextApiUtilitiesSerializers",),
        ".settings_manager": ("FlextApiUtilitiesSettingsManager",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
