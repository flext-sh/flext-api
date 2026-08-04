# @generated AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

from .__version__ import __author__ as __author__
from .__version__ import __author_email__ as __author_email__
from .__version__ import __description__ as __description__
from .__version__ import __license__ as __license__
from .__version__ import __title__ as __title__
from .__version__ import __url__ as __url__
from .__version__ import __version__ as __version__
from .__version__ import __version_info__ as __version_info__

if TYPE_CHECKING:
    from flext_web import d as d
    from flext_web import e as e
    from flext_web import h as h
    from flext_web import r as r
    from flext_web import x as x

    from ._config import FlextApiConfig as FlextApiConfig
    from ._config import config as config
    from ._settings import FlextApiSettings as FlextApiSettings
    from ._settings import settings as settings
    from .api import FlextApi as FlextApi
    from .api import FlextApiClient as FlextApiClient
    from .api import api as api
    from .base import (
        FlextApiServiceBase as FlextApiServiceBase,
        FlextApiServiceBase as s,
    )
    from .constants import FlextApiConstants as FlextApiConstants

    c: type[FlextApiConstants]
    from .models import FlextApiModels as FlextApiModels

    m: type[FlextApiModels]
    from .protocols import FlextApiProtocols as FlextApiProtocols

    p: type[FlextApiProtocols]
    from .typings import FlextApiTypes as FlextApiTypes

    t: type[FlextApiTypes]
    from .utilities import FlextApiUtilities as FlextApiUtilities

    u: type[FlextApiUtilities]

_LAZY_MODULES: dict[str, tuple[str, ...]] = {
    "._config": ("FlextApiConfig", "config"),
    "._settings": ("FlextApiSettings", "settings"),
    ".api": ("FlextApi", "FlextApiClient", "api"),
    ".base": ("FlextApiServiceBase", "s"),
    ".constants": ("FlextApiConstants", "c"),
    ".models": ("FlextApiModels", "m"),
    ".protocols": ("FlextApiProtocols", "p"),
    ".typings": ("FlextApiTypes", "t"),
    ".utilities": ("FlextApiUtilities", "u"),
    "flext_web": ("d", "e", "h", "r", "x"),
}


_LAZY_ALIAS_GROUPS: dict[str, tuple[tuple[str, str], ...]] = {}


_LAZY_IMPORTS = build_lazy_import_map(
    _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
)

_PUBLIC_EXPORTS: tuple[str, ...] = (
    "FlextApi",
    "FlextApiClient",
    "FlextApiConfig",
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
    "config",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "u",
    "x",
)

__all__: tuple[str, ...] = tuple(_PUBLIC_EXPORTS)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
