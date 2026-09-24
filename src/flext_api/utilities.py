"""FlextApi utilities facade."""

from __future__ import annotations

from flext_web import FlextWebUtilities

from . import t
from ._utilities import (
    FlextApiUtilitiesApiPydantic,
    FlextApiUtilitiesRequestUtils,
    FlextApiUtilitiesSerializers,
    FlextApiUtilitiesSettingsManager,
    FlextApiUtilitiesTransport,
)
from ._utilities.base import FlextApiUtilitiesBase


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


__all__: t.MutableSequenceOf[str] = ["FlextApiUtilities", "u"]

u = FlextApiUtilities
