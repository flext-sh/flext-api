# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api. Utilities package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_api._utilities.api_pydantic import FlextApiUtilitiesApiPydantic
    from flext_api._utilities.base import FlextApiUtilitiesBase
    from flext_api._utilities.request_utils import FlextApiUtilitiesRequestUtils
    from flext_api._utilities.serializers import FlextApiUtilitiesSerializers
    from flext_api._utilities.transport import FlextApiUtilitiesTransport


__all__: tuple[str, ...] = (
    "FlextApiUtilitiesApiPydantic",
    "FlextApiUtilitiesBase",
    "FlextApiUtilitiesRequestUtils",
    "FlextApiUtilitiesSerializers",
    "FlextApiUtilitiesTransport",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextApiUtilitiesApiPydantic": ".api_pydantic",
        "FlextApiUtilitiesBase": ".base",
        "FlextApiUtilitiesRequestUtils": ".request_utils",
        "FlextApiUtilitiesSerializers": ".serializers",
        "FlextApiUtilitiesTransport": ".transport",
    }),
    public_exports=__all__,
)
