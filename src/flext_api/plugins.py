"""Generic plugin system for flext-api using FLEXT patterns.

Delegates to external libraries and flext-core for plugin management.
Provides abstract plugin types with Clean Architecture patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from abc import abstractmethod
from typing import ClassVar

from flext_core import FlextLogger, FlextResult

from flext_api.typings import FlextApiTypes


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
            self.logger = FlextLogger(f"{__name__}.{name}")
            self._initialized = False

        def initialize(self) -> FlextResult[None]:
            """Initialize plugin resources."""
            if self._initialized:
                msg = f"Plugin '{self.name}' already initialized"
                return FlextResult[None].fail(msg)
            self.logger.debug(f"Initializing plugin: {self.name}")
            self._initialized = True
            return FlextResult[None].ok(None)

        def shutdown(self) -> FlextResult[None]:
            """Shutdown plugin and release resources."""
            if not self._initialized:
                return FlextResult[None].fail(
                    f"Plugin '{self.name}' not initialized"
                )
            self.logger.debug(f"Shutting down plugin: {self.name}")
            self._initialized = False
            return FlextResult[None].ok(None)

        @property
        def is_initialized(self) -> bool:
            """Check if plugin is initialized."""
            return self._initialized

        def get_metadata(self) -> dict[str, object]:
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
            request: FlextApiTypes.RequestData,
            **kwargs: FlextApiTypes.JsonValue,
        ) -> FlextResult[FlextApiTypes.ResponseData]:
            """Send request using this protocol."""
            ...

        @abstractmethod
        def supports_protocol(self, protocol: str) -> bool:
            """Check if this plugin supports the given protocol."""
            ...

        def get_supported_protocols(self) -> list[str]:  # noqa: PLR6301
            """Get list of supported protocols."""
            return []

    class Schema(Plugin):
        """Abstract schema plugin for schema validation and introspection."""

        @abstractmethod
        def validate_request(
            self,
            request: FlextApiTypes.RequestData,
            schema: FlextApiTypes.Schema.JsonSchema,
        ) -> FlextResult[bool]:
            """Validate request against schema."""
            ...

        @abstractmethod
        def validate_response(
            self,
            response: FlextApiTypes.ResponseData,
            schema: FlextApiTypes.Schema.JsonSchema,
        ) -> FlextResult[bool]:
            """Validate response against schema."""
            ...

        @abstractmethod
        def load_schema(self, schema_source: str) -> FlextResult[object]:
            """Load schema from source."""
            ...

        def supports_schema_type(self) -> bool:  # noqa: PLR6301
            """Check if this plugin supports the given schema type."""
            return False

        def get_schema_version(self) -> str:  # noqa: PLR6301
            """Get schema specification version."""
            return "unknown"

    class Transport(Plugin):
        """Abstract transport plugin for network communication."""

        @abstractmethod
        def connect(
            self, url: str, **options: FlextApiTypes.JsonValue
        ) -> FlextResult[bool]:
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
            data: FlextApiTypes.Protocol.ProtocolMessage,
            **options: FlextApiTypes.JsonValue,
        ) -> FlextResult[bool]:
            """Send data through connection."""
            ...

        @abstractmethod
        def receive(
            self, connection: object, **options: FlextApiTypes.JsonValue
        ) -> FlextResult[FlextApiTypes.Protocol.ProtocolMessage]:
            """Receive data from connection."""
            ...

        def supports_streaming(self) -> bool:  # noqa: PLR6301
            """Check if transport supports streaming."""
            return False

        def get_connection_info(self) -> FlextApiTypes.Transport.ConnectionInfo:  # noqa: PLR6301
            """Get connection information."""
            return {}

    class Authentication(Plugin):
        """Abstract authentication plugin for credential management."""

        @abstractmethod
        def authenticate(
            self,
            request: FlextApiTypes.RequestData,
            credentials: FlextApiTypes.Authentication.AuthCredentials,
        ) -> FlextResult[FlextApiTypes.RequestData]:
            """Add authentication to request."""
            ...

        @abstractmethod
        def validate_credentials(
            self, credentials: FlextApiTypes.Authentication.AuthCredentials
        ) -> FlextResult[bool]:
            """Validate authentication credentials."""
            ...

        def get_auth_scheme(self) -> str:  # noqa: PLR6301
            """Get authentication scheme name."""
            return "Unknown"

        def requires_refresh(self) -> bool:  # noqa: PLR6301
            """Check if credentials need refresh."""
            return False

        def refresh_credentials(
            self, _credentials: dict[str, object]  # noqa: PLR6301
        ) -> FlextResult[dict[str, object]]:
            """Refresh authentication credentials."""
            return FlextResult[dict[str, object]].fail(
                "Refresh not supported by this plugin"
            )

    class Manager:
        """Plugin manager for discovery, loading, and lifecycle management."""

        def __init__(self) -> None:
            """Initialize plugin manager."""
            self.logger = FlextLogger(__name__)
            self._loaded_plugins: dict[str, FlextApiPlugins.Plugin] = {}

        def load_plugin(self, plugin: FlextApiPlugins.Plugin) -> FlextResult[None]:
            """Load and initialize a plugin."""
            if plugin.name in self._loaded_plugins:
                return FlextResult[None].fail(f"Plugin '{plugin.name}' already loaded")
            init_result = plugin.initialize()
            if init_result.is_failure:
                return FlextResult[None].fail(
                    f"Failed to initialize plugin '{plugin.name}': {init_result.error}"
                )
            self._loaded_plugins[plugin.name] = plugin
            self.logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
            return FlextResult[None].ok(None)

        def unload_plugin(self, plugin_name: str) -> FlextResult[None]:
            """Unload and shutdown a plugin."""
            if plugin_name not in self._loaded_plugins:
                return FlextResult[None].fail(f"Plugin '{plugin_name}' not loaded")
            plugin = self._loaded_plugins[plugin_name]
            shutdown_result = plugin.shutdown()
            if shutdown_result.is_failure:
                self.logger.warning(
                    f"Plugin shutdown warning: {shutdown_result.error}",
                    extra={"plugin": plugin_name},
                )
            del self._loaded_plugins[plugin_name]
            self.logger.info(f"Unloaded plugin: {plugin_name}")
            return FlextResult[None].ok(None)

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

        def shutdown_all(self) -> FlextResult[None]:
            """Shutdown and unload all plugins."""
            failed_plugins: list[str] = []
            for plugin_name in list(self._loaded_plugins.keys()):
                result = self.unload_plugin(plugin_name)
                if result.is_failure:
                    failed_plugins.append(plugin_name)
            if failed_plugins:
                return FlextResult[None].fail(
                    f"Failed to unload plugins: {', '.join(failed_plugins)}"
                )
            return FlextResult[None].ok(None)


# Backward compatibility exports (type aliases for convenience)
BasePlugin = FlextApiPlugins.Plugin
ProtocolPlugin = FlextApiPlugins.Protocol
SchemaPlugin = FlextApiPlugins.Schema
TransportPlugin = FlextApiPlugins.Transport
AuthenticationPlugin = FlextApiPlugins.Authentication
PluginManager = FlextApiPlugins.Manager

__all__ = [
    "AuthenticationPlugin",
    "BasePlugin",
    "PluginManager",
    "ProtocolPlugin",
    "SchemaPlugin",
    "TransportPlugin",
    "FlextApiPlugins",
]
