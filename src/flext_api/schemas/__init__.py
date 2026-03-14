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

from typing import TYPE_CHECKING, Any

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_api.schemas.asyncapi import AsyncAPISchemaValidator
    from flext_api.schemas.jsonschema import JSONSchemaValidator
    from flext_api.schemas.openapi import OpenAPISchemaValidator

# Lazy import mapping: export_name -> (module_path, attr_name)
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


def __getattr__(
    name: str,
) -> Any:  # JUSTIFIED: Ruff (any-type) with PEP 562 dynamic module exports — https://docs.astral.sh/ruff/rules/any-type/
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
