"""Test constants for flext-api.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsConstants

from flext_api import FlextApiConstants


class TestsFlextApiConstants(FlextTestsConstants, FlextApiConstants):
    """Test constants for flext-api — composes the package constants."""


c = TestsFlextApiConstants

__all__: list[str] = ["TestsFlextApiConstants", "c"]
