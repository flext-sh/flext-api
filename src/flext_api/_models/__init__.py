# AUTO-GENERATED FILE — Regenerate with: make gen
"""Models package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_api._models.client import FlextApiModelsClient
    from flext_api._models.request import FlextApiModelsRequest
    from flext_api._models.response import FlextApiModelsResponse
    from flext_api._models.storage import FlextApiModelsStorage
    from flext_api._models.webhook import FlextApiModelsWebhook
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".client": ("FlextApiModelsClient",),
        ".request": ("FlextApiModelsRequest",),
        ".response": ("FlextApiModelsResponse",),
        ".storage": ("FlextApiModelsStorage",),
        ".webhook": ("FlextApiModelsWebhook",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
