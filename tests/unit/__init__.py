# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Unit package."""

from __future__ import annotations

import typing as _t

from flext_core.constants import FlextConstants as c
from flext_core.decorators import FlextDecorators as d
from flext_core.exceptions import FlextExceptions as e
from flext_core.handlers import FlextHandlers as h
from flext_core.lazy import install_lazy_exports
from flext_core.mixins import FlextMixins as x
from flext_core.models import FlextModels as m
from flext_core.protocols import FlextProtocols as p
from flext_core.result import FlextResult as r
from flext_core.service import FlextService as s
from flext_core.typings import FlextTypes as t
from flext_core.utilities import FlextUtilities as u
from tests.unit.test_serializers import TestMessagePackUnpackb
from tests.unit.test_smoke import (
    TestConstants,
    TestFacadeInheritance,
    TestModels,
    TestSerializers,
    test_package_imports_main_facade,
)

if _t.TYPE_CHECKING:
    import tests.unit.test_serializers as _tests_unit_test_serializers

    test_serializers = _tests_unit_test_serializers
    import tests.unit.test_smoke as _tests_unit_test_smoke

    test_smoke = _tests_unit_test_smoke

    _ = (
        TestConstants,
        TestFacadeInheritance,
        TestMessagePackUnpackb,
        TestModels,
        TestSerializers,
        c,
        d,
        e,
        h,
        m,
        p,
        r,
        s,
        t,
        test_package_imports_main_facade,
        test_serializers,
        test_smoke,
        u,
        x,
    )
_LAZY_IMPORTS = {
    "TestConstants": "tests.unit.test_smoke",
    "TestFacadeInheritance": "tests.unit.test_smoke",
    "TestMessagePackUnpackb": "tests.unit.test_serializers",
    "TestModels": "tests.unit.test_smoke",
    "TestSerializers": "tests.unit.test_smoke",
    "c": ("flext_core.constants", "FlextConstants"),
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("flext_core.models", "FlextModels"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "t": ("flext_core.typings", "FlextTypes"),
    "test_package_imports_main_facade": "tests.unit.test_smoke",
    "test_serializers": "tests.unit.test_serializers",
    "test_smoke": "tests.unit.test_smoke",
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
    "TestConstants",
    "TestFacadeInheritance",
    "TestMessagePackUnpackb",
    "TestModels",
    "TestSerializers",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "test_package_imports_main_facade",
    "test_serializers",
    "test_smoke",
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
