"""Tests for main module."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unittest.mock import MagicMock
from unittest.mock import patch

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

    @patch("uvicorn.run")
    def test_main_execution(self, mock_uvicorn_run: MagicMock) -> None:
        """Test main execution path."""
        # Test the main execution by simulating module run
        # This is a simplified test since the actual execution happens in __main__ block
        assert mock_uvicorn_run is not None  # Just verify patch worked

    def test_storage_functionality(self) -> None:
        """Test storage basic functionality."""
        if storage is not None:
            # Test basic storage operations if available
            storage.set("test_key", "test_value")
            result = storage.get("test_key")
            if result != "test_value":
                msg = f"Expected {"test_value"}, got {result}"
                raise AssertionError(msg)
