"""FlextApi constants facade."""

from __future__ import annotations

from flext_api._constants.api import FlextApiConstantsApi
from flext_web import c


class FlextApiConstants(c):
    """FlextApi domain constants extending FlextWebConstants via MRO."""

    class Api(FlextApiConstantsApi):
        """API domain constants namespace."""


c = FlextApiConstants

__all__: list[str] = ["FlextApiConstants", "c"]
