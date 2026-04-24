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

from flext_web import u

from flext_api import p, r, t


class FlextApiProtocolPlugins:
    """Unified plugin system for flext-api with FLEXT-pure patterns."""

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

    class Plugin(_FlextApiPluginBase):
        """Base plugin type used by manager APIs."""

    class Protocol(_FlextApiPluginBase):
        """Abstract protocol plugin for API protocol implementations."""

        def supported_protocols(self) -> t.StrSequence:
            """Get list of supported protocols."""
            protocols: list[str] = []
            return protocols

        @abstractmethod
        def send_request(
            self,
            request: t.JsonMapping,
            **kwargs: t.Scalar,
        ) -> p.Result[t.JsonMapping]:
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
        def load_schema(self, schema_source: str) -> p.Result[t.JsonValue]:
            """Load schema from source."""
            ...

        def supports_schema_type(self) -> bool:
            """Check if this plugin supports the given schema type."""
            return False

        @abstractmethod
        def validate_request(
            self,
            request: t.JsonMapping,
            schema: t.JsonMapping,
        ) -> p.Result[bool]:
            """Validate request against schema."""
            ...

        @abstractmethod
        def validate_response(
            self,
            response: t.JsonMapping,
            schema: t.JsonMapping,
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
        def disconnect(self, connection: t.JsonValue) -> p.Result[bool]:
            """Close connection."""
            ...

        def connection_info(self) -> t.JsonMapping:
            """Get connection information."""
            info: t.JsonMapping = {}
            return info

        @abstractmethod
        def receive(
            self,
            connection: t.JsonValue,
            **options: t.Scalar,
        ) -> p.Result[t.JsonMapping | str | bytes]:
            """Receive data from connection."""
            ...

        @abstractmethod
        def send(
            self,
            connection: t.JsonValue,
            data: t.JsonMapping | str | bytes,
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
            request: t.JsonMapping,
            credentials: t.JsonMapping,
        ) -> p.Result[t.JsonMapping]:
            """Add authentication to request."""
            ...

        def auth_scheme(self) -> str:
            """Get authentication scheme name."""
            return "Unknown"

        def refresh_credentials(
            self, credentials: t.JsonMapping
        ) -> p.Result[t.JsonMapping]:
            """Refresh authentication credentials."""
            _ = credentials
            return r[t.JsonMapping].fail("Refresh not supported by this plugin")

        def requires_refresh(self) -> bool:
            """Check if credentials need refresh."""
            return False

        @abstractmethod
        def validate_credentials(self, credentials: t.JsonMapping) -> p.Result[bool]:
            """Validate authentication credentials."""
            ...

    class Manager:
        """Plugin manager for discovery, loading, and lifecycle management."""

        _loaded_plugins: MutableMapping[str, FlextApiProtocolPlugins.Plugin]

        def __init__(self) -> None:
            """Initialize plugin manager."""
            self.logger = u.fetch_logger(__name__)
            self._loaded_plugins: MutableMapping[
                str, FlextApiProtocolPlugins.Plugin
            ] = {}

        def resolve_plugin(
            self, plugin_name: str
        ) -> p.Result[FlextApiProtocolPlugins.Plugin]:
            """Get loaded plugin by name."""
            if plugin_name not in self._loaded_plugins:
                return r[FlextApiProtocolPlugins.Plugin].fail(
                    f"Plugin '{plugin_name}' not loaded",
                )
            return r[FlextApiProtocolPlugins.Plugin].ok(
                self._loaded_plugins[plugin_name]
            )

        def resolve_plugins_by_type(
            self,
            plugin_type: type[FlextApiProtocolPlugins.Plugin],
        ) -> Sequence[FlextApiProtocolPlugins.Plugin]:
            """Get all loaded plugins of specific type."""
            return [
                plugin
                for plugin in self._loaded_plugins.values()
                if issubclass(plugin.__class__, plugin_type)
            ]

        def list_loaded_plugins(self) -> t.StrSequence:
            """Get list of loaded plugin names."""
            return list(self._loaded_plugins.keys())

        def load_plugin(self, plugin: FlextApiProtocolPlugins.Plugin) -> p.Result[bool]:
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


__all__: list[str] = ["FlextApiProtocolPlugins"]
