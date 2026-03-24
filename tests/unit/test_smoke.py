"""Smoke tests for flext-api test discovery."""

from __future__ import annotations

from flext_tests import tm

from flext_api import FlextApi


def test_package_imports_main_facade() -> None:
    tm.that(FlextApi, none=False)
