"""FlextApi constants facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_web import FlextWebConstants

from flext_api._constants import (
    FlextApiConstantsApi,
    FlextApiConstantsBase,
    FlextApiConstantsConfig,
)


class FlextApiConstants(FlextWebConstants):
    """FlextApi domain constants extending c via MRO."""

    class Api(FlextApiConstantsBase, FlextApiConstantsConfig, FlextApiConstantsApi):
        """API domain constants namespace."""


c = FlextApiConstants

__all__: list[str] = ["FlextApiConstants", "c"]
