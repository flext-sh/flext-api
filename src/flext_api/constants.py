"""FlextApi constants facade."""

from __future__ import annotations

from flext_web import FlextWebConstants

from ._constants import FlextApiConstantsApi
from ._constants.base import FlextApiConstantsBase
from ._constants.config import FlextApiConstantsConfig


class FlextApiConstants(FlextWebConstants):
    """FlextApi domain constants extending FlextWebConstants via MRO."""

    class Api(FlextApiConstantsBase, FlextApiConstantsConfig, FlextApiConstantsApi):
        """API domain constants namespace."""


c = FlextApiConstants

__all__: list[str] = ["FlextApiConstants", "c"]
