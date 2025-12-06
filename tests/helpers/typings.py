"""Test typings extending flext_api.typings for test-specific type definitions.

This module provides test-specific type definitions that extend the production
types from src/flext_api/typings.py. All test types use real inheritance
to expose the full hierarchy and avoid duplication.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.typings import FlextApiTypes


class TestsTypings(FlextApiTypes):
    """Test-specific type definitions extending FlextApiTypes.

    Provides test-specific type aliases that extend production types
    with test-specific type definitions. Uses real inheritance to expose
    the full hierarchy without duplication.
    """

    # Test-specific types can be added here as nested classes
    # All parent types are accessible via inheritance


# Standardized short name for use in tests (same pattern as flext-core)
t = TestsTypings

__all__ = ["TestsTypings", "t"]
