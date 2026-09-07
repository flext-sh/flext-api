"""FLEXT API model facade."""

from __future__ import annotations

from flext_web import m

from ._models.client import FlextApiModelsClient
from ._models.request import FlextApiModelsRequest
from ._models.response import FlextApiModelsResponse
from ._models.storage import FlextApiModelsStorage
from ._models.webhook import FlextApiModelsWebhook
from .typings import t


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
