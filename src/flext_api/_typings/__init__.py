# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api. Typings package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_api._typings.base import FlextApiTypingsBase
    from flext_api._typings.serialization import FlextApiTypingsSerialization
    from flext_api._typings.transport import FlextApiTypingsTransport
    from flext_api._typings.types import FlextApiTypes, t


__all__: tuple[str, ...] = (
    "FlextApiTypes",
    "FlextApiTypingsBase",
    "FlextApiTypingsSerialization",
    "FlextApiTypingsTransport",
    "t",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextApiTypes": ".types",
        "FlextApiTypingsBase": ".base",
        "FlextApiTypingsSerialization": ".serialization",
        "FlextApiTypingsTransport": ".transport",
        "t": ".types",
    }),
    public_exports=__all__,
)
