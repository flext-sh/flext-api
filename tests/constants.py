"""Test constants for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsConstants

from flext_api import c
from tests import t


class TestsFlextApiConstants(FlextTestsConstants, c):
    """Test constants for flext-api."""

    class Api(c.Api):
        """Api domain test constants."""

        class Tests:
            """Test-specific constants."""


c = TestsFlextApiConstants
__all__: t.MutableSequenceOf[str] = ["TestsFlextApiConstants", "c"]
