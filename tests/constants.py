"""Test constants for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_tests import FlextTestsConstants

from flext_api import c

if TYPE_CHECKING:
    from tests import t


class TestsFlextApiConstants(FlextTestsConstants, c):
    """Test constants for flext-api."""

    class Tests(FlextTestsConstants.Tests):
        """Test-specific constants."""


c = TestsFlextApiConstants
__all__: t.MutableSequenceOf[str] = ["TestsFlextApiConstants", "c"]
