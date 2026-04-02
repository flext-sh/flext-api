"""Test utilities for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsUtilities

from flext_api import FlextApiUtilities


class FlextApiTestUtilities(FlextTestsUtilities, FlextApiUtilities):
    """Test utilities for flext-api."""


u = FlextApiTestUtilities
__all__ = ["FlextApiTestUtilities", "u"]
