"""Lazy export wiring for flext_api.schemas."""

from __future__ import annotations

import sys
from collections.abc import Callable, Mapping, Sequence
from types import ModuleType
from typing import Final

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

_MODULE_NAME: Final = "flext_api.schemas"

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "AsyncAPISchemaValidator": (
        "flext_api.schemas.asyncapi",
        "AsyncAPISchemaValidator",
    ),
    "JSONSchemaValidator": ("flext_api.schemas.jsonschema", "JSONSchemaValidator"),
    "OpenAPISchemaValidator": ("flext_api.schemas.openapi", "OpenAPISchemaValidator"),
}

__all__ = list(_LAZY_IMPORTS)


def __getattr__(name: str) -> LazyModuleExport:
    """Lazy-load schema exports on first access."""
    return lazy_getattr(
        name, _LAZY_IMPORTS, vars(sys.modules[_MODULE_NAME]), _MODULE_NAME
    )


def __dir__() -> list[str]:
    """Return available schema exports for autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(_MODULE_NAME, _LAZY_IMPORTS)
