"""Test helpers for flext-api tests.

Provides reusable test utilities and helpers for all test modules.
Consolidates typings, models, and protocols in unified classes.

Uses standardized short names (m, t, p, u) for easy access in tests.
Helpers extend main classes and use same short names in place of base classes.

NOTE: Constants have been moved to tests/constants.py - import from tests.constants instead.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from .models import TestsModels, m
from .protocols import TestsProtocols, p
from .typings import TestsTypings, t
from .utilities import TestsUtilities, u

__all__ = [
    "TestsModels",
    "TestsProtocols",
    "TestsTypings",
    "TestsUtilities",
    "m",
    "p",
    "t",
    "u",
]
