# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_api import c, d, e, h, m, p, r, t, u, x
    from tests import unit
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
    "unit",
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
        "c": "flext_api",
        "d": "flext_api",
        "e": "flext_api",
        "h": "flext_api",
        "m": "flext_api",
        "p": "flext_api",
        "r": "flext_api",
        "s": ".base",
        "t": "flext_api",
        "u": "flext_api",
        "unit": ".unit",
        "x": "flext_api",
    }),
    public_exports=__all__,
)
