# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests import (
        constants as constants,
        models as models,
        protocols as protocols,
        typings as typings,
        unit as unit,
        utilities as utilities,
    )
    from tests.constants import (
        FlextApiTestConstants as FlextApiTestConstants,
        FlextApiTestConstants as c,
    )
    from tests.models import (
        FlextApiTestModels as FlextApiTestModels,
        FlextApiTestModels as m,
    )
    from tests.protocols import (
        FlextApiTestProtocols as FlextApiTestProtocols,
        FlextApiTestProtocols as p,
    )
    from tests.typings import (
        FlextApiTestTypes as FlextApiTestTypes,
        FlextApiTestTypes as t,
    )
    from tests.unit import (
        test_serializers as test_serializers,
        test_smoke as test_smoke,
    )
    from tests.unit.test_serializers import (
        TestMessagePackUnpackb as TestMessagePackUnpackb,
    )
    from tests.unit.test_smoke import (
        TestConstants as TestConstants,
        TestFacadeInheritance as TestFacadeInheritance,
        TestModels as TestModels,
        TestSerializers as TestSerializers,
        test_package_imports_main_facade as test_package_imports_main_facade,
    )
    from tests.utilities import (
        FlextApiTestUtilities as FlextApiTestUtilities,
        FlextApiTestUtilities as u,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlextApiTestConstants": ["tests.constants", "FlextApiTestConstants"],
    "FlextApiTestModels": ["tests.models", "FlextApiTestModels"],
    "FlextApiTestProtocols": ["tests.protocols", "FlextApiTestProtocols"],
    "FlextApiTestTypes": ["tests.typings", "FlextApiTestTypes"],
    "FlextApiTestUtilities": ["tests.utilities", "FlextApiTestUtilities"],
    "TestConstants": ["tests.unit.test_smoke", "TestConstants"],
    "TestFacadeInheritance": ["tests.unit.test_smoke", "TestFacadeInheritance"],
    "TestMessagePackUnpackb": ["tests.unit.test_serializers", "TestMessagePackUnpackb"],
    "TestModels": ["tests.unit.test_smoke", "TestModels"],
    "TestSerializers": ["tests.unit.test_smoke", "TestSerializers"],
    "c": ["tests.constants", "FlextApiTestConstants"],
    "constants": ["tests.constants", ""],
    "d": ["flext_tests", "d"],
    "e": ["flext_tests", "e"],
    "h": ["flext_tests", "h"],
    "m": ["tests.models", "FlextApiTestModels"],
    "models": ["tests.models", ""],
    "p": ["tests.protocols", "FlextApiTestProtocols"],
    "protocols": ["tests.protocols", ""],
    "r": ["flext_tests", "r"],
    "s": ["flext_tests", "s"],
    "t": ["tests.typings", "FlextApiTestTypes"],
    "test_package_imports_main_facade": [
        "tests.unit.test_smoke",
        "test_package_imports_main_facade",
    ],
    "test_serializers": ["tests.unit.test_serializers", ""],
    "test_smoke": ["tests.unit.test_smoke", ""],
    "typings": ["tests.typings", ""],
    "u": ["tests.utilities", "FlextApiTestUtilities"],
    "unit": ["tests.unit", ""],
    "utilities": ["tests.utilities", ""],
    "x": ["flext_tests", "x"],
}

_EXPORTS: Sequence[str] = [
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
