# AUTO-GENERATED FILE — Regenerate with: make gen
"""FlextApi constants facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_web import c as flext_web_c

from flext_api._constants import (
    FlextApiConstantsApi,
    FlextApiConstantsBase,
    FlextApiConstantsConfig,
)


class FlextApiConstants(flext_web_c):
    """FlextApi domain constants extending c via MRO."""

    class Api(
        FlextApiConstantsApi,
        FlextApiConstantsBase,
        FlextApiConstantsConfig,
    ):
        """API domain constants namespace."""


c = FlextApiConstants
__all__: list[str] = ["FlextApiConstants", "c"]
