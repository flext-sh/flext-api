"""Test type aliases for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api import t


class TestsFlextApiTypes(t):
    """Test type aliases for flext-api — extends flext_api.t."""

    class Tests(t):
        """Test-specific type aliases."""


__all__: list[str] = ["TestsFlextApiTypes"]
