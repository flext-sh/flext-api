"""Test constants for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsConstants

from flext_api import c
from flext_web import FlextWebConstants


class TestsFlextApiConstants(FlextTestsConstants, c, FlextWebConstants):
    """Test constants for flext-api."""

    class Api(c.Api):
        """Api domain test constants."""

        class Tests:
            """Test-specific constants."""


c = TestsFlextApiConstants
__all__: list[str] = ["TestsFlextApiConstants", "c"]
