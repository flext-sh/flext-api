# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import *

    from tests import constants, models, protocols, typings, utilities
    from tests.constants import *
    from tests.models import *
    from tests.protocols import *
    from tests.typings import *
    from tests.unit import *
    from tests.utilities import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "FlextApiTestConstants": "tests.constants",
    "FlextApiTestModels": "tests.models",
    "FlextApiTestProtocols": "tests.protocols",
    "FlextApiTestTypes": "tests.typings",
    "FlextApiTestUtilities": "tests.utilities",
    "TestConstants": "tests.unit.test_smoke",
    "TestFacadeInheritance": "tests.unit.test_smoke",
    "TestMessagePackUnpackb": "tests.unit.test_serializers",
    "TestModels": "tests.unit.test_smoke",
    "TestSerializers": "tests.unit.test_smoke",
    "c": ["tests.constants", "FlextApiTestConstants"],
    "constants": "tests.constants",
    "d": "flext_tests",
    "e": "flext_tests",
    "h": "flext_tests",
    "m": ["tests.models", "FlextApiTestModels"],
    "models": "tests.models",
    "p": ["tests.protocols", "FlextApiTestProtocols"],
    "protocols": "tests.protocols",
    "r": "flext_tests",
    "s": "flext_tests",
    "t": ["tests.typings", "FlextApiTestTypes"],
    "test_package_imports_main_facade": "tests.unit.test_smoke",
    "test_serializers": "tests.unit.test_serializers",
    "test_smoke": "tests.unit.test_smoke",
    "typings": "tests.typings",
    "u": ["tests.utilities", "FlextApiTestUtilities"],
    "unit": "tests.unit",
    "utilities": "tests.utilities",
    "x": "flext_tests",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, sorted(_LAZY_IMPORTS))
