"""FLEXT API Types - Unified domain-specific type definitions with Clean Architecture.

Single class namespace with NO aliases, NO weak types.
All types consolidated within FlextApiTypes using Python 3.13+ syntax.

Note: Protocols are in protocols.py, not here. Use p.Api.* for protocols.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

# Generated type facade; declarations belong to flext_api._typings.types.
from flext_api._typings.types import FlextApiTypes as _FlextApiTypes


class FlextApiTypes(_FlextApiTypes):
    """Public type facade inheriting its complete canonical owner."""


t = FlextApiTypes

__all__: list[str] = ["FlextApiTypes", "t"]
