# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if _t.TYPE_CHECKING:
    from flext_api.constants import c
    from flext_api.models import m
    from flext_api.protocols import p
    from flext_api.typings import t
    from flext_api.utilities import u
    from flext_core.decorators import d
    from flext_core.exceptions import e
    from flext_core.handlers import h
    from flext_core.mixins import x
    from flext_core.result import r
    from flext_core.service import s
_LAZY_IMPORTS = build_lazy_import_map(
    {
        "flext_api.constants": ("c",),
        "flext_api.models": ("m",),
        "flext_api.protocols": ("p",),
        "flext_api.typings": ("t",),
        "flext_api.utilities": ("u",),
        "flext_core.decorators": ("d",),
        "flext_core.exceptions": ("e",),
        "flext_core.handlers": ("h",),
        "flext_core.mixins": ("x",),
        "flext_core.result": ("r",),
        "flext_core.service": ("s",),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__ = [
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "u",
    "x",
]
