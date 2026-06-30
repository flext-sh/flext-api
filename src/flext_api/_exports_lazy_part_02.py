# AUTO-GENERATED FILE — Regenerate with: make gen
"""Lazy export map part."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map

FLEXT_API_LAZY_IMPORTS_PART_02 = build_lazy_import_map(
    {
        "._utilities.api_pydantic": ("FlextApiUtilitiesApiPydantic",),
        "._utilities.request_utils": ("FlextApiUtilitiesRequestUtils",),
        "._utilities.serializers": ("FlextApiUtilitiesSerializers",),
        "._utilities.settings_manager": ("FlextApiUtilitiesSettingsManager",),
        ".api": ("api",),
        ".base": ("s",),
        ".constants": ("c",),
        ".models": ("m",),
        ".protocols": ("p",),
        ".typings": ("t",),
        ".utilities": ("u",),
    },
)

__all__: list[str] = ["FLEXT_API_LAZY_IMPORTS_PART_02"]
