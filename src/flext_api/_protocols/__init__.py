# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Protocols package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_api import plugins, transports
    from flext_api.plugins import FlextApiPlugins
    from flext_api.transports import FlextApiTransports
    from flext_core import FlextTypes

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
    "FlextApiPlugins": "flext_api.plugins",
    "FlextApiTransports": "flext_api.transports",
    "plugins": "flext_api.plugins",
    "transports": "flext_api.transports",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
