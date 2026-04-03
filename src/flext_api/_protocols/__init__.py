# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Protocols package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import flext_api._protocols.plugins as _flext_api__protocols_plugins

    plugins = _flext_api__protocols_plugins
    import flext_api._protocols.transports as _flext_api__protocols_transports
    from flext_api._protocols.plugins import FlextApiPlugins

    transports = _flext_api__protocols_transports
    from flext_api._protocols.transports import FlextApiTransports
_LAZY_IMPORTS = {
    "FlextApiPlugins": "flext_api._protocols.plugins",
    "FlextApiTransports": "flext_api._protocols.transports",
    "plugins": "flext_api._protocols.plugins",
    "transports": "flext_api._protocols.transports",
}

__all__ = [
    "FlextApiPlugins",
    "FlextApiTransports",
    "plugins",
    "transports",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
