# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api. Models package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_api._models.base import FlextApiModelsBase
    from flext_api._models.request import FlextApiModelsRequest
    from flext_api._models.response import FlextApiModelsResponse
    from flext_api._models.storage import FlextApiModelsStorage
    from flext_api._models.webhook import FlextApiModelsWebhook


__all__: tuple[str, ...] = (
    "FlextApiModelsBase",
    "FlextApiModelsRequest",
    "FlextApiModelsResponse",
    "FlextApiModelsStorage",
    "FlextApiModelsWebhook",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".base": ("FlextApiModelsBase",),
            ".request": ("FlextApiModelsRequest",),
            ".response": ("FlextApiModelsResponse",),
            ".storage": ("FlextApiModelsStorage",),
            ".webhook": ("FlextApiModelsWebhook",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
