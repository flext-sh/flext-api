"""Base protocol facade for flext-api."""

from __future__ import annotations

from flext_api._protocols.base_grpc import FlextApiProtocolsGrpc
from flext_api._protocols.base_http import FlextApiProtocolsHttpClient
from flext_api._protocols.base_resources import FlextApiProtocolsResources
from flext_api._protocols.base_serialization import FlextApiProtocolsSerializer
from flext_api._protocols.base_storage import FlextApiProtocolsStorage
from flext_api._protocols.base_transport import FlextApiProtocolsTransport


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
