# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from tests import constants, models, protocols, typings, unit, utilities
    from tests.constants import FlextApiTestConstants, FlextApiTestConstants as c
    from tests.models import FlextApiTestModels, FlextApiTestModels as m
    from tests.protocols import FlextApiTestProtocols, FlextApiTestProtocols as p
    from tests.typings import FlextApiTestTypes, FlextApiTestTypes as t
    from tests.unit import (
        TestConstants,
        TestFacadeInheritance,
        TestMessagePackUnpackb,
        TestModels,
        TestSerializers,
        test_package_imports_main_facade,
        test_serializers,
        test_smoke,
    )
    from tests.utilities import FlextApiTestUtilities, FlextApiTestUtilities as u

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = merge_lazy_imports(
    ("tests.unit",),
    {
        "FlextApiTestConstants": "tests.constants",
        "FlextApiTestModels": "tests.models",
        "FlextApiTestProtocols": "tests.protocols",
        "FlextApiTestTypes": "tests.typings",
        "FlextApiTestUtilities": "tests.utilities",
        "c": ("tests.constants", "FlextApiTestConstants"),
        "constants": "tests.constants",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "h": ("flext_core.handlers", "FlextHandlers"),
        "m": ("tests.models", "FlextApiTestModels"),
        "models": "tests.models",
        "p": ("tests.protocols", "FlextApiTestProtocols"),
        "protocols": "tests.protocols",
        "r": ("flext_core.result", "FlextResult"),
        "s": ("flext_core.service", "FlextService"),
        "t": ("tests.typings", "FlextApiTestTypes"),
        "typings": "tests.typings",
        "u": ("tests.utilities", "FlextApiTestUtilities"),
        "unit": "tests.unit",
        "utilities": "tests.utilities",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
