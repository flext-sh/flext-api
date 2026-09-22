"""Test constants for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api import c


class TestsFlextApiConstants(c):
    """Test constants for flext-api — extends flext_api.c."""

    class Tests(c):
        """Test-specific constants."""


__all__: list[str] = ["TestsFlextApiConstants"]
