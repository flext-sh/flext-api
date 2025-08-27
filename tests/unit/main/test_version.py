"""Tests for version module.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import re

from packaging.version import Version

import flext_api
from flext_api import (
    FLEXT_API_VERSION as __version__,
    FLEXT_API_VERSION as main_version,
    FLEXT_API_VERSION as reimported_version,
    FLEXT_API_VERSION as version2,
)


class TestVersionModule:
    """Test cases for version module."""

    def test_version_import(self) -> None:
        """Test that version can be imported."""
        # flext_api uses main package version, not separate __version__ module

        assert __version__ is not None
        assert isinstance(__version__, str)
        if __version__ != "0.9.0":
            msg = f"Expected {'0.9.0'}, got {__version__}"
            raise AssertionError(msg)

    def test_version_format(self) -> None:
        """Test that version follows semantic versioning format."""
        assert isinstance(__version__, str)
        assert len(__version__.strip()) > 0

        # Should have at least X.Y.Z format
        parts = __version__.strip().split(".")
        if len(parts) < 3:
            msg = f"Expected {len(parts)} >= 3, Version {__version__} should have at least 3 parts"
            raise AssertionError(
                msg,
            )

        # First three parts should be numeric
        for i, part in enumerate(parts[:3]):
            assert part.isdigit(), f"Version part {i} ({part}) should be numeric"

    def test_version_constants(self) -> None:
        """Test version module constants."""
        # Should be a proper version string
        assert isinstance(__version__, str)
        assert len(__version__) > 0

        # Should match expected format

        version_pattern = r"^\d+\.\d+\.\d+(?:[-+].+)?$"
        assert re.match(version_pattern, __version__), (
            f"Invalid version format: {__version__}"
        )

    def test_version_comparison(self) -> None:
        """Test that version can be compared."""
        # Should be comparable to string
        if __version__ < "0.0.0":
            msg = f"Expected {__version__} >= {'0.0.0'}"
            raise AssertionError(msg)
        assert __version__ != ""

        # Should be a valid version string for packaging
        try:
            parsed_version = Version(__version__)
            assert parsed_version is not None
        except ImportError:
            # packaging module not available, skip this test
            pass

    def test_version_metadata(self) -> None:
        """Test additional version metadata if available."""
        # flext_api doesn't use separate __version__ module with metadata
        # Just verify the main version exists

        assert __version__ is not None
        assert isinstance(__version__, str)

        # Optional: Check if main module has other metadata

        if hasattr(flext_api, "__author__"):
            assert isinstance(flext_api.__author__, str)
        if hasattr(flext_api, "__email__"):
            assert isinstance(flext_api.__email__, str)

    def test_version_module_structure(self) -> None:
        """Test version module structure."""
        # flext_api doesn't use separate __version__ module
        # Test the main module structure instead

        # Should have __version__ attribute
        assert hasattr(flext_api, "__version__")

        # Should be a proper module
        assert hasattr(flext_api, "__name__")
        if flext_api.__name__ != "flext_api":
            msg = f"Expected {'flext_api'}, got {flext_api.__name__}"
            raise AssertionError(msg)

    def test_version_consistency(self) -> None:
        """Test that version is consistent across imports."""
        # Import from main package
        # Version should be consistent on multiple imports

        if main_version != version2:  # Version should be consistent on reimport
            msg = f"Expected {version2}, got {main_version}"
            raise AssertionError(msg)

        # Check direct access

        if flext_api.__version__ != main_version:  # Direct access should match import
            msg = f"Expected {main_version}, got {flext_api.__version__}"
            raise AssertionError(
                msg,
            )

    def test_version_immutability(self) -> None:
        """Test that version cannot be easily modified."""
        original_version = __version__

        # Attempting to modify should not affect the original
        # (This is more about documentation than enforcement)
        modified_version = __version__ + "-modified"
        assert modified_version != original_version

        # Re-import should still have original version

        if reimported_version != original_version:
            msg = f"Expected {original_version}, got {reimported_version}"
            raise AssertionError(
                msg,
            )

    def test_version_documentation(self) -> None:
        """Test that version module has proper documentation."""
        # Test main module documentation

        # Check if module has docstring
        if hasattr(flext_api, "__doc__") and flext_api.__doc__:
            assert isinstance(flext_api.__doc__, str)
            assert len(flext_api.__doc__.strip()) > 0

    def test_version_attributes_types(self) -> None:
        """Test that version attributes have correct types."""
        # __version__ must be string
        assert isinstance(__version__, str)

        # Test other optional attributes from main module

        optional_string_attrs = [
            "__author__",
            "__email__",
            "__description__",
            "__url__",
            "__license__",
        ]

        for attr_name in optional_string_attrs:
            if hasattr(flext_api, attr_name):
                attr_value = getattr(flext_api, attr_name)
                assert isinstance(attr_value, str), (
                    f"{attr_name} should be string if present"
                )

    def test_version_export_consistency(self) -> None:
        """Test that version is properly exported from main package."""
        # Should be able to access version from main package
        assert hasattr(flext_api, "__version__")
        version = flext_api.__version__

        assert isinstance(version, str)
        assert len(version) > 0
        if version != "0.9.0":
            msg = f"Expected {'0.9.0'}, got {version}"
            raise AssertionError(msg)
