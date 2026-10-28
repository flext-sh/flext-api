# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_web import cli, d, e, h, r, web, x

    from flext_api.__version__ import (
        FlextApiVersion,
        __author__,
        __author_email__,
        __description__,
        __license__,
        __title__,
        __url__,
        __version__,
        __version_info__,
    )
    from flext_api._config import FlextApiConfig, config
    from flext_api._settings import FlextApiSettings, settings
    from flext_api.api import FlextApi, api
    from flext_api.base import FlextApiServiceBase, s
    from flext_api.cli import FlextApiCli, main
    from flext_api.constants import FlextApiConstants, c
    from flext_api.models import FlextApiModels, FlextApiModelsConfig, m
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
    from flext_api.typings import FlextApiTypes, t
    from flext_api.utilities import FlextApiUtilities, u


__all__: tuple[str, ...] = (
    "FlextApi",
    "FlextApiCli",
    "FlextApiConfig",
    "FlextApiConstants",
    "FlextApiModels",
    "FlextApiModelsConfig",
    "FlextApiProtocols",
    "FlextApiProtocolsTransports",
    "FlextApiServiceBase",
    "FlextApiSettings",
    "FlextApiTypes",
    "FlextApiUtilities",
    "FlextApiVersion",
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
    "d",
    "e",
    "h",
    "m",
    "main",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "u",
    "web",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextApi": ".api",
        "FlextApiCli": ".cli",
        "FlextApiConfig": "._config",
        "FlextApiConstants": ".constants",
        "FlextApiModels": ".models",
        "FlextApiModelsConfig": ".models",
        "FlextApiProtocols": ".protocols",
        "FlextApiProtocolsTransports": ".protocols",
        "FlextApiServiceBase": ".base",
        "FlextApiSettings": "._settings",
        "FlextApiTypes": ".typings",
        "FlextApiUtilities": ".utilities",
        "FlextApiVersion": ".__version__",
        "HttpxAsyncClient": ".protocols",
        "HttpxClient": ".protocols",
        "HttpxHTTPError": ".protocols",
        "HttpxHTTPStatusError": ".protocols",
        "HttpxRequestError": ".protocols",
        "HttpxResponse": ".protocols",
        "HttpxTimeoutException": ".protocols",
        "__author__": ".__version__",
        "__author_email__": ".__version__",
        "__description__": ".__version__",
        "__license__": ".__version__",
        "__title__": ".__version__",
        "__url__": ".__version__",
        "__version_info__": ".__version__",
        "api": ".api",
        "c": ".constants",
        "cli": "flext_web",
        "config": "._config",
        "d": "flext_web",
        "e": "flext_web",
        "h": "flext_web",
        "m": ".models",
        "main": ".cli",
        "p": ".protocols",
        "r": "flext_web",
        "s": ".base",
        "settings": "._settings",
        "t": ".typings",
        "u": ".utilities",
        "web": "flext_web",
        "x": "flext_web",
    }),
    public_exports=__all__,
)

if not TYPE_CHECKING:
    from flext_api.__version__ import __version__
