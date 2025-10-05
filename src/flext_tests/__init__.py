"""FLEXT Test Utilities - Shared testing infrastructure for the FLEXT ecosystem.

Provides test domains, matchers, and utilities following FLEXT patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests.domains import FlextTestsDomains
from flext_tests.matchers import FlextTestsMatchers
from flext_tests.utilities import FlextTestsUtilities

__all__ = [
    "FlextTestsDomains",
    "FlextTestsMatchers",
    "FlextTestsUtilities",
]
