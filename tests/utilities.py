"""Test utilities for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api import u
from flext_tests import FlextTestsUtilities


class TestsFlextApiUtilities(FlextTestsUtilities, u):
    """Test utilities for flext-api."""

    class Tests(FlextTestsUtilities.Tests):
        """Test-specific utilities."""


u = TestsFlextApiUtilities

__all__: list[str] = ["TestsFlextApiUtilities", "u"]
