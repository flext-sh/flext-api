"""Plugin protocol facade for flext-api."""

from __future__ import annotations

from flext_api._protocols.plugin_manager import FlextApiProtocolPluginManager
from flext_api._protocols.plugin_types import FlextApiProtocolPluginTypes


class FlextApiProtocolPlugins(
    FlextApiProtocolPluginTypes,
    FlextApiProtocolPluginManager,
):
    """Unified plugin system for flext-api with FLEXT-pure patterns."""


__all__: list[str] = ["FlextApiProtocolPlugins"]
