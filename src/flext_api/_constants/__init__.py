# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api. Constants package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_api._constants.api import FlextApiConstantsApi
    from flext_api._constants.api_enums import FlextApiConstantsEnums
    from flext_api._constants.api_values import FlextApiConstantsValues
    from flext_api._constants.base import FlextApiConstantsBase
    from flext_api._constants.config import FlextApiConstantsConfig


__all__: tuple[str, ...] = (
    "FlextApiConstantsApi",
    "FlextApiConstantsBase",
    "FlextApiConstantsConfig",
    "FlextApiConstantsEnums",
    "FlextApiConstantsValues",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextApiConstantsApi": ".api",
        "FlextApiConstantsBase": ".base",
        "FlextApiConstantsConfig": ".config",
        "FlextApiConstantsEnums": ".api_enums",
        "FlextApiConstantsValues": ".api_values",
    }),
    public_exports=__all__,
)
