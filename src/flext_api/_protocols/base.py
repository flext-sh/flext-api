"""Base protocol facade for flext-api.

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


class FlextApiProtocolsBase:
    """Leaf base for the FLEXT API protocol family."""


__all__: list[str] = ["FlextApiProtocolsBase"]
