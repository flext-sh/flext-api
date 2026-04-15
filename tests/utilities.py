"""Test utilities for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsUtilities

from flext_api import FlextApiUtilities
from flext_web import FlextWebUtilities


class TestsFlextApiUtilities(FlextTestsUtilities, FlextApiUtilities, FlextWebUtilities):
    """Test utilities for flext-api."""

    class Api(FlextApiUtilities.Api):
        """Api domain test utilities."""

        class Tests:
            """Test-specific utilities."""


u = TestsFlextApiUtilities

__all__: list[str] = ["TestsFlextApiUtilities", "u"]
