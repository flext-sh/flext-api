# AUTO-GENERATED FILE — Regenerate with: make gen
"""Typings package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_api._typings.serialization import (
        FlextApiTypingsSerialization as FlextApiTypingsSerialization,
    )
_LAZY_IMPORTS = build_lazy_import_map({
    ".serialization": ("FlextApiTypingsSerialization",)
})


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
