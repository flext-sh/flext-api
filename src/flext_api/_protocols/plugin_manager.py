"""Plugin manager shard.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from abc import ABC
from collections.abc import MutableMapping
from typing import TYPE_CHECKING

from flext_web import r, u

from flext_api import t
from flext_api._protocols import FlextApiTypesProtocolPlugin

if TYPE_CHECKING:
    from flext_web import p


class FlextApiProtocolPluginManager:
    """Plugin manager shard for ``p.Api``."""

    class Manager(ABC):
        """Plugin manager for discovery, loading, and lifecycle management."""

        _loaded_plugins: MutableMapping[str, FlextApiTypesProtocolPlugin.Plugin]

        def __init__(self) -> None:
            """Initialize plugin manager."""
            self.logger = u.fetch_logger(__name__)
            self._loaded_plugins = {}

        def resolve_plugin(
            self,
            plugin_name: str,
        ) -> p.Result[FlextApiTypesProtocolPlugin.Plugin]:
            """Get loaded plugin by name.

            Returns:
                The resulting ``p.Result[FlextApiTypesProtocolPlugin.Plugin]``.

            """
            if plugin_name not in self._loaded_plugins:
                return r[FlextApiTypesProtocolPlugin.Plugin].fail(
                    f"Plugin '{plugin_name}' not loaded",
                )
            return r[FlextApiTypesProtocolPlugin.Plugin].ok(
                self._loaded_plugins[plugin_name],
            )

        def resolve_plugins_by_type(
            self,
            plugin_type: type[FlextApiTypesProtocolPlugin.Plugin],
        ) -> t.SequenceOf[FlextApiTypesProtocolPlugin.Plugin]:
            """Get all loaded plugins of specific type.

            Returns:
                The resulting ``t.SequenceOf[FlextApiTypesProtocolPlugin.Plugin]``.

            """
            return [
                plugin
                for plugin in self._loaded_plugins.values()
                if issubclass(plugin.__class__, plugin_type)
            ]

        def list_loaded_plugins(self) -> t.StrSequence:
            """Get list of loaded plugin names.

            Returns:
                The resulting ``t.StrSequence``.

            """
            return list(self._loaded_plugins.keys())

        def load_plugin(
            self,
            plugin: FlextApiTypesProtocolPlugin.Plugin,
        ) -> p.Result[bool]:
            """Load and initialize a plugin.

            Returns:
                The resulting ``p.Result[bool]``.

            """
            if plugin.name in self._loaded_plugins:
                return r[bool].fail(f"Plugin '{plugin.name}' already loaded")
            init_result = plugin.initialize()
            if init_result.failure:
                return r[bool].fail(
                    f"Failed to initialize plugin '{plugin.name}': {init_result.error}",
                )
            self._loaded_plugins[plugin.name] = plugin
            self.logger.info("Loaded plugin: %s v%s", plugin.name, plugin.version)
            return r[bool].ok(value=True)

        def shutdown_all(self) -> p.Result[bool]:
            """Shutdown and unload all plugins.

            Returns:
                The resulting ``p.Result[bool]``.

            """
            failed_plugins: t.StrSequence = [
                plugin_name
                for plugin_name in list(self._loaded_plugins.keys())
                if self.unload_plugin(plugin_name).failure
            ]
            if failed_plugins:
                return r[bool].fail(
                    f"Failed to unload plugins: {', '.join(failed_plugins)}",
                )
            return r[bool].ok(value=True)

        def unload_plugin(self, plugin_name: str) -> p.Result[bool]:
            """Unload and shutdown a plugin.

            Returns:
                The resulting ``p.Result[bool]``.

            """
            if plugin_name not in self._loaded_plugins:
                return r[bool].fail(f"Plugin '{plugin_name}' not loaded")
            plugin = self._loaded_plugins[plugin_name]
            plugin.shutdown().tap_error(
                lambda error: self._log_shutdown_warning(error, plugin_name),
            )
            del self._loaded_plugins[plugin_name]
            self.logger.info("Unloaded plugin: %s", plugin_name)
            return r[bool].ok(value=True)

        def _log_shutdown_warning(self, error: str, plugin_name: str) -> None:
            """Log shutdown warnings while preserving tap_error's None contract."""
            self.logger.warning(
                "Plugin shutdown warning: %s",
                error,
                plugin=plugin_name,
            )


__all__: list[str] = ["FlextApiProtocolPluginManager"]
