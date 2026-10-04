"""Plugin protocol facade for flext-api.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api._protocols import (
    FlextApiProtocolPluginManager,
    FlextApiProtocolPluginTypes,
)


class FlextApiProtocolPlugins(
    FlextApiProtocolPluginTypes,
    FlextApiProtocolPluginManager,
):
    """Unified plugin system for flext-api with FLEXT-pure patterns."""


__all__: list[str] = ["FlextApiProtocolPlugins"]
