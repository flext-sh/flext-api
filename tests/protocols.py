"""Test protocols for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsProtocols

from flext_api import p
from flext_web import FlextWebProtocols


class TestsFlextApiProtocols(FlextTestsProtocols, p, FlextWebProtocols):
    """Test protocols for flext-api."""

    class Api(p.Api):
        """Api domain test protocols."""

        class Tests:
            """Test-specific protocols."""


p = TestsFlextApiProtocols

__all__: list[str] = ["TestsFlextApiProtocols", "p"]
