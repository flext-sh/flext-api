# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unit package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_api.tests.unit.test_serializers import (
        TestsFlextApiSerializers as TestsFlextApiSerializers,
    )
    from flext_api.tests.unit.test_smoke import TestsFlextApiSmoke as TestsFlextApiSmoke
    from flext_api.tests.unit.test_transports_characterization import (
        TestsFlextApiTransportsCharacterization as TestsFlextApiTransportsCharacterization,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".test_serializers": ("TestsFlextApiSerializers",),
        ".test_smoke": ("TestsFlextApiSmoke",),
        ".test_transports_characterization": (
            "TestsFlextApiTransportsCharacterization",
        ),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
