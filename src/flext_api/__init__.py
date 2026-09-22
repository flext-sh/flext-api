# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

from .__version__ import (
    __author__ as __author__,
    __author_email__ as __author_email__,
    __description__ as __description__,
    __license__ as __license__,
    __title__ as __title__,
    __url__ as __url__,
    __version__ as __version__,
    __version_info__ as __version_info__,
)

if TYPE_CHECKING:
    from flext_cli import cli
    from flext_web import main, web
    from pydantic_core import from_json, to_json, to_jsonable_python

    from flext_core import core, d, e, h, lazy_attribute, r, x

    from . import services
    from ._config import FlextApiConfig, config
    from ._settings import FlextApiSettings, settings
    from .api import FlextApi, api
    from .base import FlextApiServiceBase, s
    from .cli import FlextApiCli
    from .constants import FlextApiConstants, c
    from .models import FlextApiModels, m
    from .protocols import (
        FlextApiProtocols,
        HttpxAsyncClient,
        HttpxClient,
        HttpxHTTPError,
        HttpxHTTPStatusError,
        HttpxRequestError,
        HttpxResponse,
        HttpxTimeoutException,
        p,
    )
    from .services.async_client import FlextApiAsyncClient
    from .services.base_client import FlextApiClientBase
    from .services.client import FlextApiClient
    from .typings import FlextApiTypes, t
    from .utilities import FlextApiUtilities, u
__all__: tuple[str, ...] = (
    "FlextApi",
    "FlextApiAsyncClient",
    "FlextApiCli",
    "FlextApiClient",
    "FlextApiClientBase",
    "FlextApiConfig",
    "FlextApiConstants",
    "FlextApiModels",
    "FlextApiProtocols",
    "FlextApiServiceBase",
    "FlextApiSettings",
    "FlextApiTypes",
    "FlextApiUtilities",
    "HttpxAsyncClient",
    "HttpxClient",
    "HttpxHTTPError",
    "HttpxHTTPStatusError",
    "HttpxRequestError",
    "HttpxResponse",
    "HttpxTimeoutException",
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
    "cli",
    "config",
    "core",
    "d",
    "e",
    "from_json",
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
    "to_json",
    "to_jsonable_python",
    "u",
    "web",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            "._config": ("FlextApiConfig", "config"),
            "._settings": ("FlextApiSettings", "settings"),
            ".api": ("FlextApi", "api"),
            ".base": ("FlextApiServiceBase", "s"),
            ".cli": ("FlextApiCli",),
            ".constants": ("FlextApiConstants", "c"),
            ".models": ("FlextApiModels", "m"),
            ".protocols": (
                "FlextApiProtocols",
                "HttpxAsyncClient",
                "HttpxClient",
                "HttpxHTTPError",
                "HttpxHTTPStatusError",
                "HttpxRequestError",
                "HttpxResponse",
                "HttpxTimeoutException",
                "p",
            ),
            ".services": ("services",),
            ".services.async_client": ("FlextApiAsyncClient",),
            ".services.base_client": ("FlextApiClientBase",),
            ".services.client": ("FlextApiClient",),
            ".typings": ("FlextApiTypes", "t"),
            ".utilities": ("FlextApiUtilities", "u"),
            "flext_cli": ("cli",),
            "flext_core": ("core", "d", "e", "h", "lazy_attribute", "r", "x"),
            "flext_web": ("main", "web"),
            "pydantic_core": ("from_json", "to_json", "to_jsonable_python"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
