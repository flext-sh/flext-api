"""Lazy export wiring for the flext_api package."""

from __future__ import annotations

import sys
from collections.abc import Callable, Mapping, Sequence
from types import ModuleType
from typing import Final

from flext_api._exports import FLEXT_API_LAZY_IMPORTS
from flext_core import FlextTypes
from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

type LazyModuleExport = (
    FlextTypes.JsonValue
    | Mapping[str, LazyModuleExport]
    | Sequence[str]
    | ModuleType
    | type
    | Callable[..., LazyModuleExport]
    | Callable[..., FlextTypes.JsonValue | Sequence[str] | ModuleType | type | None]
    | None
)

_MODULE_NAME: Final = "flext_api"

_LAZY_IMPORTS = FLEXT_API_LAZY_IMPORTS

__all__: list[str] = ["LazyModuleExport"]


def __getattr__(name: str) -> LazyModuleExport:
    """Lazy-load package attributes on first access."""
    return lazy_getattr(
        name,
        _LAZY_IMPORTS,
        vars(sys.modules[_MODULE_NAME]),
        _MODULE_NAME,
    )


def __dir__() -> list[str]:
    """Return available package exports for autocomplete."""
    return sorted(_LAZY_IMPORTS)


cleanup_submodule_namespace(_MODULE_NAME, _LAZY_IMPORTS)
