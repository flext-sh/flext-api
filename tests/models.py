"""Test models for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import m as flext_tests_m

from flext_api import m as flext_api_m


class TestsFlextApiModels(flext_tests_m, flext_api_m):
    """Test models for flext-api — extends flext_api.m."""

    class Tests(flext_tests_m.Tests):
        """Test-specific models."""


m = TestsFlextApiModels

__all__: list[str] = ["TestsFlextApiModels", "m"]
