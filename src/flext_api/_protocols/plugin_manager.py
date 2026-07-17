"""Plugin manager shard."""

from __future__ import annotations

from abc import ABC
from collections.abc import MutableMapping
from typing import TYPE_CHECKING

from flext_api._protocols.plugin_types import FlextApiProtocolPluginTypes
from flext_core import p, r
from flext_web import u

if TYPE_CHECKING:
    from flext_api import t


class FlextApiProtocolPluginManager:
    """Plugin manager shard for ``p.Api``."""

    class Manager(ABC):
        """Plugin manager for discovery, loading, and lifecycle management."""

        _loaded_plugins: MutableMapping[str, FlextApiProtocolPluginTypes.Plugin]

        def __init__(self) -> None:
            """Initialize plugin manager."""
            self.logger = u.fetch_logger(__name__)
            self._loaded_plugins = {}

        def resolve_plugin(
            self, plugin_name: str
        ) -> p.Result[FlextApiProtocolPluginTypes.Plugin]:
            """Get loaded plugin by name."""
            if plugin_name not in self._loaded_plugins:
                return r[FlextApiProtocolPluginTypes.Plugin].fail(
                    f"Plugin '{plugin_name}' not loaded"
                )
            return r[FlextApiProtocolPluginTypes.Plugin].ok(
                self._loaded_plugins[plugin_name]
            )

        def resolve_plugins_by_type(
            self, plugin_type: type[FlextApiProtocolPluginTypes.Plugin]
        ) -> t.SequenceOf[FlextApiProtocolPluginTypes.Plugin]:
            """Get all loaded plugins of specific type."""
            return [
                plugin
                for plugin in self._loaded_plugins.values()
                if issubclass(plugin.__class__, plugin_type)
            ]

        def list_loaded_plugins(self) -> t.StrSequence:
            """Get list of loaded plugin names."""
            return list(self._loaded_plugins.keys())

        def load_plugin(
            self, plugin: FlextApiProtocolPluginTypes.Plugin
        ) -> p.Result[bool]:
            """Load and initialize a plugin."""
            if plugin.name in self._loaded_plugins:
                return r[bool].fail(f"Plugin '{plugin.name}' already loaded")
            init_result = plugin.initialize()
            if init_result.failure:
                return r[bool].fail(
                    f"Failed to initialize plugin '{plugin.name}': {init_result.error}"
                )
            self._loaded_plugins[plugin.name] = plugin
            self.logger.info("Loaded plugin: %s v%s", plugin.name, plugin.version)
            return r[bool].ok(value=True)

        def shutdown_all(self) -> p.Result[bool]:
            """Shutdown and unload all plugins."""
            failed_plugins: t.StrSequence = [
                plugin_name
                for plugin_name in list(self._loaded_plugins.keys())
                if self.unload_plugin(plugin_name).failure
            ]
            if failed_plugins:
                return r[bool].fail(
                    f"Failed to unload plugins: {', '.join(failed_plugins)}"
                )
            return r[bool].ok(value=True)

        def unload_plugin(self, plugin_name: str) -> p.Result[bool]:
            """Unload and shutdown a plugin."""
            if plugin_name not in self._loaded_plugins:
                return r[bool].fail(f"Plugin '{plugin_name}' not loaded")
            plugin = self._loaded_plugins[plugin_name]
            plugin.shutdown().tap_error(
                lambda error: self._log_shutdown_warning(error, plugin_name)
            )
            del self._loaded_plugins[plugin_name]
            self.logger.info("Unloaded plugin: %s", plugin_name)
            return r[bool].ok(value=True)

        def _log_shutdown_warning(self, error: str, plugin_name: str) -> None:
            """Log shutdown warnings while preserving tap_error's None contract."""
            _ = self.logger.warning(
                "Plugin shutdown warning: %s", error, plugin=plugin_name
            )


__all__: list[str] = ["FlextApiProtocolPluginManager"]
