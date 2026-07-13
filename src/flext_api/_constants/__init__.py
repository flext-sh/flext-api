# AUTO-GENERATED FILE — Regenerate with: make gen
"""Constants package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_api._constants.api import FlextApiConstantsApi as FlextApiConstantsApi
    from flext_api._constants.api_enums import (
        FlextApiConstantsEnums as FlextApiConstantsEnums,
    )
    from flext_api._constants.api_values import (
        FlextApiConstantsValues as FlextApiConstantsValues,
    )
_LAZY_IMPORTS = build_lazy_import_map({
    ".api": ("FlextApiConstantsApi",),
    ".api_enums": ("FlextApiConstantsEnums",),
    ".api_values": ("FlextApiConstantsValues",),
})


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
