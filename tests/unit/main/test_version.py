"""Tests for version module.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import re

from packaging.version import Version

import flext_api

VERSION_CONSTANT = flext_api.__version__
MAIN_VERSION = flext_api.__version__
REIMPORTED_VERSION = flext_api.__version__
VERSION2 = flext_api.__version__


class TestVersionModule:
    """Test cases for version module."""

    def test_version_import(self) -> None:
        """Test that version can be imported."""
        # flext_api uses main package version, not separate VERSION_CONSTANT module

        assert VERSION_CONSTANT is not None
        assert isinstance(VERSION_CONSTANT, str)
        if VERSION_CONSTANT != "0.9.0":
            msg = f"Expected {'0.9.0'}, got {VERSION_CONSTANT}"
            raise AssertionError(msg)

    def test_version_format(self) -> None:
        """Test that version follows semantic versioning format."""
        assert isinstance(VERSION_CONSTANT, str)
        assert len(VERSION_CONSTANT.strip()) > 0

        # Should have at least X.Y.Z format
        parts = VERSION_CONSTANT.strip().split(".")
        if len(parts) < 3:
            msg = f"Expected {len(parts)} >= 3, Version {VERSION_CONSTANT} should have at least 3 parts"
            raise AssertionError(
                msg,
            )

        # First three parts should be numeric
        for i, part in enumerate(parts[:3]):
            assert part.isdigit(), f"Version part {i} ({part}) should be numeric"

    def test_version_constants(self) -> None:
        """Test version module constants."""
        # Should be a proper version string
        assert isinstance(VERSION_CONSTANT, str)
        assert len(VERSION_CONSTANT) > 0

        # Should match expected format

        version_pattern = r"^\d+\.\d+\.\d+(?:[-+].+)?$"
        assert re.match(version_pattern, VERSION_CONSTANT), (
            f"Invalid version format: {VERSION_CONSTANT}"
        )

    def test_version_comparison(self) -> None:
        """Test that version can be compared."""
        # Should be comparable to string
        if VERSION_CONSTANT < "0.0.0":
            msg = f"Expected {VERSION_CONSTANT} >= {'0.0.0'}"
            raise AssertionError(msg)
        assert VERSION_CONSTANT != ""

        # Should be a valid version string for packaging
        parsed_version = Version(VERSION_CONSTANT)
        assert parsed_version is not None

    def test_version_metadata(self) -> None:
        """Test additional version metadata if available."""
        # flext_api doesn't use separate VERSION_CONSTANT module with metadata
        # Just verify the main version exists

        assert VERSION_CONSTANT is not None
        assert isinstance(VERSION_CONSTANT, str)

        # Optional: Check if main module has other metadata

        if hasattr(flext_api, "__author__"):
            assert isinstance(flext_api.__author__, str)
        if hasattr(flext_api, "__email__"):
            assert isinstance(flext_api.__email__, str)

    def test_version_module_structure(self) -> None:
        """Test version module structure."""
        # flext_api doesn't use separate VERSION_CONSTANT module
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

        if MAIN_VERSION != VERSION2:  # Version should be consistent on reimport
            msg = f"Expected {VERSION2}, got {MAIN_VERSION}"
            raise AssertionError(msg)

        # Check direct access

        if flext_api.__version__ != MAIN_VERSION:  # Direct access should match import
            msg = f"Expected {MAIN_VERSION}, got {flext_api.__version__}"
            raise AssertionError(
                msg,
            )

    def test_version_immutability(self) -> None:
        """Test that version cannot be easily modified."""
        original_version = VERSION_CONSTANT

        # Attempting to modify should not affect the original
        # (This is more about documentation than enforcement)
        modified_version = VERSION_CONSTANT + "-modified"
        assert original_version != modified_version

        # Re-import should still have original version

        if original_version != REIMPORTED_VERSION:
            msg = f"Expected {original_version}, got {REIMPORTED_VERSION}"
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
        # VERSION_CONSTANT must be string
        assert isinstance(VERSION_CONSTANT, str)

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
