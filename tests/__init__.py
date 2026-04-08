# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

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
_LAZY_IMPORTS = {
    "TestsFlextApiConstants": ".constants",
    "TestsFlextApiModels": ".models",
    "TestsFlextApiProtocols": ".protocols",
    "TestsFlextApiTypes": ".typings",
    "TestsFlextApiUtilities": ".utilities",
    "c": (".constants", "TestsFlextApiConstants"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": (".models", "TestsFlextApiModels"),
    "p": (".protocols", "TestsFlextApiProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "t": (".typings", "TestsFlextApiTypes"),
    "u": (".utilities", "TestsFlextApiUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}

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
