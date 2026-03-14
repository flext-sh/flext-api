"""Smoke tests for flext-api test discovery."""

from __future__ import annotations

from flext_api import FlextApi


def test_package_imports_main_facade() -> None:
    assert FlextApi is not None
