"""Test protocols for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsProtocols

from flext_api import p


class TestsFlextApiProtocols(FlextTestsProtocols, p):
    """Test protocols for flext-api."""

    class Tests(FlextTestsProtocols.Tests):
        """Test-specific protocols."""


p = TestsFlextApiProtocols

__all__: list[str] = ["TestsFlextApiProtocols", "p"]
