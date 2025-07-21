"""Tests for version module."""

from __future__ import annotations


class TestVersionModule:
    """Test cases for version module."""

    def test_version_import(self) -> None:
        """Test that version can be imported."""
        # flext_api uses main package version, not separate __version__ module
        from flext_api import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)
        assert __version__ == "0.1.0"

    def test_version_format(self) -> None:
        """Test that version follows semantic versioning format."""
        from flext_api import __version__

        assert isinstance(__version__, str)
        assert len(__version__.strip()) > 0

        # Should have at least X.Y.Z format
        parts = __version__.strip().split(".")
        assert len(parts) >= 3, f"Version {__version__} should have at least 3 parts"

        # First three parts should be numeric
        for i, part in enumerate(parts[:3]):
            assert part.isdigit(), f"Version part {i} ({part}) should be numeric"

    def test_version_constants(self) -> None:
        """Test version module constants."""
        from flext_api import __version__

        # Should be a proper version string
        assert isinstance(__version__, str)
        assert len(__version__) > 0

        # Should match expected format
        import re

        version_pattern = r"^\d+\.\d+\.\d+(?:[-+].+)?$"
        assert re.match(version_pattern, __version__), (
            f"Invalid version format: {__version__}"
        )

    def test_version_comparison(self) -> None:
        """Test that version can be compared."""
        from flext_api import __version__

        # Should be comparable to string
        assert __version__ >= "0.0.0"
        assert __version__ != ""

        # Should be a valid version string for packaging
        try:
            from packaging.version import Version

            parsed_version = Version(__version__)
            assert parsed_version is not None
        except ImportError:
            # packaging module not available, skip this test
            pass

    def test_version_metadata(self) -> None:
        """Test additional version metadata if available."""
        # flext_api doesn't use separate __version__ module with metadata
        # Just verify the main version exists
        from flext_api import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)

        # Optional: Check if main module has other metadata
        import flext_api

        if hasattr(flext_api, "__author__"):
            assert isinstance(flext_api.__author__, str)
        if hasattr(flext_api, "__email__"):
            assert isinstance(flext_api.__email__, str)

    def test_version_module_structure(self) -> None:
        """Test version module structure."""
        # flext_api doesn't use separate __version__ module
        # Test the main module structure instead
        import flext_api

        # Should have __version__ attribute
        assert hasattr(flext_api, "__version__")

        # Should be a proper module
        assert hasattr(flext_api, "__name__")
        assert flext_api.__name__ == "flext_api"

    def test_version_consistency(self) -> None:
        """Test that version is consistent across imports."""
        # Import from main package
        # Version should be consistent on multiple imports
        from flext_api import __version__ as main_version, __version__ as version2

        assert main_version == version2, "Version should be consistent on reimport"

        # Check direct access
        import flext_api

        assert flext_api.__version__ == main_version, (
            "Direct access should match import"
        )

    def test_version_immutability(self) -> None:
        """Test that version cannot be easily modified."""
        from flext_api import __version__

        original_version = __version__

        # Attempting to modify should not affect the original
        # (This is more about documentation than enforcement)
        modified_version = __version__ + "-modified"
        assert modified_version != original_version

        # Re-import should still have original version
        from flext_api import __version__ as reimported_version

        assert reimported_version == original_version

    def test_version_documentation(self) -> None:
        """Test that version module has proper documentation."""
        # Test main module documentation
        import flext_api

        # Check if module has docstring
        if hasattr(flext_api, "__doc__") and flext_api.__doc__:
            assert isinstance(flext_api.__doc__, str)
            assert len(flext_api.__doc__.strip()) > 0

    def test_version_attributes_types(self) -> None:
        """Test that version attributes have correct types."""
        from flext_api import __version__

        # __version__ must be string
        assert isinstance(__version__, str)

        # Test other optional attributes from main module
        import flext_api

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
        import flext_api

        # Should be able to access version from main package
        assert hasattr(flext_api, "__version__")
        version = flext_api.__version__

        assert isinstance(version, str)
        assert len(version) > 0
        assert version == "0.1.0"
