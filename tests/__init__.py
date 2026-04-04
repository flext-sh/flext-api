# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _t.TYPE_CHECKING:
    import tests.constants as _tests_constants

    constants = _tests_constants
    import tests.models as _tests_models
    from tests.constants import FlextApiTestConstants, FlextApiTestConstants as c

    models = _tests_models
    import tests.protocols as _tests_protocols
    from tests.models import FlextApiTestModels, FlextApiTestModels as m

    protocols = _tests_protocols
    import tests.typings as _tests_typings
    from tests.protocols import FlextApiTestProtocols, FlextApiTestProtocols as p

    typings = _tests_typings
    import tests.unit as _tests_unit
    from tests.typings import FlextApiTestTypes, FlextApiTestTypes as t

    unit = _tests_unit
    import tests.utilities as _tests_utilities
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

    utilities = _tests_utilities
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from tests.utilities import FlextApiTestUtilities, FlextApiTestUtilities as u
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
