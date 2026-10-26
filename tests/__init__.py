# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import td, tf, tk, tm

    from flext_api import api, c, config, d, e, h, m, main, p, r, settings, t, u, web, x
    from tests.base import TestsFlextApiServiceBase, s
    from tests.constants import TestsFlextApiConstants
    from tests.models import TestsFlextApiModels
    from tests.protocols import TestsFlextApiProtocols
    from tests.settings import TestsFlextApiSettings
    from tests.typings import TestsFlextApiTypes
    from tests.utilities import TestsFlextApiUtilities


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
    "web",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "TestsFlextApiConstants": ".constants",
        "TestsFlextApiModels": ".models",
        "TestsFlextApiProtocols": ".protocols",
        "TestsFlextApiServiceBase": ".base",
        "TestsFlextApiSettings": ".settings",
        "TestsFlextApiTypes": ".typings",
        "TestsFlextApiUtilities": ".utilities",
        "api": "flext_api",
        "c": "flext_api",
        "config": "flext_api",
        "d": "flext_api",
        "e": "flext_api",
        "h": "flext_api",
        "m": "flext_api",
        "main": "flext_api",
        "p": "flext_api",
        "r": "flext_api",
        "s": ".base",
        "settings": "flext_api",
        "t": "flext_api",
        "td": "flext_tests",
        "tf": "flext_tests",
        "tk": "flext_tests",
        "tm": "flext_tests",
        "u": "flext_api",
        "web": "flext_api",
        "x": "flext_api",
    }),
    public_exports=__all__,
)
