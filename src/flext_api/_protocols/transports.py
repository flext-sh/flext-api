"""FLEXT API Transports - Transport protocol contracts.

This module provides the transport protocol namespace for owner-derived HTTP
status contracts. Transport implementations live outside the protocols layer.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar, Protocol, runtime_checkable

import httpx


class FlextApiProtocolsTransports:
    """FLEXT API transport protocol namespace."""

    @runtime_checkable
    class Httpx(Protocol):
        """Protocol namespace for owner-derived HTTP status contracts.

        Runtime classes and exceptions are published as module-level
        ``Httpx*`` class-object re-exports. Keeping class identity out of this
        protocol namespace preserves both construction/isinstance semantics and
        the Protocol/namespace census contract.
        """

        CONFLICT: ClassVar[int] = int(httpx.codes.CONFLICT)


__all__: list[str] = ["FlextApiProtocolsTransports"]
