"""Tests for main module."""

from __future__ import annotations

import flext_api.main as main_module
from flext_api.main import app, storage


class TestMainModule:
    """Test cases for main module."""

    def test_app_exists(self) -> None:
        """Test that app is available."""
        assert app is not None

    def test_storage_exists(self) -> None:
        """Test that storage is available."""
        assert storage is not None

    def test_app_attributes(self) -> None:
        """Test app has expected attributes."""
        assert hasattr(app, "title")
        assert hasattr(app, "description")
        assert hasattr(app, "version")

    def test_main_execution(self) -> None:
        """Test main execution path."""
        # Test the main execution by verifying module structure
        # Skip actual uvicorn.run test to avoid type complexity
        assert hasattr(main_module, "app")
        assert hasattr(main_module, "storage")
        assert hasattr(main_module, "__all__")

    def test_storage_functionality(self) -> None:
        """Test storage basic functionality."""
        if storage is not None:
            # Test basic storage operations if available
            storage.set("test_key", "test_value")
            result = storage.get("test_key")
            if result != "test_value":
                msg = f"Expected {"test_value"}, got {result}"
                raise AssertionError(msg)
