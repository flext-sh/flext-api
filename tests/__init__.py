# AUTO-GENERATED FILE — canonical lazy tests facade. Regenerate with: make gen
"""Test package facade exposing the project test aliases lazily."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from tests.constants import TestsFlextApiConstants as TestsFlextApiConstants, c as c
    from tests.typings import TestsFlextApiTypes as TestsFlextApiTypes, t as t
    from tests.protocols import TestsFlextApiProtocols as TestsFlextApiProtocols, p
    from tests.models import TestsFlextApiModels as TestsFlextApiModels, m as m
    from tests.utilities import TestsFlextApiUtilities as TestsFlextApiUtilities, u
    from tests.base import TestsFlextApiServiceBase as TestsFlextApiServiceBase, s as s

_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".constants": ("TestsFlextApiConstants", "c"),
        ".typings": ("TestsFlextApiTypes", "t"),
        ".protocols": ("TestsFlextApiProtocols", "p"),
        ".models": ("TestsFlextApiModels", "m"),
        ".utilities": ("TestsFlextApiUtilities", "u"),
        ".base": ("TestsFlextApiServiceBase", "s"),
    },
)

install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
