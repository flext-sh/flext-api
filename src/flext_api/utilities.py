"""FlextApi utilities facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_web import FlextWebUtilities

from flext_api._utilities import (
    FlextApiUtilitiesApiPydantic,
    FlextApiUtilitiesBase,
    FlextApiUtilitiesRequestUtils,
    FlextApiUtilitiesSerializers,
    FlextApiUtilitiesTransport,
)

if TYPE_CHECKING:
    from flext_api import t


class FlextApiUtilities(FlextWebUtilities):
    """FlextApi utilities extending FlextUtilities with API-specific helpers."""

    class Api(
        FlextApiUtilitiesBase,
        FlextApiUtilitiesApiPydantic,
        FlextApiUtilitiesRequestUtils,
        FlextApiUtilitiesSerializers,
        FlextApiUtilitiesTransport,
    ):
        """API-specific utility namespace."""


u = FlextApiUtilities

__all__: t.MutableSequenceOf[str] = ["FlextApiUtilities", "u"]
