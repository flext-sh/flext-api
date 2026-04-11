# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if _t.TYPE_CHECKING:
    from flext_api.test_serializers import TestMessagePackUnpackb
    from flext_api.test_smoke import (
        TestConstants,
        TestFacadeInheritance,
        TestModels,
        TestSerializers,
        test_package_imports_main_facade,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".test_serializers": ("TestMessagePackUnpackb",),
        ".test_smoke": (
            "TestConstants",
            "TestFacadeInheritance",
            "TestModels",
            "TestSerializers",
            "test_package_imports_main_facade",
        ),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__ = [
    "TestConstants",
    "TestFacadeInheritance",
    "TestMessagePackUnpackb",
    "TestModels",
    "TestSerializers",
    "test_package_imports_main_facade",
]
