"""FLEXT API model facade."""

from __future__ import annotations

from flext_api import t
from flext_api._models.client import FlextApiModelsClient
from flext_api._models.request import FlextApiModelsRequest
from flext_api._models.response import FlextApiModelsResponse
from flext_api._models.storage import FlextApiModelsStorage
from flext_api._models.webhook import FlextApiModelsWebhook
from flext_web import m


class FlextApiModels(m):
    """HTTP domain models for flext-api."""

    class Api(
        FlextApiModelsRequest,
        FlextApiModelsResponse,
        FlextApiModelsClient,
        FlextApiModelsStorage,
        FlextApiModelsWebhook,
    ):
        """API domain models namespace."""


m = FlextApiModels

__all__: t.MutableSequenceOf[str] = ["FlextApiModels", "m"]
