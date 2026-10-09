"""FLEXT API Types - Unified domain-specific type definitions with Clean Architecture.

Single class namespace with NO aliases, NO weak types.
All types consolidated within FlextApiTypes using Python 3.13+ syntax.

Note: Protocols are in protocols.py, not here. Use p.Api.* for protocols.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_web import FlextWebTypes

from flext_api._typings import (
    FlextApiTypingsBase,
    FlextApiTypingsSerialization,
    FlextApiTypingsTransport,
)


class FlextApiTypes(FlextWebTypes):
    """Unified API type definitions extending FlextWebTypes via MRO."""

    class Api(
        FlextApiTypingsBase,
        FlextApiTypingsSerialization,
        FlextApiTypingsTransport,
    ):
        """API types namespace for cross-project access."""


t = FlextApiTypes

__all__: list[str] = ["FlextApiTypes", "t"]
