"""Generic protocol definitions for HTTP operations.

All protocol interfaces are centralized here following FLEXT standards.
Single unified class with nested protocol definitions organized under .Api namespace.
Domain-agnostic and reusable across any HTTP implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api._protocols.base import FlextApiProtocolsBase
from flext_api._protocols.plugins import FlextApiProtocolPlugins
from flext_api._protocols.serialization import FlextApiProtocolsSerialization
from flext_api._protocols.transports import FlextApiProtocolsTransports
from flext_core import FlextProtocols


class FlextApiProtocols(
    FlextProtocols,
):
    """Single unified HTTP protocols class extending flext-core FlextProtocols."""

    class Api(
        FlextApiProtocolsBase,
        FlextApiProtocolPlugins,
        FlextApiProtocolsSerialization,
        FlextApiProtocolsTransports,
    ):
        """API-specific protocol namespace.

        All API domain-specific protocols are organized here to enable
        proper namespace separation. Parent protocols from flext-core are
        accessible via parent class (e.g., `p.Result`).
        """


p = FlextApiProtocols

__all__: list[str] = ["FlextApiProtocols", "p"]
