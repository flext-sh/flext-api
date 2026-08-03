# @generated AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api. Models package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from .client import FlextApiModelsClient as FlextApiModelsClient
    from .request import FlextApiModelsRequest as FlextApiModelsRequest
    from .response import FlextApiModelsResponse as FlextApiModelsResponse
    from .storage import FlextApiModelsStorage as FlextApiModelsStorage
    from .webhook import FlextApiModelsWebhook as FlextApiModelsWebhook

_LAZY_MODULES: dict[str, tuple[str, ...]] = {
    ".client": ("FlextApiModelsClient",),
    ".request": ("FlextApiModelsRequest",),
    ".response": ("FlextApiModelsResponse",),
    ".storage": ("FlextApiModelsStorage",),
    ".webhook": ("FlextApiModelsWebhook",),
}


_LAZY_ALIAS_GROUPS: dict[str, tuple[tuple[str, str], ...]] = {}


_LAZY_IMPORTS = build_lazy_import_map(
    _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
)

_PUBLIC_EXPORTS: tuple[str, ...] = (
    "FlextApiModelsClient",
    "FlextApiModelsRequest",
    "FlextApiModelsResponse",
    "FlextApiModelsStorage",
    "FlextApiModelsWebhook",
)

__all__: tuple[str, ...] = tuple(_PUBLIC_EXPORTS)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
