"""Base protocol facade for flext-api."""

from __future__ import annotations

from .base_grpc import FlextApiProtocolsGrpc
from .base_http import FlextApiProtocolsHttpClient
from .base_resources import FlextApiProtocolsResources
from .base_serialization import FlextApiProtocolsSerializer
from .base_storage import FlextApiProtocolsStorage
from .base_transport import FlextApiProtocolsTransport


class FlextApiProtocolsBase(
    FlextApiProtocolsHttpClient,
    FlextApiProtocolsStorage,
    FlextApiProtocolsSerializer,
    FlextApiProtocolsResources,
    FlextApiProtocolsTransport,
    FlextApiProtocolsGrpc,
):
    """FLEXT API transport protocol namespace."""


__all__: list[str] = ["FlextApiProtocolsBase"]
