# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if TYPE_CHECKING:
    from flext_tests import (
        d as d,
        e as e,
        h as h,
        r as r,
        td as td,
        tf as tf,
        tk as tk,
        tm as tm,
        tv as tv,
        x as x,
    )

    from flext_api.tests.base import (
        TestsFlextApiServiceBase as TestsFlextApiServiceBase,
        s as s,
    )
    from flext_api.tests.constants import (
        TestsFlextApiConstants as TestsFlextApiConstants,
        c as c,
    )
    from flext_api.tests.models import (
        TestsFlextApiModels as TestsFlextApiModels,
        m as m,
    )
    from flext_api.tests.protocols import (
        TestsFlextApiProtocols as TestsFlextApiProtocols,
        p as p,
    )
    from flext_api.tests.settings import TestsFlextApiSettings as TestsFlextApiSettings
    from flext_api.tests.typings import TestsFlextApiTypes as TestsFlextApiTypes, t as t
    from flext_api.tests.unit.test_serializers import (
        TestsFlextApiSerializers as TestsFlextApiSerializers,
    )
    from flext_api.tests.unit.test_smoke import TestsFlextApiSmoke as TestsFlextApiSmoke
    from flext_api.tests.unit.test_transports_characterization import (
        TestsFlextApiTransportsCharacterization as TestsFlextApiTransportsCharacterization,
    )
    from flext_api.tests.utilities import (
        TestsFlextApiUtilities as TestsFlextApiUtilities,
        u as u,
    )
_LAZY_IMPORTS = merge_lazy_imports(
    (".unit",),
    build_lazy_import_map(
        {
            ".base": (
                "TestsFlextApiServiceBase",
                "s",
            ),
            ".conftest": ("conftest",),
            ".constants": (
                "TestsFlextApiConstants",
                "c",
            ),
            ".models": (
                "TestsFlextApiModels",
                "m",
            ),
            ".protocols": (
                "TestsFlextApiProtocols",
                "p",
            ),
            ".settings": ("TestsFlextApiSettings",),
            ".typings": (
                "TestsFlextApiTypes",
                "t",
            ),
            ".unit": ("unit",),
            ".unit.test_serializers": ("TestsFlextApiSerializers",),
            ".unit.test_smoke": ("TestsFlextApiSmoke",),
            ".unit.test_transports_characterization": (
                "TestsFlextApiTransportsCharacterization",
            ),
            ".utilities": (
                "TestsFlextApiUtilities",
                "u",
            ),
            "flext_tests": (
                "d",
                "e",
                "h",
                "r",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
                "x",
            ),
        },
    ),
    exclude_names=(
        "cleanup_submodule_namespace",
        "install_lazy_exports",
        "lazy_getattr",
        "logger",
        "merge_lazy_imports",
        "output",
        "output_reporting",
        "pytest_addoption",
        "pytest_collect_file",
        "pytest_collection_modifyitems",
        "pytest_configure",
        "pytest_runtest_setup",
        "pytest_runtest_teardown",
        "pytest_sessionfinish",
        "pytest_sessionstart",
        "pytest_terminal_summary",
        "pytest_warning_recorded",
    ),
    module_name=__name__,
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
