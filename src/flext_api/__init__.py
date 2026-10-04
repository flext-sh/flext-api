# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
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
from flext_core import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_web import d, e, h, r, x

    from flext_api import services
    from flext_api._config import FlextApiConfig, config
    from flext_api._settings import FlextApiSettings, settings
    from flext_api.api import FlextApi, api
    from flext_api.base import FlextApiServiceBase, s
    from flext_api.cli import FlextApiCli, main
    from flext_api.constants import FlextApiConstants, c
    from flext_api.models import FlextApiModels, m
    from flext_api.protocols import (
        FlextApiProtocols,
        FlextApiProtocolsTransports,
        HttpxAsyncClient,
        HttpxClient,
        HttpxHTTPError,
        HttpxHTTPStatusError,
        HttpxRequestError,
        HttpxResponse,
        HttpxTimeoutException,
        p,
    )
    from flext_api.services.async_client import FlextApiAsyncClient
    from flext_api.services.base_client import FlextApiClientBase
    from flext_api.services.client import FlextApiClient
    from flext_api.typings import FlextApiTypes, t
    from flext_api.utilities import FlextApiUtilities, u


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
    "FlextApiProtocolsTransports",
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
    "config",
    "d",
    "e",
    "h",
    "m",
    "main",
    "p",
    "r",
    "s",
    "services",
    "settings",
    "t",
    "u",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            "._config": ("FlextApiConfig", "config"),
            "._settings": ("FlextApiSettings", "settings"),
            ".api": ("FlextApi", "api"),
            ".base": ("FlextApiServiceBase", "s"),
            ".cli": ("FlextApiCli", "main"),
            ".constants": ("FlextApiConstants", "c"),
            ".models": ("FlextApiModels", "m"),
            ".protocols": (
                "FlextApiProtocols",
                "FlextApiProtocolsTransports",
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
            "flext_web": ("d", "e", "h", "r", "x"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
