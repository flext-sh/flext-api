"""FlextApi utilities facade."""

from __future__ import annotations

from flext_api import FlextApiUtilitiesSerializers, FlextApiUtilitiesSettingsManager
from flext_api._utilities.api_pydantic import FlextApiUtilitiesApiPydantic
from flext_api._utilities.request_utils import FlextApiUtilitiesRequestUtils
from flext_web import u


class FlextApiUtilities(
    u,
    FlextApiUtilitiesSerializers,
    FlextApiUtilitiesSettingsManager,
):
    """FlextApi utilities extending FlextUtilities with API-specific helpers."""

    MAX_HOSTNAME_LENGTH: int = 253
    MAX_PORT: int = 65535
    VALID_HTTP_METHODS: frozenset[str] = frozenset({
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "HEAD",
        "OPTIONS",
        "CONNECT",
        "TRACE",
    })

    class Api(FlextApiUtilitiesApiPydantic, FlextApiUtilitiesRequestUtils):
        """API-specific utility namespace."""


__all__: list[str] = ["FlextApiUtilities", "u"]

u = FlextApiUtilities
