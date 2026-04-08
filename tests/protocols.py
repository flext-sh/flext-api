"""Test protocols for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsProtocols

from flext_api import FlextApiProtocols


class TestsFlextApiProtocols(FlextTestsProtocols, FlextApiProtocols):
    """Test protocols for flext-api."""

    class Api(FlextApiProtocols.Api):
        """Api domain test protocols."""

        class Tests:
            """Test-specific protocols."""


p = TestsFlextApiProtocols
__all__ = ["TestsFlextApiProtocols", "p"]
