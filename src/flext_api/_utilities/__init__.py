# AUTO-GENERATED FILE — Regenerate with: make gen
"""Utilities package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

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
