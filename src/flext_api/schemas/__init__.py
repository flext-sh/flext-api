# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Schema validation systems for flext-api.

Provides schema validation for:
- OpenAPI 3.x specifications
- JSON Schema validation
- AsyncAPI specifications

See TRANSFORMATION_PLAN.md - Phase 5 for implementation details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import FlextTypes

    from flext_api.schemas.asyncapi import AsyncAPISchemaValidator
    from flext_api.schemas.jsonschema import JSONSchemaValidator
    from flext_api.schemas.openapi import OpenAPISchemaValidator

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "AsyncAPISchemaValidator": (
        "flext_api.schemas.asyncapi",
        "AsyncAPISchemaValidator",
    ),
    "JSONSchemaValidator": ("flext_api.schemas.jsonschema", "JSONSchemaValidator"),
    "OpenAPISchemaValidator": ("flext_api.schemas.openapi", "OpenAPISchemaValidator"),
}

__all__ = [
    "AsyncAPISchemaValidator",
    "JSONSchemaValidator",
    "OpenAPISchemaValidator",
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
