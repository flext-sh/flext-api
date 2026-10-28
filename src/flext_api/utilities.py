# AUTO-GENERATED FILE — Regenerate with: make gen
"""FlextApi utilities facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from flext_web import u

from flext_api._utilities import (
    FlextApiUtilitiesBase,
    FlextApiUtilitiesRequestUtils,
    FlextApiUtilitiesSerializers,
    FlextApiUtilitiesTransport,
)


class FlextApiUtilities(u):
    """FlextApi utilities extending FlextUtilities with API-specific helpers."""

    class Api(
        FlextApiUtilitiesSerializers,
        FlextApiUtilitiesBase,
        FlextApiUtilitiesRequestUtils,
        FlextApiUtilitiesTransport,
    ):
        """API-specific utility namespace."""


u = FlextApiUtilities
__all__: list[str] = ["FlextApiUtilities", "u"]
