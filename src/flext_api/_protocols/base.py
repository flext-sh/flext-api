"""Base protocol facade for flext-api."""

from __future__ import annotations

from . import (
    FlextApiProtocolsGrpc,
    FlextApiProtocolsHttpClient,
    FlextApiProtocolsResources,
    FlextApiProtocolsSerializer,
    FlextApiProtocolsStorage,
    FlextApiProtocolsTransport,
)


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
