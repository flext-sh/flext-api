# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_tests import d, e, h, r, s, x

    from tests import unit
    from tests.constants import FlextApiTestConstants, FlextApiTestConstants as c
    from tests.models import FlextApiTestModels, FlextApiTestModels as m
    from tests.protocols import FlextApiTestProtocols, FlextApiTestProtocols as p
    from tests.typings import FlextApiTestTypes, FlextApiTestTypes as t
    from tests.unit.test_serializers import TestMessagePackUnpackb
    from tests.unit.test_smoke import test_package_imports_main_facade
    from tests.utilities import FlextApiTestUtilities, FlextApiTestUtilities as u

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlextApiTestConstants": ["tests.constants", "FlextApiTestConstants"],
    "FlextApiTestModels": ["tests.models", "FlextApiTestModels"],
    "FlextApiTestProtocols": ["tests.protocols", "FlextApiTestProtocols"],
    "FlextApiTestTypes": ["tests.typings", "FlextApiTestTypes"],
    "FlextApiTestUtilities": ["tests.utilities", "FlextApiTestUtilities"],
    "TestMessagePackUnpackb": ["tests.unit.test_serializers", "TestMessagePackUnpackb"],
    "c": ["tests.constants", "FlextApiTestConstants"],
    "d": ["flext_tests", "d"],
    "e": ["flext_tests", "e"],
    "h": ["flext_tests", "h"],
    "m": ["tests.models", "FlextApiTestModels"],
    "p": ["tests.protocols", "FlextApiTestProtocols"],
    "r": ["flext_tests", "r"],
    "s": ["flext_tests", "s"],
    "t": ["tests.typings", "FlextApiTestTypes"],
    "test_package_imports_main_facade": ["tests.unit.test_smoke", "test_package_imports_main_facade"],
    "u": ["tests.utilities", "FlextApiTestUtilities"],
    "unit": ["tests.unit", ""],
    "x": ["flext_tests", "x"],
}

__all__ = [
    "FlextApiTestConstants",
    "FlextApiTestModels",
    "FlextApiTestProtocols",
    "FlextApiTestTypes",
    "FlextApiTestUtilities",
    "TestMessagePackUnpackb",
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
    "u",
    "unit",
    "x",
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
