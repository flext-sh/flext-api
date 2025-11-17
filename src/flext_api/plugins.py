"""Generic plugin system for flext-api using FLEXT patterns.

Delegates to external libraries and flext-core for plugin management.
Provides abstract plugin types with Clean Architecture patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from flext_core import FlextLogger, FlextResult


class FlextApiPlugins:
    """Unified plugin system for flext-api with FLEXT-pure patterns."""

    class Plugin:
        """Base plugin with lifecycle management and metadata."""

        def __init__(
            self, name: str, version: str = "1.0.0", description: str = ""
        ) -> None:
            """Initialize plugin with metadata."""
            self.name = name
            self.version = version
            self.description = description
            # Set logger only if not already a property (from FlextMixins via FlextService)
            # Use object.__setattr__ to bypass property if it exists
            try:
                object.__setattr__(self, "logger", FlextLogger(f"{__name__}.{name}"))
            except (AttributeError, TypeError):
                # Logger is a property, use _plugin_logger instead
                object.__setattr__(
                    self, "_plugin_logger", FlextLogger(f"{__name__}.{name}")
                )
            self._initialized = False

        def initialize(self) -> FlextResult[bool]:
            """Initialize plugin resources."""
            if self._initialized:
                msg = f"Plugin '{self.name}' already initialized"
                return FlextResult[bool].fail(msg)
            self.logger.debug(f"Initializing plugin: {self.name}")
            self._initialized = True
            return FlextResult[bool].ok(True)

        def shutdown(self) -> FlextResult[bool]:
            """Shutdown plugin and release resources."""
            if not self._initialized:
                return FlextResult[bool].fail(f"Plugin '{self.name}' not initialized")
            self.logger.debug(f"Shutting down plugin: {self.name}")
            self._initialized = False
            return FlextResult[bool].ok(True)

        @property
        def is_initialized(self) -> bool:
            """Check if plugin is initialized."""
            return self._initialized

        def get_metadata(self) -> dict[str, Any]:
            """Get plugin metadata."""
            return {
                "name": self.name,
                "version": self.version,
                "description": self.description,
                "initialized": str(self._initialized),
            }

    class Protocol(Plugin):
        """Abstract protocol plugin for API protocol implementations."""

        @abstractmethod
        def send_request(
            self,
            request: dict[str, object],
            **kwargs: object,
        ) -> FlextResult[dict[str, object]]:
            """Send request using this protocol."""
            ...

        @abstractmethod
        def supports_protocol(self, protocol: str) -> bool:
            """Check if this plugin supports the given protocol."""
            ...

        def get_supported_protocols(self) -> list[str]:
            """Get list of supported protocols."""
            return []

    class Schema(Plugin):
        """Abstract schema plugin for schema validation and introspection."""

        @abstractmethod
        def validate_request(
            self,
            request: dict[str, Any],
            schema: dict[str, Any],
        ) -> FlextResult[bool]:
            """Validate request against schema."""
            ...

        @abstractmethod
        def validate_response(
            self,
            response: dict[str, Any],
            schema: dict[str, Any],
        ) -> FlextResult[bool]:
            """Validate response against schema."""
            ...

        @abstractmethod
        def load_schema(self, schema_source: str) -> FlextResult[object]:
            """Load schema from source."""
            ...

        def supports_schema_type(self) -> bool:
            """Check if this plugin supports the given schema type."""
            return False

        def get_schema_version(self) -> str:
            """Get schema specification version."""
            return "unknown"

    class Transport(Plugin):
        """Abstract transport plugin for network communication."""

        @abstractmethod
        def connect(self, url: str, **options: object) -> FlextResult[bool]:
            """Establish connection to endpoint."""
            ...

        @abstractmethod
        def disconnect(self, connection: object) -> FlextResult[bool]:
            """Close connection."""
            ...

        @abstractmethod
        def send(
            self,
            connection: object,
            data: dict[str, object] | str | bytes,
            **options: object,
        ) -> FlextResult[bool]:
            """Send data through connection."""
            ...

        @abstractmethod
        def receive(
            self, connection: object, **options: object
        ) -> FlextResult[dict[str, object] | str | bytes]:
            """Receive data from connection."""
            ...

        def supports_streaming(self) -> bool:
            """Check if transport supports streaming."""
            return False

        def get_connection_info(self) -> dict[str, Any]:
            """Get connection information."""
            return {}

    class Authentication(Plugin):
        """Abstract authentication plugin for credential management."""

        @abstractmethod
        def authenticate(
            self,
            request: dict[str, Any],
            credentials: dict[str, Any],
        ) -> FlextResult[dict[str, Any]]:
            """Add authentication to request."""
            ...

        @abstractmethod
        def validate_credentials(
            self, credentials: dict[str, Any]
        ) -> FlextResult[bool]:
            """Validate authentication credentials."""
            ...

        def get_auth_scheme(self) -> str:
            """Get authentication scheme name."""
            return "Unknown"

        def requires_refresh(self) -> bool:
            """Check if credentials need refresh."""
            return False

        def refresh_credentials(
            self, _credentials: dict[str, Any]
        ) -> FlextResult[dict[str, Any]]:
            """Refresh authentication credentials."""
            return FlextResult[dict[str, Any]].fail(
                "Refresh not supported by this plugin"
            )

    class Manager:
        """Plugin manager for discovery, loading, and lifecycle management."""

        def __init__(self) -> None:
            """Initialize plugin manager."""
            self.logger = FlextLogger(__name__)
            self._loaded_plugins: dict[str, FlextApiPlugins.Plugin] = {}

        def load_plugin(self, plugin: FlextApiPlugins.Plugin) -> FlextResult[bool]:
            """Load and initialize a plugin."""
            if plugin.name in self._loaded_plugins:
                return FlextResult[bool].fail(f"Plugin '{plugin.name}' already loaded")
            init_result = plugin.initialize()
            if init_result.is_failure:
                return FlextResult[bool].fail(
                    f"Failed to initialize plugin '{plugin.name}': {init_result.error}"
                )
            self._loaded_plugins[plugin.name] = plugin
            self.logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
            return FlextResult[bool].ok(True)

        def unload_plugin(self, plugin_name: str) -> FlextResult[bool]:
            """Unload and shutdown a plugin."""
            if plugin_name not in self._loaded_plugins:
                return FlextResult[bool].fail(f"Plugin '{plugin_name}' not loaded")
            plugin = self._loaded_plugins[plugin_name]
            shutdown_result = plugin.shutdown()
            if shutdown_result.is_failure:
                self.logger.warning(
                    f"Plugin shutdown warning: {shutdown_result.error}",
                    extra={"plugin": plugin_name},
                )
            del self._loaded_plugins[plugin_name]
            self.logger.info(f"Unloaded plugin: {plugin_name}")
            return FlextResult[bool].ok(True)

        def get_plugin(self, plugin_name: str) -> FlextResult[FlextApiPlugins.Plugin]:
            """Get loaded plugin by name."""
            if plugin_name not in self._loaded_plugins:
                return FlextResult[FlextApiPlugins.Plugin].fail(
                    f"Plugin '{plugin_name}' not loaded"
                )
            return FlextResult[FlextApiPlugins.Plugin].ok(
                self._loaded_plugins[plugin_name]
            )

        def list_loaded_plugins(self) -> list[str]:
            """Get list of loaded plugin names."""
            return list(self._loaded_plugins.keys())

        def get_plugins_by_type(
            self, plugin_type: type[FlextApiPlugins.Plugin]
        ) -> list[FlextApiPlugins.Plugin]:
            """Get all loaded plugins of specific type."""
            return [
                plugin
                for plugin in self._loaded_plugins.values()
                if isinstance(plugin, plugin_type)
            ]

        def shutdown_all(self) -> FlextResult[bool]:
            """Shutdown and unload all plugins."""
            failed_plugins: list[str] = []
            for plugin_name in list(self._loaded_plugins.keys()):
                result = self.unload_plugin(plugin_name)
                if result.is_failure:
                    failed_plugins.append(plugin_name)
            if failed_plugins:
                return FlextResult[bool].fail(
                    f"Failed to unload plugins: {', '.join(failed_plugins)}"
                )
            return FlextResult[bool].ok(True)


# Note: Compatibility aliases removed - use FlextApiPlugins.* directly
# Previous aliases (removed):
# - BasePlugin -> FlextApiPlugins.Plugin
# - ProtocolPlugin -> FlextApiPlugins.Protocol
# - SchemaPlugin -> FlextApiPlugins.Schema
# - TransportPlugin -> FlextApiPlugins.Transport
# - AuthenticationPlugin -> FlextApiPlugins.Authentication
# - PluginManager -> FlextApiPlugins.Manager

__all__ = [
    "FlextApiPlugins",
]
