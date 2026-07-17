"""FlextApi utilities facade."""

from __future__ import annotations

from flext_api._utilities.api_pydantic import FlextApiUtilitiesApiPydantic
from flext_api._utilities.request_utils import FlextApiUtilitiesRequestUtils
from flext_api._utilities.serializers import FlextApiUtilitiesSerializers
from flext_api._utilities.settings_manager import FlextApiUtilitiesSettingsManager
from flext_web import u
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flext_api import t


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
