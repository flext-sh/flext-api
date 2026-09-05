# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from typing import TYPE_CHECKING

    from flext_tests import FlextTestsConstants, d, e, h, r, td, tf, tk, tm, tv, x

    from . import unit as unit
    from .base import TestsFlextApiServiceBase, TestsFlextApiServiceBase as s
    from .constants import TestsFlextApiConstants, TestsFlextApiConstants as c
    from .models import TestsFlextApiModels, TestsFlextApiModels as m
    from .protocols import TestsFlextApiProtocols, TestsFlextApiProtocols as p
    from .settings import TestsFlextApiSettings
    from .typings import TestsFlextApiTypes, TestsFlextApiTypes as t
    from .utilities import TestsFlextApiUtilities, TestsFlextApiUtilities as u
__all__: tuple[str, ...] = (
    "TYPE_CHECKING",
    "FlextTestsConstants",
    "TestsFlextApiConstants",
    "TestsFlextApiModels",
    "TestsFlextApiProtocols",
    "TestsFlextApiServiceBase",
    "TestsFlextApiSettings",
    "TestsFlextApiTypes",
    "TestsFlextApiUtilities",
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
    "unit",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".base": ("TestsFlextApiServiceBase", "s"),
            ".constants": ("TestsFlextApiConstants", "c"),
            ".models": ("TestsFlextApiModels", "m"),
            ".protocols": ("TestsFlextApiProtocols", "p"),
            ".settings": ("TestsFlextApiSettings",),
            ".typings": ("TestsFlextApiTypes", "t"),
            ".unit": ("unit",),
            ".utilities": ("TestsFlextApiUtilities", "u"),
            "flext_tests": (
                "FlextTestsConstants",
                "d",
                "e",
                "h",
                "r",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
                "x",
            ),
            "typing": ("TYPE_CHECKING",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
