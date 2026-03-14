# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Unit package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

    from tests.unit.test_serializers import TestMessagePackUnpackb
    from tests.unit.test_smoke import test_package_imports_main_facade

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "TestMessagePackUnpackb": ("tests.unit.test_serializers", "TestMessagePackUnpackb"),
    "test_package_imports_main_facade": (
        "tests.unit.test_smoke",
        "test_package_imports_main_facade",
    ),
}

__all__ = [
    "TestMessagePackUnpackb",
    "test_package_imports_main_facade",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
