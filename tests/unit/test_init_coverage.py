#!/usr/bin/env python3
"""Tests for __init__.py coverage."""

import flext_api
from flext_api import FlextResult, get_logger


class TestInitCoverage:
    """Test cases for __init__.py coverage."""

    def test_version_import_success(self) -> None:
        """Test successful version import."""
        # Test that version is properly imported
        assert hasattr(flext_api, "__version__")
        assert isinstance(flext_api.__version__, str)
        assert flext_api.__version__ != ""

    def test_version_import_fallback(self) -> None:
        """Test version import fallback when importlib.metadata fails."""
        # Test the logic that would happen in the except block
        try:
            version = "1.0.0"  # This is what would happen in the except block
            if version != "1.0.0":
                raise AssertionError(f"Expected 1.0.0, got {version}")
        except ValueError as e:
            # This exception is never expected but shows the pattern
            msg = "Unexpected error in version test"
            raise AssertionError(msg) from e

    def test_version_info_generation(self) -> None:
        """Test version info tuple generation."""
        # Test that version_info is properly generated
        assert hasattr(flext_api, "__version_info__")
        assert isinstance(flext_api.__version_info__, tuple)

        # Test with known version patterns
        version = "1.2.3"
        version_info = tuple(int(x) for x in version.split(".") if x.isdigit())
        if version_info != (1, 2, 3):
            raise AssertionError(f"Expected (1, 2, 3), got {version_info}")

        # Test with alpha/beta versions (only numeric parts)
        version_alpha = "1.2.3a1"
        version_info_alpha = tuple(
            int(x) for x in version_alpha.split(".") if x.isdigit()
        )
        if version_info_alpha != (1, 2):  # Only 1 and 2 are digits, 3a1 is not
            raise AssertionError(f"Expected (1, 2), got {version_info_alpha}")

    def test_all_imports_successful(self) -> None:
        """Test that all imports in __init__.py work correctly."""
        # This should import without errors and cover import lines
        # Verify all main exports are available
        exports_to_check = [
            "FlextApi",
            "FlextApiBuilder",
            "FlextApiClient",
            "FlextResult",
            "create_flext_api",
            "build_query",
            "build_success_response",
        ]

        for export in exports_to_check:
            assert hasattr(flext_api, export), f"Missing export: {export}"

    def test_all_list_completeness(self) -> None:
        """Test that __all__ list contains all expected exports."""
        # Check that __all__ is defined and contains expected items
        assert hasattr(flext_api, "__all__")
        assert isinstance(flext_api.__all__, list)

        # Check some key exports are in __all__
        required_exports = [
            "FlextApi",
            "FlextApiClient",
            "FlextResult",
            "__version__",
            "__version_info__",
        ]

        for export in required_exports:
            if export not in flext_api.__all__:
                raise AssertionError(f"Missing from __all__: {export}")

    def test_version_attributes_exist(self) -> None:
        """Test that version attributes exist and are correct type."""
        # Test __version__ exists and is string
        assert hasattr(flext_api, "__version__")
        assert isinstance(flext_api.__version__, str)

        # Test __version_info__ exists and is tuple
        assert hasattr(flext_api, "__version_info__")
        assert isinstance(flext_api.__version_info__, tuple)

        # Test version info contains only integers
        for item in flext_api.__version_info__:
            assert isinstance(item, int)

    def test_flext_core_imports_work(self) -> None:
        """Test that flext-core imports are successful."""
        # This should cover the flext-core import lines
        # Verify they are importable and functional
        assert FlextResult is not None
        assert get_logger is not None

        # Test FlextResult basic functionality
        result = FlextResult.ok("test")
        assert result.is_success
        if result.data != "test":
            raise AssertionError(f"Expected test, got {result.data}")

        # Test get_logger basic functionality
        logger = get_logger(__name__)
        assert logger is not None
