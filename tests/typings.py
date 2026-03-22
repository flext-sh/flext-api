"""Test type aliases for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsTypes

from flext_api import FlextApiTypes


class FlextApiTestTypes(FlextTestsTypes, FlextApiTypes):
    """Test type aliases for flext-api."""

    class Api(FlextApiTypes.Api):
        """Api domain test types."""

        class Tests:
            """Test-specific type aliases."""


t = FlextApiTestTypes
__all__ = ["FlextApiTestTypes", "t"]
