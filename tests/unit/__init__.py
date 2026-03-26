# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Unit package."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import FlextTypes

    from tests.unit.test_serializers import TestMessagePackUnpackb
    from tests.unit.test_smoke import (
        TestConstants,
        TestFacadeInheritance,
        TestModels,
        TestSerializers,
        test_package_imports_main_facade,
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
}

__all__ = [
    "TestConstants",
    "TestFacadeInheritance",
    "TestMessagePackUnpackb",
    "TestModels",
    "TestSerializers",
    "test_package_imports_main_facade",
]


_LAZY_CACHE: MutableMapping[str, FlextTypes.ModuleExport] = {}


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562).

    A local cache ``_LAZY_CACHE`` persists resolved objects across repeated
    accesses during process lifetime.

    Args:
        name: Attribute name requested by dir()/import.

    Returns:
        Lazy-loaded module export type.

    Raises:
        AttributeError: If attribute not registered.

    """
    if name in _LAZY_CACHE:
        return _LAZY_CACHE[name]

    value = lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)
    _LAZY_CACHE[name] = value
    return value


def __dir__() -> Sequence[str]:
    """Return list of available attributes for dir() and autocomplete.

    Returns:
        List of public names from module exports.

    """
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
