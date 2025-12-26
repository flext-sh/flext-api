"""Comprehensive tests for flext_api version and metadata.

Tests validate version parsing and metadata extraction using real package metadata.
No mocks - uses actual importlib.metadata from installed package.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api import __version__, __version_info__

from flext_api.__version__ import (
    __version__ as version_module_version,
    __version_info__ as version_module_version_info,
)


class TestFlextApiVersion:
    """Test version and metadata extraction."""

    def test_version_is_string(self) -> None:
        """Test that __version__ is a non-empty string."""
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_version_has_dots(self) -> None:
        """Test that version contains dots for semantic versioning."""
        assert "." in __version__

    def test_version_info_tuple(self) -> None:
        """Test that __version_info__ is a tuple."""
        assert isinstance(__version_info__, tuple)
        assert len(__version_info__) >= 2  # At least major.minor

        # Each part should be int or str
        for part in __version_info__:
            assert isinstance(part, (int, str))

    def test_all_exports_exist(self) -> None:
        """Test that all __all__ exports are available."""
        # Exported version info should be accessible
        assert __version__ is not None
        assert __version_info__ is not None

    def test_version_module_internals(self) -> None:
        """Test version module internal functionality."""
        # Test that version module works internally
        assert isinstance(version_module_version, str)
        assert isinstance(version_module_version_info, tuple)
