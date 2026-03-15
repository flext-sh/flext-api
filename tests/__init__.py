# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Tests package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

    from tests import unit
    from tests.constants import TestsFlextApiConstants, TestsFlextApiConstants as c
    from tests.models import TestsFlextApiModels, TestsFlextApiModels as m
    from tests.protocols import TestsFlextApiProtocols, TestsFlextApiProtocols as p
    from tests.typings import TestsFlextApiTypes, TestsFlextApiTypes as t
    from tests.unit.test_serializers import TestMessagePackUnpackb
    from tests.unit.test_smoke import test_package_imports_main_facade
    from tests.utilities import TestsFlextApiUtilities, TestsFlextApiUtilities as u

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


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
