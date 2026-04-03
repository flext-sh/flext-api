# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.decorators import FlextDecorators as d
from flext_core.exceptions import FlextExceptions as e
from flext_core.handlers import FlextHandlers as h
from flext_core.lazy import install_lazy_exports, merge_lazy_imports
from flext_core.mixins import FlextMixins as x
from flext_core.result import FlextResult as r
from flext_core.service import FlextService as s
from tests.constants import FlextApiTestConstants, FlextApiTestConstants as c
from tests.models import FlextApiTestModels, FlextApiTestModels as m
from tests.protocols import FlextApiTestProtocols, FlextApiTestProtocols as p
from tests.typings import FlextApiTestTypes, FlextApiTestTypes as t
from tests.unit.test_serializers import TestMessagePackUnpackb
from tests.unit.test_smoke import (
    TestConstants,
    TestFacadeInheritance,
    TestModels,
    TestSerializers,
    test_package_imports_main_facade,
)
from tests.utilities import FlextApiTestUtilities, FlextApiTestUtilities as u

if _t.TYPE_CHECKING:
    import tests.constants as _tests_constants

    constants = _tests_constants
    import tests.models as _tests_models

    models = _tests_models
    import tests.protocols as _tests_protocols

    protocols = _tests_protocols
    import tests.typings as _tests_typings

    typings = _tests_typings
    import tests.unit as _tests_unit

    unit = _tests_unit
    import tests.unit.test_serializers as _tests_unit_test_serializers

    test_serializers = _tests_unit_test_serializers
    import tests.unit.test_smoke as _tests_unit_test_smoke

    test_smoke = _tests_unit_test_smoke
    import tests.utilities as _tests_utilities

    utilities = _tests_utilities

    _ = (
        FlextApiTestConstants,
        FlextApiTestModels,
        FlextApiTestProtocols,
        FlextApiTestTypes,
        FlextApiTestUtilities,
        TestConstants,
        TestFacadeInheritance,
        TestMessagePackUnpackb,
        TestModels,
        TestSerializers,
        c,
        constants,
        d,
        e,
        h,
        m,
        models,
        p,
        protocols,
        r,
        s,
        t,
        test_package_imports_main_facade,
        test_serializers,
        test_smoke,
        typings,
        u,
        unit,
        utilities,
        x,
    )
_LAZY_IMPORTS = merge_lazy_imports(
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

__all__ = [
    "FlextApiTestConstants",
    "FlextApiTestModels",
    "FlextApiTestProtocols",
    "FlextApiTestTypes",
    "FlextApiTestUtilities",
    "TestConstants",
    "TestFacadeInheritance",
    "TestMessagePackUnpackb",
    "TestModels",
    "TestSerializers",
    "c",
    "constants",
    "d",
    "e",
    "h",
    "m",
    "models",
    "p",
    "protocols",
    "r",
    "s",
    "t",
    "test_package_imports_main_facade",
    "test_serializers",
    "test_smoke",
    "typings",
    "u",
    "unit",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
