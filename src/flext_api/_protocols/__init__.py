# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""FlextApi protocols subpackage."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_core import FlextTypes

    from flext_api._protocols import plugins, transports
    from flext_api._protocols.plugins import FlextApiPlugins
    from flext_api._protocols.transports import FlextApiTransports

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "FlextApiPlugins": "flext_api._protocols.plugins",
    "FlextApiTransports": "flext_api._protocols.transports",
    "plugins": "flext_api._protocols.plugins",
    "transports": "flext_api._protocols.transports",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
