"""Test utilities for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api import FlextApiUtilities


class TestsFlextApiUtilities(FlextApiUtilities):
    """Test utilities for flext-api — extends flext_api.u."""

    class Tests(FlextApiUtilities):
        """Test-specific utilities."""


__all__: list[str] = ["TestsFlextApiUtilities"]
