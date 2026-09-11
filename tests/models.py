"""Test models for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsModels

from flext_api import m


class TestsFlextApiModels(FlextTestsModels, m):
    """Test models for flext-api."""

    class Tests(FlextTestsModels.Tests):
        """Test-specific models."""


m = TestsFlextApiModels
__all__: list[str] = ["TestsFlextApiModels", "m"]
