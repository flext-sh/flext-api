"""Test protocol definitions for flext-api.

Provides TestsFlextApiProtocols, combining FlextTestsProtocols with
FlextApiProtocols for test-specific protocol definitions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests.protocols import FlextTestsProtocols

from flext_api.protocols import FlextApiProtocols


class TestsFlextApiProtocols(FlextTestsProtocols, FlextApiProtocols):
    """Test protocols combining FlextTestsProtocols and FlextApiProtocols.

    Provides access to:
    - tp.Tests.Docker.* (from FlextTestsProtocols)
    - tp.Tests.Factory.* (from FlextTestsProtocols)
    - tp.Api.* (from FlextApiProtocols)
    """

    class Tests:
        """Project-specific test protocols.

        Extends FlextTestsProtocols.Tests with Api-specific protocols.
        """

        class Api:
            """Api-specific test protocols."""


# Runtime aliases
p = TestsFlextApiProtocols
tp = TestsFlextApiProtocols

__all__ = ["TestsFlextApiProtocols", "p", "tp"]
