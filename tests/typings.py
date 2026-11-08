"""Test type aliases for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import t as flext_tests_t

from flext_api import t as flext_api_t


class TestsFlextApiTypes(flext_tests_t, flext_api_t):
    """Test type aliases for flext-api — extends flext_api.t."""

    class Tests(flext_tests_t.Tests):
        """Test-specific type aliases."""


t = TestsFlextApiTypes

__all__: list[str] = ["TestsFlextApiTypes", "t"]
