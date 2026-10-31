# AUTO-GENERATED FILE — Regenerate with: make gen
"""FLEXT API model facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_web import m as flext_web_m

from flext_api._models import (
    FlextApiModelsBase,
    FlextApiModelsConfig,
    FlextApiModelsRequest,
    FlextApiModelsResponse,
    FlextApiModelsStorage,
    FlextApiModelsWebhook,
)


class FlextApiModels(flext_web_m):
    """HTTP domain models for flext-api."""

    class Api(
        FlextApiModelsBase,
        FlextApiModelsConfig,
        FlextApiModelsRequest,
        FlextApiModelsResponse,
        FlextApiModelsStorage,
        FlextApiModelsWebhook,
    ):
        """API domain models namespace."""


m = FlextApiModels
__all__: list[str] = ["FlextApiModels", "FlextApiModelsConfig", "m"]
