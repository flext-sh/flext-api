"""Service base for flext-api tests."""

from __future__ import annotations

from typing import override

from flext_tests import s as tests_s

from flext_api import m, p
from tests.settings import TestsFlextApiSettings


class TestsFlextApiServiceBase(tests_s):
    """API test service base with source and test settings namespaces."""

    # NOTE (multi-agent): flext-tests owns fetch_settings; this project
    # declares only its more-specific bootstrap settings type.
    @classmethod
    @override
    def _runtime_bootstrap_options(cls) -> p.RuntimeBootstrapOptions:
        return m.RuntimeBootstrapOptions(settings_type=TestsFlextApiSettings)


s = TestsFlextApiServiceBase

__all__: list[str] = ["TestsFlextApiServiceBase", "s"]
