# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Unit package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
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

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "TestConstants": ["tests.unit.test_smoke", "TestConstants"],
    "TestFacadeInheritance": ["tests.unit.test_smoke", "TestFacadeInheritance"],
    "TestMessagePackUnpackb": ["tests.unit.test_serializers", "TestMessagePackUnpackb"],
    "TestModels": ["tests.unit.test_smoke", "TestModels"],
    "TestSerializers": ["tests.unit.test_smoke", "TestSerializers"],
    "test_package_imports_main_facade": [
        "tests.unit.test_smoke",
        "test_package_imports_main_facade",
    ],
    "test_serializers": ["tests.unit.test_serializers", ""],
    "test_smoke": ["tests.unit.test_smoke", ""],
}

_EXPORTS: Sequence[str] = [
    "TestConstants",
    "TestFacadeInheritance",
    "TestMessagePackUnpackb",
    "TestModels",
    "TestSerializers",
    "test_package_imports_main_facade",
    "test_serializers",
    "test_smoke",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
