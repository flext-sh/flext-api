# AUTO-GENERATED FILE — Regenerate with: make gen
"""Lazy export map part."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map

FLEXT_API_LAZY_IMPORTS_PART_01 = build_lazy_import_map(
    {
        "._constants": ("_constants",),
        "._models": ("_models",),
        "._protocols": ("_protocols",),
        "._typings": ("_typings",),
        "._utilities": ("_utilities",),
        ".api": (
            "FlextApi",
            "api",
        ),
        ".base": (
            "FlextApiServiceBase",
            "s",
        ),
        ".constants": (
            "FlextApiConstants",
            "c",
        ),
        ".models": (
            "FlextApiModels",
            "m",
        ),
        ".protocol_impls": ("protocol_impls",),
        ".protocols": (
            "FlextApiProtocols",
            "p",
        ),
        ".settings": ("FlextApiSettings",),
        ".typings": (
            "FlextApiTypes",
            "t",
        ),
        ".utilities": (
            "FlextApiUtilities",
            "u",
        ),
    },
)

__all__: list[str] = ["FLEXT_API_LAZY_IMPORTS_PART_01"]
