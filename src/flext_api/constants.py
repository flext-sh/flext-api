"""FlextApi constants facade."""

from __future__ import annotations

from flext_api._constants.api import FlextApiConstantsApi
from flext_web import FlextWebConstants
from flext_api import t


class FlextApiConstants(FlextWebConstants):
    """FlextApi domain constants extending FlextWebConstants via MRO."""

    class Api(FlextApiConstantsApi):
        """API domain constants namespace."""


c = FlextApiConstants

__all__: t.MutableSequenceOf[str] = ["FlextApiConstants", "c"]