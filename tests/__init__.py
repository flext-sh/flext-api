# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli import cli
<<<<<<< HEAD
    from flext_web import services, web
=======
    from flext_web import web
>>>>>>> origin/chore/regen-20260923

    from flext_api import api, c, config, m, main, p, s, settings, t, u
    from flext_core import core, d, e, h, lazy_attribute, r, x

    from . import unit
    from .base import TestsFlextApiServiceBase
    from .constants import TestsFlextApiConstants
    from .models import TestsFlextApiModels
    from .protocols import TestsFlextApiProtocols
    from .settings import TestsFlextApiSettings
    from .typings import TestsFlextApiTypes
    from .utilities import TestsFlextApiUtilities


__all__: tuple[str, ...] = (
    "TestsFlextApiConstants",
    "TestsFlextApiModels",
    "TestsFlextApiProtocols",
    "TestsFlextApiServiceBase",
    "TestsFlextApiSettings",
    "TestsFlextApiTypes",
    "TestsFlextApiUtilities",
    "api",
    "c",
    "cli",
    "config",
    "core",
    "d",
    "e",
    "h",
    "lazy_attribute",
    "m",
    "main",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "u",
    "unit",
    "web",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".base": ("TestsFlextApiServiceBase",),
            ".constants": ("TestsFlextApiConstants",),
            ".models": ("TestsFlextApiModels",),
            ".protocols": ("TestsFlextApiProtocols",),
            ".settings": ("TestsFlextApiSettings",),
            ".typings": ("TestsFlextApiTypes",),
            ".unit": ("unit",),
            ".utilities": ("TestsFlextApiUtilities",),
            "flext_api": (
                "api",
                "c",
                "config",
                "m",
                "main",
                "p",
                "s",
                "settings",
                "t",
                "u",
            ),
            "flext_cli": ("cli",),
            "flext_core": ("core", "d", "e", "h", "lazy_attribute", "r", "x"),
<<<<<<< HEAD
            "flext_web": ("services", "web"),
=======
            "flext_web": ("web",),
>>>>>>> origin/chore/regen-20260923
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
