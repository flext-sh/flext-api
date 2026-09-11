"""Plugin protocol facade for flext-api."""

from __future__ import annotations

from . import FlextApiProtocolPluginManager, FlextApiProtocolPluginTypes


class FlextApiProtocolPlugins(
    FlextApiProtocolPluginTypes, FlextApiProtocolPluginManager
):
    """Unified plugin system for flext-api with FLEXT-pure patterns."""


__all__: list[str] = ["FlextApiProtocolPlugins"]
