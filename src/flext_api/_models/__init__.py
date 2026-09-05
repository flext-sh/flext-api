# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api. Models package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from types import MappingProxyType

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from .client import FlextApiModelsClient
    from .request import FlextApiModelsRequest
    from .response import FlextApiModelsResponse
    from .storage import FlextApiModelsStorage
    from .webhook import FlextApiModelsWebhook
__all__: tuple[str, ...] = (
    "FlextApiModelsClient",
    "FlextApiModelsRequest",
    "FlextApiModelsResponse",
    "FlextApiModelsStorage",
    "FlextApiModelsWebhook",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".client": ("FlextApiModelsClient",),
            ".request": ("FlextApiModelsRequest",),
            ".response": ("FlextApiModelsResponse",),
            ".storage": ("FlextApiModelsStorage",),
            ".webhook": ("FlextApiModelsWebhook",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
