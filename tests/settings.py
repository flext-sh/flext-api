"""Runtime settings for flext-api tests."""

from __future__ import annotations

from flext_tests import FlextTestsSettings

from flext_api import FlextApiSettings


class TestsFlextApiSettings(FlextApiSettings, FlextTestsSettings):
    """API settings extended with the shared test namespace."""


__all__: list[str] = ["TestsFlextApiSettings"]
