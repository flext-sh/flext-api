# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api. Models package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_api._models._api_namespace import ApiNamespace
    from flext_api._models.base import FlextApiModelsBase
    from flext_api._models.request import FlextApiModelsRequest
    from flext_api._models.response import FlextApiModelsResponse
    from flext_api._models.storage import FlextApiModelsStorage
    from flext_api._models.webhook import FlextApiModelsWebhook


__all__: tuple[str, ...] = (
    "ApiNamespace",
    "FlextApiModelsBase",
    "FlextApiModelsRequest",
    "FlextApiModelsResponse",
    "FlextApiModelsStorage",
    "FlextApiModelsWebhook",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "ApiNamespace": "._api_namespace",
        "FlextApiModelsBase": ".base",
        "FlextApiModelsRequest": ".request",
        "FlextApiModelsResponse": ".response",
        "FlextApiModelsStorage": ".storage",
        "FlextApiModelsWebhook": ".webhook",
    }),
    public_exports=__all__,
)
