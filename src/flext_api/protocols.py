"""Generic protocol definitions for HTTP operations.

All protocol interfaces are centralized here following FLEXT standards.
Single unified class with nested protocol definitions organized under .Api namespace.
Domain-agnostic and reusable across any HTTP implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_web import FlextWebProtocols
from httpx import (
    AsyncClient as HttpxAsyncClient,
    Client as HttpxClient,
    HTTPError as HttpxHTTPError,
    HTTPStatusError as HttpxHTTPStatusError,
    RequestError as HttpxRequestError,
    Response as HttpxResponse,
    TimeoutException as HttpxTimeoutException,
)

from ._protocols import (
    FlextApiProtocolPlugins,
    FlextApiProtocolsBase,
    FlextApiProtocolsSerialization,
    FlextApiProtocolsTransports,
)


class FlextApiProtocols(FlextWebProtocols):
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

# Module-level explicit class-object re-exports: consumers can construct and
# isinstance-narrow these names with both static and runtime class semantics.

__all__: list[str] = [
    "FlextApiProtocols",
    "FlextApiProtocolsTransports",
    "HttpxAsyncClient",
    "HttpxClient",
    "HttpxHTTPError",
    "HttpxHTTPStatusError",
    "HttpxRequestError",
    "HttpxResponse",
    "HttpxTimeoutException",
    "p",
]
