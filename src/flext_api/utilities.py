"""FlextApi utilities facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_web import FlextWebUtilities

from flext_api import t
from flext_api._utilities import (
    FlextApiUtilitiesApiPydantic,
    FlextApiUtilitiesRequestUtils,
    FlextApiUtilitiesSerializers,
    FlextApiUtilitiesSettingsManager,
    FlextApiUtilitiesTransport,
)
from flext_api._utilities.base import FlextApiUtilitiesBase


class FlextApiUtilities(FlextWebUtilities):
    """FlextApi utilities extending FlextUtilities with API-specific helpers."""

    class Api(
        FlextApiUtilitiesBase,
        FlextApiUtilitiesApiPydantic,
        FlextApiUtilitiesRequestUtils,
        FlextApiUtilitiesSerializers,
        FlextApiUtilitiesSettingsManager,
        FlextApiUtilitiesTransport,
    ):
        """API-specific utility namespace."""


u = FlextApiUtilities

__all__: t.MutableSequenceOf[str] = ["FlextApiUtilities", "u"]
