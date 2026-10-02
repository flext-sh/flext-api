"""FLEXT API model facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_web import FlextWebModels

from flext_api._models.base import FlextApiModelsBase
from flext_api._models.client import FlextApiModelsClient
from flext_api._models.request import FlextApiModelsRequest
from flext_api._models.response import FlextApiModelsResponse
from flext_api._models.storage import FlextApiModelsStorage
from flext_api._models.webhook import FlextApiModelsWebhook

if TYPE_CHECKING:
    from flext_api import t


class FlextApiModels(FlextWebModels):
    """HTTP domain models for flext-api."""

    class Api(
        FlextApiModelsBase,
        FlextApiModelsRequest,
        FlextApiModelsResponse,
        FlextApiModelsClient,
        FlextApiModelsStorage,
        FlextApiModelsWebhook,
    ):
        """API domain models namespace."""


m = FlextApiModels

__all__: t.MutableSequenceOf[str] = ["FlextApiModels", "m"]
