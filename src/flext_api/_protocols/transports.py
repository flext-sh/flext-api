"""FLEXT API Transports - Transport protocol contracts.

This module provides the transport protocol namespace for owner-derived HTTP
status contracts. Transport implementations live outside the protocols layer.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, runtime_checkable

from flext_api._protocols import (
    FlextApiProtocolsGrpc,
    FlextApiProtocolsHttpClient,
    FlextApiProtocolsResources,
    FlextApiProtocolsSerializer,
    FlextApiProtocolsStorage,
    FlextApiProtocolsTransport,
)


class FlextApiProtocolsTransports(
    FlextApiProtocolsHttpClient,
    FlextApiProtocolsStorage,
    FlextApiProtocolsSerializer,
    FlextApiProtocolsResources,
    FlextApiProtocolsTransport,
    FlextApiProtocolsGrpc,
):
    """FLEXT API transport protocol namespace."""

    @runtime_checkable
    class HttpResponse(Protocol):
        """Minimum response wire contract consumed by API services."""

        @property
        def content(self) -> bytes: ...

        @property
        def headers(self) -> Mapping[str, str]: ...

        @property
        def status_code(self) -> int: ...

        @property
        def text(self) -> str: ...

        def raise_for_status(self) -> FlextApiProtocolsTransports.HttpResponse: ...


__all__: list[str] = ["FlextApiProtocolsTransports"]
