"""Tests for deprecated http_operations module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_api import http_operations


class TestHttpOperationsDeprecation:
    """Test deprecated http_operations module."""

    def test_module_can_be_imported(self) -> None:
        """Test that the deprecated module can still be imported."""
        # This module is deprecated but should still be importable
        assert http_operations is not None
        assert hasattr(http_operations, "__all__")
        assert http_operations.__all__ == []

    @pytest.mark.skip(reason="Module is deprecated - no functionality to test")
    def test_no_functionality_available(self) -> None:
        """Test that no functionality is available in this deprecated module."""
        # This module contains no functionality - it's just for backward compatibility
