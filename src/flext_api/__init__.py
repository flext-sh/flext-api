# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_api.__version__ import (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
    __version_info__,
)
from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_api.api import FlextApi, api
    from flext_api.base import FlextApiServiceBase, s
    from flext_api.constants import FlextApiConstants, c
    from flext_api.models import FlextApiModels, m
    from flext_api.protocols import FlextApiProtocols, p
    from flext_api.settings import FlextApiSettings
    from flext_api.typings import FlextApiTypes, t
    from flext_api.utilities import FlextApiUtilities, u
    from flext_web import d, e, h, r, x
_LAZY_IMPORTS = build_lazy_import_map(
    {
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
        "flext_web": (
            "d",
            "e",
            "h",
            "r",
            "x",
        ),
    },
)


__all__: tuple[str, ...] = (
    "FlextApi",
    "FlextApiConstants",
    "FlextApiModels",
    "FlextApiProtocols",
    "FlextApiServiceBase",
    "FlextApiSettings",
    "FlextApiTypes",
    "FlextApiUtilities",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "api",
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
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    public_exports=__all__,
)
