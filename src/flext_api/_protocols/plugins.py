"""Plugin protocol facade for flext-api.

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

from flext_api._protocols import (
    FlextApiProtocolPluginManager,
    FlextApiTypesProtocolPlugin,
)


class FlextApiProtocolPlugins(
    FlextApiTypesProtocolPlugin,
    FlextApiProtocolPluginManager,
):
    """Unified plugin system for flext-api with FLEXT-pure patterns."""


__all__: list[str] = ["FlextApiProtocolPlugins"]
