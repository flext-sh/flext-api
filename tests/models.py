"""Test models for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsModels

from flext_api import FlextApiModels


class FlextApiTestModels(FlextTestsModels, FlextApiModels):
    """Test models for flext-api."""

    class Api(FlextApiModels.Api):
        """Api domain test models."""

        class Tests:
            """Test-specific models."""


m = FlextApiTestModels
__all__ = ["FlextApiTestModels", "m"]
