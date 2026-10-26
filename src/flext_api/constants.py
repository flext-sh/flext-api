# AUTO-GENERATED FILE — Regenerate with: make gen
"""FlextApi constants facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_web import c

from flext_api._constants import (
    FlextApiConstantsApi,
    FlextApiConstantsBase,
    FlextApiConstantsConfig,
    FlextApiConstantsEnums,
    FlextApiConstantsValues,
)


class FlextApiConstants(c):
    """FlextApi domain constants extending c via MRO."""

    class Api(
        FlextApiConstantsApi,
        FlextApiConstantsValues,
        FlextApiConstantsEnums,
        FlextApiConstantsBase,
        FlextApiConstantsConfig,
    ):
        """API domain constants namespace."""


c = FlextApiConstants
__all__: list[str] = ["FlextApiConstants", "c"]
