# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests.unit package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import c, d, e, h, m, p, r, s, t, td, tf, tk, tm, tv, u, x

    from .model_contract import TestsFlextApiModelContract
    from .test_async_client import TestsFlextApiAsyncClientSmoke
    from .test_response_wire_content import TestsFlextApiResponseWireContent
    from .test_serializers import TestsFlextApiSerializers
    from .test_smoke import TestsFlextApiSmoke
    from .test_transports_facade_httpx import TestsFlextApiHttpxContracts
    from .test_utilities_transport import TestsFlextApiUtilitiesTransport
__all__: tuple[str, ...] = (
    "TestsFlextApiAsyncClientSmoke",
    "TestsFlextApiHttpxContracts",
    "TestsFlextApiModelContract",
    "TestsFlextApiResponseWireContent",
    "TestsFlextApiSerializers",
    "TestsFlextApiSmoke",
    "TestsFlextApiUtilitiesTransport",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "td",
    "tf",
    "tk",
    "tm",
    "tv",
    "u",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".model_contract": ("TestsFlextApiModelContract",),
            ".test_async_client": ("TestsFlextApiAsyncClientSmoke",),
            ".test_response_wire_content": ("TestsFlextApiResponseWireContent",),
            ".test_serializers": ("TestsFlextApiSerializers",),
            ".test_smoke": ("TestsFlextApiSmoke",),
            ".test_transports_facade_httpx": ("TestsFlextApiHttpxContracts",),
            ".test_utilities_transport": ("TestsFlextApiUtilitiesTransport",),
            "flext_tests": (
                "c",
                "d",
                "e",
                "h",
                "m",
                "p",
                "r",
                "s",
                "t",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
                "u",
                "x",
            ),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
