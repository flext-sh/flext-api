"""FlextApi utilities facade."""

from __future__ import annotations

from flext_web import u

from ._utilities.api_pydantic import FlextApiUtilitiesApiPydantic
from ._utilities.request_utils import FlextApiUtilitiesRequestUtils
from ._utilities.serializers import FlextApiUtilitiesSerializers
from ._utilities.settings_manager import FlextApiUtilitiesSettingsManager
from .typings import t


class FlextApiUtilities(u):
    """FlextApi utilities extending FlextUtilities with API-specific helpers."""

    class Api(
        FlextApiUtilitiesApiPydantic,
        FlextApiUtilitiesRequestUtils,
        FlextApiUtilitiesSerializers,
        FlextApiUtilitiesSettingsManager,
    ):
        """API-specific utility namespace."""


__all__: t.MutableSequenceOf[str] = ["FlextApiUtilities", "u"]

u = FlextApiUtilities
