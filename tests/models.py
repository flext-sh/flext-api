"""Test models for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsModels

from flext_api import m
from flext_web import FlextWebModels


class TestsFlextApiModels(FlextTestsModels, m, FlextWebModels):
    """Test models for flext-api."""

    class Api(m.Api):
        """Api domain test models."""

        class Tests:
            """Test-specific models."""


m = TestsFlextApiModels
__all__: list[str] = ["TestsFlextApiModels", "m"]
