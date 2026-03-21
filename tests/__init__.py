# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Tests package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

    from . import unit as unit
    from .constants import TestsFlextApiConstants, TestsFlextApiConstants as c
    from .models import TestsFlextApiModels, TestsFlextApiModels as m
    from .protocols import TestsFlextApiProtocols, TestsFlextApiProtocols as p
    from .typings import TestsFlextApiTypes, TestsFlextApiTypes as t
    from .unit.test_serializers import TestMessagePackUnpackb
    from .unit.test_smoke import test_package_imports_main_facade
    from .utilities import TestsFlextApiUtilities, TestsFlextApiUtilities as u

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "TestMessagePackUnpackb": ("tests.unit.test_serializers", "TestMessagePackUnpackb"),
    "TestsFlextApiConstants": ("tests.constants", "TestsFlextApiConstants"),
    "TestsFlextApiModels": ("tests.models", "TestsFlextApiModels"),
    "TestsFlextApiProtocols": ("tests.protocols", "TestsFlextApiProtocols"),
    "TestsFlextApiTypes": ("tests.typings", "TestsFlextApiTypes"),
    "TestsFlextApiUtilities": ("tests.utilities", "TestsFlextApiUtilities"),
    "c": ("tests.constants", "TestsFlextApiConstants"),
    "m": ("tests.models", "TestsFlextApiModels"),
    "p": ("tests.protocols", "TestsFlextApiProtocols"),
    "t": ("tests.typings", "TestsFlextApiTypes"),
    "test_package_imports_main_facade": (
        "tests.unit.test_smoke",
        "test_package_imports_main_facade",
    ),
    "u": ("tests.utilities", "TestsFlextApiUtilities"),
    "unit": ("tests.unit", ""),
}

__all__ = [
    "TestMessagePackUnpackb",
    "TestsFlextApiConstants",
    "TestsFlextApiModels",
    "TestsFlextApiProtocols",
    "TestsFlextApiTypes",
    "TestsFlextApiUtilities",
    "c",
    "m",
    "p",
    "t",
    "test_package_imports_main_facade",
    "u",
    "unit",
]


_LAZY_CACHE: dict[str, FlextTypes.ModuleExport] = {}


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


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete.

    Returns:
        List of public names from module exports.

    """
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
