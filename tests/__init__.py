# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import build_lazy_import_map, install_lazy_exports

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

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".base": ("TestsFlextApiServiceBase", "s"),
            ".constants": ("TestsFlextApiConstants",),
            ".models": ("TestsFlextApiModels",),
            ".protocols": ("TestsFlextApiProtocols",),
            ".settings": ("TestsFlextApiSettings",),
            ".typings": ("TestsFlextApiTypes",),
            ".unit": ("unit",),
            ".utilities": ("TestsFlextApiUtilities",),
            "flext_api": ("c", "d", "e", "h", "m", "p", "r", "t", "u", "x"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
