"""Test utilities for flext-api.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsUtilities

from flext_api import FlextApiUtilities


class TestsFlextApiUtilities(FlextTestsUtilities, FlextApiUtilities):
    """Test utilities for flext-api — composes the package utilities."""


u = TestsFlextApiUtilities

__all__: list[str] = ["TestsFlextApiUtilities", "u"]
