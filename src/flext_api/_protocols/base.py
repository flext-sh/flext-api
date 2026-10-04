"""Base protocol facade for flext-api.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api._protocols import (
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
