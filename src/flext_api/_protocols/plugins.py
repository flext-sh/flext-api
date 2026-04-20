"""Generic plugin system for flext-api using FLEXT patterns.

Delegates to external libraries and flext-core for plugin management.
Provides abstract plugin types with Clean Architecture patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import (
    MutableMapping,
    Sequence,
)

from flext_api import p, r, t, u


class _FlextApiPluginBase:
    """Base class for flext-api plugin implementations."""

    name: str
    version: str
    description: str
    logger: p.Logger

    def __init__(
        self,
        name: str = "plugin",
        version: str = "0.0.0",
        description: str = "",
    ) -> None:
        self.name = name
        self.version = version
        self.description = description
        self.logger = u.fetch_logger(__name__)

    def initialize(self) -> p.Result[bool]:
        return r[bool].ok(value=True)

    def shutdown(self) -> p.Result[bool]:
        return r[bool].ok(value=True)


class FlextApiPlugins:
    """Unified plugin system for flext-api with FLEXT-pure patterns."""

    class Plugin(_FlextApiPluginBase):
        """Base plugin type used by manager APIs."""

    class Protocol(_FlextApiPluginBase):
        """Abstract protocol plugin for API protocol implementations."""

        def supported_protocols(self) -> t.StrSequence:
            """Get list of supported protocols."""
            return []

        @abstractmethod
        def send_request(
            self,
            request: t.JsonObject,
            **kwargs: t.Scalar,
        ) -> p.Result[t.JsonObject]:
            """Send request using this protocol."""
            ...

        @abstractmethod
        def supports_protocol(self, protocol: str) -> bool:
            """Check if this plugin supports the given protocol."""
            ...

    class Schema(_FlextApiPluginBase):
        """Abstract schema plugin for schema validation and introspection."""

        def schema_version(self) -> str:
            """Get schema specification version."""
            return "unknown"

        @abstractmethod
        def load_schema(self, schema_source: str) -> p.Result[t.ContainerValue]:
            """Load schema from source."""
            ...

        def supports_schema_type(self) -> bool:
            """Check if this plugin supports the given schema type."""
            return False

        @abstractmethod
        def validate_request(
            self,
            request: t.JsonObject,
            schema: t.JsonObject,
        ) -> p.Result[bool]:
            """Validate request against schema."""
            ...

        @abstractmethod
        def validate_response(
            self,
            response: t.JsonObject,
            schema: t.JsonObject,
        ) -> p.Result[bool]:
            """Validate response against schema."""
            ...

    class Transport(_FlextApiPluginBase):
        """Abstract transport plugin for network communication."""

        @abstractmethod
        def connect(self, url: str, **options: t.Scalar) -> p.Result[bool]:
            """Establish connection to endpoint."""
            ...

        @abstractmethod
        def disconnect(self, connection: t.ContainerValue) -> p.Result[bool]:
            """Close connection."""
            ...

        def connection_info(self) -> t.JsonObject:
            """Get connection information."""
            return {}

        @abstractmethod
        def receive(
            self,
            connection: t.ContainerValue,
            **options: t.Scalar,
        ) -> p.Result[t.JsonObject | str | bytes]:
            """Receive data from connection."""
            ...

        @abstractmethod
        def send(
            self,
            connection: t.ContainerValue,
            data: t.JsonObject | str | bytes,
            **options: t.Scalar,
        ) -> p.Result[bool]:
            """Send data through connection."""
            ...

        def supports_streaming(self) -> bool:
            """Check if transport supports streaming."""
            return False

    class Authentication(_FlextApiPluginBase):
        """Abstract authentication plugin for credential management."""

        @abstractmethod
        def authenticate(
            self,
            request: t.JsonObject,
            credentials: t.JsonObject,
        ) -> p.Result[t.JsonObject]:
            """Add authentication to request."""
            ...

        def auth_scheme(self) -> str:
            """Get authentication scheme name."""
            return "Unknown"

        def refresh_credentials(
            self, credentials: t.JsonObject
        ) -> p.Result[t.JsonObject]:
            """Refresh authentication credentials."""
            _ = credentials
            return r[t.JsonObject].fail("Refresh not supported by this plugin")

        def requires_refresh(self) -> bool:
            """Check if credentials need refresh."""
            return False

        @abstractmethod
        def validate_credentials(self, credentials: t.JsonObject) -> p.Result[bool]:
            """Validate authentication credentials."""
            ...

    class Manager:
        """Plugin manager for discovery, loading, and lifecycle management."""

        _loaded_plugins: MutableMapping[str, FlextApiPlugins.Plugin]

        def __init__(self) -> None:
            """Initialize plugin manager."""
            self.logger = u.fetch_logger(__name__)
            self._loaded_plugins: MutableMapping[str, FlextApiPlugins.Plugin] = {}

        def resolve_plugin(self, plugin_name: str) -> p.Result[FlextApiPlugins.Plugin]:
            """Get loaded plugin by name."""
            if plugin_name not in self._loaded_plugins:
                return r[FlextApiPlugins.Plugin].fail(
                    f"Plugin '{plugin_name}' not loaded",
                )
            return r[FlextApiPlugins.Plugin].ok(self._loaded_plugins[plugin_name])

        def resolve_plugins_by_type(
            self,
            plugin_type: type[FlextApiPlugins.Plugin],
        ) -> Sequence[FlextApiPlugins.Plugin]:
            """Get all loaded plugins of specific type."""
            return [
                plugin
                for plugin in self._loaded_plugins.values()
                if issubclass(plugin.__class__, plugin_type)
            ]

        def list_loaded_plugins(self) -> t.StrSequence:
            """Get list of loaded plugin names."""
            return list(self._loaded_plugins.keys())

        def load_plugin(self, plugin: FlextApiPlugins.Plugin) -> p.Result[bool]:
            """Load and initialize a plugin."""
            if plugin.name in self._loaded_plugins:
                return r[bool].fail(f"Plugin '{plugin.name}' already loaded")
            init_result = plugin.initialize()
            if init_result.failure:
                return r[bool].fail(
                    f"Failed to initialize plugin '{plugin.name}': {init_result.error}",
                )
            self._loaded_plugins[plugin.name] = plugin
            self.logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
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
                    f"Failed to unload plugins: {', '.join(failed_plugins)}",
                )
            return r[bool].ok(value=True)

        def unload_plugin(self, plugin_name: str) -> p.Result[bool]:
            """Unload and shutdown a plugin."""
            if plugin_name not in self._loaded_plugins:
                return r[bool].fail(f"Plugin '{plugin_name}' not loaded")
            plugin = self._loaded_plugins[plugin_name]

            def _log_shutdown_warning(error: str) -> None:
                self.logger.warning(
                    "Plugin shutdown warning: %s",
                    error,
                    plugin=plugin_name,
                )

            plugin.shutdown().tap_error(_log_shutdown_warning)
            del self._loaded_plugins[plugin_name]
            self.logger.info("Unloaded plugin: %s", plugin_name)
            return r[bool].ok(value=True)


__all__: list[str] = ["FlextApiPlugins"]
