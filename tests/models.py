"""Test models for flext-api.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from tests import m


class TestsFlextApiModels(m):
    """Test models for flext-api — extends flext_api.m."""

    class Tests(m):
        """Test-specific models."""


__all__: list[str] = ["TestsFlextApiModels"]
