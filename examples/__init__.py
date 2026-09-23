# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli import cli
    from flext_web import services, web

    from flext_api import api, c, config, m, main, p, s, settings, t, u
    from flext_core import core, d, e, h, lazy_attribute, r, x


__all__: tuple[str, ...] = (
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
    "services",
    "settings",
    "t",
    "u",
    "web",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
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
            "flext_web": ("services", "web"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
