# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import api, d, e, h, r, td, tf, tk, tm, x

    from flext_api import (
        FlextApi,
        FlextApiCli,
        FlextApiConfig,
        FlextApiConfigNamespace,
        FlextApiConstants,
        FlextApiModels,
        FlextApiModelsConfig,
        FlextApiProtocols,
        FlextApiProtocolsTransports,
        FlextApiServiceBase,
        FlextApiSettings,
        FlextApiTypes,
        FlextApiUtilities,
        FlextApiVersion,
        HttpxAsyncClient,
        HttpxClient,
        HttpxHTTPError,
        HttpxHTTPStatusError,
        HttpxRequestError,
        HttpxResponse,
        HttpxTimeoutException,
        config,
        main,
        settings,
    )
    from tests.base import TestsFlextApiServiceBase, s
    from tests.constants import TestsFlextApiConstants, c
    from tests.models import TestsFlextApiModels, m
    from tests.protocols import TestsFlextApiProtocols, p
    from tests.settings import TestsFlextApiSettings
    from tests.typings import TestsFlextApiTypes, t
    from tests.unit import TestsFlextApiModelContract
    from tests.utilities import TestsFlextApiUtilities, u


__all__: tuple[str, ...] = (
    "FlextApi",
    "FlextApiCli",
    "FlextApiConfig",
    "FlextApiConfigNamespace",
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
    "TestsFlextApiConstants",
    "TestsFlextApiModelContract",
    "TestsFlextApiModels",
    "TestsFlextApiProtocols",
    "TestsFlextApiServiceBase",
    "TestsFlextApiSettings",
    "TestsFlextApiTypes",
    "TestsFlextApiUtilities",
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
    "settings",
    "t",
    "td",
    "tf",
    "tk",
    "tm",
    "u",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "FlextApi": "flext_api",
        "FlextApiCli": "flext_api",
        "FlextApiConfig": "flext_api",
        "FlextApiConfigNamespace": "flext_api",
        "FlextApiConstants": "flext_api",
        "FlextApiModels": "flext_api",
        "FlextApiModelsConfig": "flext_api",
        "FlextApiProtocols": "flext_api",
        "FlextApiProtocolsTransports": "flext_api",
        "FlextApiServiceBase": "flext_api",
        "FlextApiSettings": "flext_api",
        "FlextApiTypes": "flext_api",
        "FlextApiUtilities": "flext_api",
        "FlextApiVersion": "flext_api",
        "HttpxAsyncClient": "flext_api",
        "HttpxClient": "flext_api",
        "HttpxHTTPError": "flext_api",
        "HttpxHTTPStatusError": "flext_api",
        "HttpxRequestError": "flext_api",
        "HttpxResponse": "flext_api",
        "HttpxTimeoutException": "flext_api",
        "TestsFlextApiConstants": ".constants",
        "TestsFlextApiModelContract": ".unit",
        "TestsFlextApiModels": ".models",
        "TestsFlextApiProtocols": ".protocols",
        "TestsFlextApiServiceBase": ".base",
        "TestsFlextApiSettings": ".settings",
        "TestsFlextApiTypes": ".typings",
        "TestsFlextApiUtilities": ".utilities",
        "api": "flext_tests",
        "c": ".constants",
        "config": "flext_api",
        "d": "flext_tests",
        "e": "flext_tests",
        "h": "flext_tests",
        "m": ".models",
        "main": "flext_api",
        "p": ".protocols",
        "r": "flext_tests",
        "s": ".base",
        "settings": "flext_api",
        "t": ".typings",
        "td": "flext_tests",
        "tf": "flext_tests",
        "tk": "flext_tests",
        "tm": "flext_tests",
        "u": ".utilities",
        "x": "flext_tests",
    },
    public_exports=__all__,
)
