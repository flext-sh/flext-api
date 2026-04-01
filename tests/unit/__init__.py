# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Unit package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_core import FlextTypes

    from tests.unit.test_serializers import *
    from tests.unit.test_smoke import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "TestConstants": "tests.unit.test_smoke",
    "TestFacadeInheritance": "tests.unit.test_smoke",
    "TestMessagePackUnpackb": "tests.unit.test_serializers",
    "TestModels": "tests.unit.test_smoke",
    "TestSerializers": "tests.unit.test_smoke",
    "test_package_imports_main_facade": "tests.unit.test_smoke",
    "test_serializers": "tests.unit.test_serializers",
    "test_smoke": "tests.unit.test_smoke",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
