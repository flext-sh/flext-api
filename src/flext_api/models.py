"""FLEXT API model facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_web import FlextWebModels

from flext_api._models import (
    ApiNamespace,
    FlextApiModelsBase,
    FlextApiModelsRequest,
    FlextApiModelsResponse,
    FlextApiModelsStorage,
    FlextApiModelsWebhook,
)

if TYPE_CHECKING:
    from flext_api import t


class FlextApiModels(FlextWebModels):
    """HTTP domain models for flext-api."""

    class Api(
        FlextApiModelsBase,
        FlextApiModelsRequest,
        FlextApiModelsResponse,
        FlextApiModelsStorage,
        FlextApiModelsWebhook,
    ):
        """API domain models namespace."""


m = FlextApiModels

__all__: t.MutableSequenceOf[str] = ["ApiNamespace", "FlextApiModels", "m"]
