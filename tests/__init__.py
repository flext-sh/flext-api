# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if _t.TYPE_CHECKING:
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from tests.constants import TestsFlextApiConstants, TestsFlextApiConstants as c
    from tests.models import TestsFlextApiModels, TestsFlextApiModels as m
    from tests.protocols import TestsFlextApiProtocols, TestsFlextApiProtocols as p
    from tests.typings import TestsFlextApiTypes, TestsFlextApiTypes as t
    from tests.utilities import TestsFlextApiUtilities, TestsFlextApiUtilities as u
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".constants": ("TestsFlextApiConstants",),
        ".models": ("TestsFlextApiModels",),
        ".protocols": ("TestsFlextApiProtocols",),
        ".typings": ("TestsFlextApiTypes",),
        ".utilities": ("TestsFlextApiUtilities",),
    },
    alias_groups={
        ".constants": (("c", "TestsFlextApiConstants"),),
        ".models": (("m", "TestsFlextApiModels"),),
        ".protocols": (("p", "TestsFlextApiProtocols"),),
        ".typings": (("t", "TestsFlextApiTypes"),),
        ".utilities": (("u", "TestsFlextApiUtilities"),),
        "flext_core.decorators": (("d", "FlextDecorators"),),
        "flext_core.exceptions": (("e", "FlextExceptions"),),
        "flext_core.handlers": (("h", "FlextHandlers"),),
        "flext_core.mixins": (("x", "FlextMixins"),),
        "flext_core.result": (("r", "FlextResult"),),
        "flext_core.service": (("s", "FlextService"),),
    },
)

__all__ = [
    "TestsFlextApiConstants",
    "TestsFlextApiModels",
    "TestsFlextApiProtocols",
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
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
