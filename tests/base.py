"""Service base for flext-api tests."""

from __future__ import annotations

from typing import override

from flext_tests import s as tests_s

from flext_api import m
from tests.settings import TestsFlextApiSettings


class TestsFlextApiServiceBase(tests_s):
    """API test service base with source and test settings namespaces."""

    @classmethod
    @override
    def fetch_settings(cls) -> TestsFlextApiSettings:
        """Return the typed API+Tests settings singleton."""

    @classmethod
    @override
    def _runtime_bootstrap_options(cls) -> m.RuntimeBootstrapOptions:
        return m.RuntimeBootstrapOptions(settings_type=TestsFlextApiSettings)


s = TestsFlextApiServiceBase

__all__: list[str] = ["TestsFlextApiServiceBase", "s"]
