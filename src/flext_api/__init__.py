# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from types import MappingProxyType

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
    from flext_web import d, e, h, r, x

    from ._config import FlextApiConfig, config
    from ._settings import FlextApiSettings, settings
    from .api import FlextApi, FlextApiClient, api
    from .base import FlextApiServiceBase, FlextApiServiceBase as s
    from .constants import FlextApiConstants, FlextApiConstants as c
    from .models import FlextApiModels, FlextApiModels as m
    from .protocols import FlextApiProtocols, FlextApiProtocols as p
    from .typings import FlextApiTypes, FlextApiTypes as t
    from .utilities import FlextApiUtilities, FlextApiUtilities as u
__all__: tuple[str, ...] = (
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

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType(
        build_lazy_import_map(
            MappingProxyType({
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
            }),
            alias_groups=MappingProxyType({}),
            sort_keys=False,
        )
    ),
    public_exports=__all__,
)
