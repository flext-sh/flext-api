# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""FlextApi protocols subpackage."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_api._protocols import plugins as plugins, transports as transports
    from flext_api._protocols.plugins import FlextApiPlugins as FlextApiPlugins
    from flext_api._protocols.transports import FlextApiTransports as FlextApiTransports

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlextApiPlugins": ["flext_api._protocols.plugins", "FlextApiPlugins"],
    "FlextApiTransports": ["flext_api._protocols.transports", "FlextApiTransports"],
    "plugins": ["flext_api._protocols.plugins", ""],
    "transports": ["flext_api._protocols.transports", ""],
}

_EXPORTS: Sequence[str] = [
    "FlextApiPlugins",
    "FlextApiTransports",
    "plugins",
    "transports",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
