"""Test models for flext-api.

Provides test-specific models extending FlextTestsModels and FlextApiModels
with proper hierarchy composition.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests.models import FlextTestsModels

from flext_api.models import FlextApiModels


class TestsFlextApiModels(FlextTestsModels, FlextApiModels):
    """Test models - composition of FlextTestsModels + FlextApiModels.

    Hierarchy:
    - FlextTestsModels: Generic test utilities from flext-tests
    - FlextApiModels: Domain models from flext-api
    - TestsFlextApiModels: Composition + namespace .Tests

    Access patterns:
    - m.Tests.* - Project-specific test fixtures
    - m.HttpRequest - Production domain models (inherited)
    - FlextTestsModels.Tests.* - Generic test utilities
    """

    class Tests:
        """Test fixtures namespace for flext-api.

        Contains test-specific models and fixtures that should not
        be part of production code.
        """


# Short aliases for tests
tm = TestsFlextApiModels
m = TestsFlextApiModels

__all__ = ["TestsFlextApiModels", "m", "tm"]
