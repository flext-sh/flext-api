"""Focused plugins/__init__.py tests for maximum coverage improvement.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import flext_api.plugins
from flext_api.plugins import __all__


class TestFlextApiPluginsFocused:
    """Focused tests to improve plugins/__init__.py coverage from 0% to 100%."""

    def test_plugins_init_import(self) -> None:
        """Test that plugins module can be imported."""
        # Test that the __all__ list exists and is accessible
        assert hasattr(flext_api.plugins, "__all__")
        assert isinstance(flext_api.plugins.__all__, list)
        assert flext_api.plugins.__all__ == []

    def test_plugins_all_export(self) -> None:
        """Test direct access to __all__ attribute."""
        # This tests line 10 directly
        assert isinstance(__all__, list)
        assert __all__ == []
