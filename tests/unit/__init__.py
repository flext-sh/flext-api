# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests.unit package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from types import MappingProxyType

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import c, d, e, h, m, p, r, s, t, td, tf, tk, tm, tv, u, x

    from .test_serializers import TestsFlextApiSerializers
    from .test_smoke import TestsFlextApiSmoke
    from .test_transports_characterization import (
        TestsFlextApiTransportsCharacterization,
    )
__all__: tuple[str, ...] = (
    "TestsFlextApiSerializers",
    "TestsFlextApiSmoke",
    "TestsFlextApiTransportsCharacterization",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "td",
    "tf",
    "tk",
    "tm",
    "tv",
    "u",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".test_serializers": ("TestsFlextApiSerializers",),
            ".test_smoke": ("TestsFlextApiSmoke",),
            ".test_transports_characterization": (
                "TestsFlextApiTransportsCharacterization",
            ),
            "flext_tests": (
                "c",
                "d",
                "e",
                "h",
                "m",
                "p",
                "r",
                "s",
                "t",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
                "u",
                "x",
            ),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
