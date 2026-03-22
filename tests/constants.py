"""Test constants for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsConstants

from flext_api import FlextApiConstants


class FlextApiTestConstants(FlextTestsConstants, FlextApiConstants):
    """Test constants for flext-api."""

    class Api(FlextApiConstants.Api):
        """Api domain test constants."""

        class Tests:
            """Test-specific constants."""


c = FlextApiTestConstants
__all__ = ["FlextApiTestConstants", "c"]
