"""Test protocols for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import p as flext_tests_p

from flext_api import p as flext_api_p


class TestsFlextApiProtocols(flext_tests_p, flext_api_p):
    """Test protocols for flext-api — extends flext_api.p."""

    class Tests(flext_tests_p.Tests):
        """Test-specific protocols."""


p = TestsFlextApiProtocols

__all__: list[str] = ["TestsFlextApiProtocols", "p"]
