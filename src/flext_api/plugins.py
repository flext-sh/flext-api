"""Plugin System for flext-api.

Base plugin classes and interfaces for extensible API functionality.
Supports protocol, schema, transport, and authentication plugins.

See TRANSFORMATION_PLAN.md - Phase 1 for architecture details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from abc import abstractmethod
from typing import Any

from flext_core import FlextLogger, FlextResult, FlextTypes

from flext_api.typings import FlextApiTypes


class BasePlugin:
    """Base class for all flext-api plugins.

    Provides common plugin functionality:
    - Plugin metadata (name, version, description)
    - Lifecycle methods (initialize, shutdown)
    - Configuration management
    - Error handling with FlextResult

    All plugins must extend this base class.
    """

    def __init__(
        self, name: str, version: str = "1.0.0", description: str = ""
    ) -> None:
        """Initialize base plugin.

        Args:
            name: Plugin name
            version: Plugin version
            description: Plugin description

        """
        self.name = name
        self.version = version
        self.description = description
        self.logger = FlextLogger(f"{__name__}.{name}")
        self._initialized = False

    def initialize(self) -> FlextResult[None]:
        """Initialize plugin resources.

        Called when plugin is registered or loaded.
        Override this method to perform plugin-specific initialization.

        Returns:
            FlextResult indicating success or failure

        """
        if self._initialized:
            return FlextResult[None].fail(f"Plugin '{self.name}' already initialized")

        self.logger.debug(f"Initializing plugin: {self.name}")
        self._initialized = True
        return FlextResult[None].ok(None)

    def shutdown(self) -> FlextResult[None]:
        """Shutdown plugin and release resources.

        Called when plugin is unregistered or application shuts down.
        Override this method to perform plugin-specific cleanup.

        Returns:
            FlextResult indicating success or failure

        """
        if not self._initialized:
            return FlextResult[None].fail(
                f"Plugin '{self.name}' not initialized, cannot shutdown"
            )

        self.logger.debug(f"Shutting down plugin: {self.name}")
        self._initialized = False
        return FlextResult[None].ok(None)

    @property
    def is_initialized(self) -> bool:
        """Check if plugin is initialized."""
        return self._initialized

    def get_metadata(self) -> dict:
        """Get plugin metadata.

        Returns:
            Dictionary containing plugin metadata

        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "initialized": str(self._initialized),
        }


class ProtocolPlugin(BasePlugin):
    """Base class for protocol plugins.

    Protocol plugins implement support for different API protocols:
    - HTTP/1.1, HTTP/2, HTTP/3
    - WebSocket
    - GraphQL
    - gRPC
    - Server-Sent Events (SSE)

    Each protocol plugin must implement request handling for its protocol.
    """

    @abstractmethod
    def send_request(
        self, request: FlextApiTypes.RequestData, **kwargs: FlextApiTypes.JsonValue
    ) -> FlextResult[FlextApiTypes.ResponseData]:
        """Send request using this protocol.

        Args:
            request: Request model
            **kwargs: Protocol-specific parameters

        Returns:
            FlextResult containing response or error

        """
        ...

    @abstractmethod
    def supports_protocol(self, protocol: str) -> bool:
        """Check if this plugin supports the given protocol.

        Args:
            protocol: Protocol identifier (e.g., "http", "websocket")

        Returns:
            True if protocol is supported

        """
        ...

    def get_supported_protocols(self) -> FlextTypes.StringList:
        """Get list of supported protocols.

        Returns:
            List of supported protocol identifiers

        """
        return []


class SchemaPlugin(BasePlugin):
    """Base class for schema plugins.

    Schema plugins implement support for different API schema systems:
    - OpenAPI 3.x
    - API
    - JSON Schema
    - GraphQL Schema
    - Protocol Buffers

    Each schema plugin must implement validation and introspection.
    """

    @abstractmethod
    def validate_request(
        self,
        request: FlextApiTypes.RequestData,
        schema: FlextApiTypes.Schema.JsonSchema,
    ) -> FlextResult[bool]:
        """Validate request against schema.

        Args:
            request: Request to validate
            schema: Schema definition

        Returns:
            FlextResult containing validation result or errors

        """
        ...

    @abstractmethod
    def validate_response(
        self,
        response: FlextApiTypes.ResponseData,
        schema: FlextApiTypes.Schema.JsonSchema,
    ) -> FlextResult[bool]:
        """Validate response against schema.

        Args:
            response: Response to validate
            schema: Schema definition

        Returns:
            FlextResult containing validation result or errors

        """
        ...

    @abstractmethod
    def load_schema(self, schema_source: str) -> FlextResult[Any]:
        """Load schema from source.

        Args:
            schema_source: Schema file path or schema dict

        Returns:
            FlextResult containing loaded schema or error

        """
        ...

    def supports_schema_type(self) -> bool:
        """Check if this plugin supports the given schema type.

        Args:
            schema_type: Schema type (e.g., "openapi", "jsonschema")

        Returns:
            True if schema type is supported

        """
        return False

    def get_schema_version(self) -> str:
        """Get schema specification version.

        Returns:
            Schema version string (e.g., "3.1.0" for OpenAPI 3.1.0)

        """
        return "unknown"


class TransportPlugin(BasePlugin):
    """Base class for transport plugins.

    Transport plugins implement the actual network communication:
    - httpx (HTTP/1.1, HTTP/2, HTTP/3)
    - websockets (WebSocket)
    - gql (GraphQL over HTTP/WebSocket)
    - grpcio (gRPC)

    Each transport plugin manages connections and data transmission.
    """

    @abstractmethod
    def connect(
        self, url: str, **options: FlextApiTypes.JsonValue
    ) -> FlextResult[bool]:
        """Establish connection to endpoint.

        Args:
            url: Endpoint URL
            **options: Transport-specific connection options

        Returns:
            FlextResult containing connection object or error

        """
        ...

    @abstractmethod
    def disconnect(self, connection: object) -> FlextResult[bool]:
        """Close connection.

        Args:
            connection: Connection object to close

        Returns:
            FlextResult indicating success or failure

        """
        ...

    @abstractmethod
    def send(
        self,
        connection: object,
        data: FlextApiTypes.Protocol.ProtocolMessage,
        **options: FlextApiTypes.JsonValue,
    ) -> FlextResult[bool]:
        """Send data through connection.

        Args:
            connection: Active connection
            data: Data to send
            **options: Transport-specific send options

        Returns:
            FlextResult indicating success or failure

        """
        ...

    @abstractmethod
    def receive(
        self, connection: object, **options: FlextApiTypes.JsonValue
    ) -> FlextResult[FlextApiTypes.Protocol.ProtocolMessage]:
        """Receive data from connection.

        Args:
            connection: Active connection
            **options: Transport-specific receive options

        Returns:
            FlextResult containing received data or error

        """
        ...

    def supports_streaming(self) -> bool:
        """Check if transport supports streaming.

        Returns:
            True if streaming is supported

        """
        return False

    def get_connection_info(self) -> FlextApiTypes.Transport.ConnectionInfo:
        """Get connection information.

        Args:
            connection: Active connection

        Returns:
            Dictionary containing connection metadata

        """
        return {}


class AuthenticationPlugin(BasePlugin):
    """Base class for authentication plugins.

    Authentication plugins integrate with FlextAuth to provide:
    - Bearer token authentication
    - API key authentication
    - OAuth2 flows
    - JWT handling
    - Custom authentication schemes

    Each auth plugin must implement credential management and request signing.
    """

    @abstractmethod
    def authenticate(
        self,
        request: FlextApiTypes.RequestData,
        credentials: FlextApiTypes.Authentication.AuthCredentials,
    ) -> FlextResult[FlextApiTypes.RequestData]:
        """Add authentication to request.

        Args:
            request: Request to authenticate
            credentials: Authentication credentials

        Returns:
            FlextResult containing authenticated request or error

        """
        ...

    @abstractmethod
    def validate_credentials(
        self, credentials: FlextApiTypes.Authentication.AuthCredentials
    ) -> FlextResult[bool]:
        """Validate authentication credentials.

        Args:
            credentials: Credentials to validate

        Returns:
            FlextResult containing validation result

        """
        ...

    def get_auth_scheme(self) -> str:
        """Get authentication scheme name.

        Returns:
            Authentication scheme (e.g., "Bearer", "API-Key", "OAuth2")

        """
        return "Unknown"

    def requires_refresh(self) -> bool:
        """Check if credentials need refresh.

        Args:
            credentials: Current credentials

        Returns:
            True if refresh is needed

        """
        return False

    def refresh_credentials(
        self,
        _credentials: FlextTypes.Dict,
    ) -> FlextResult[FlextTypes.Dict]:
        """Refresh authentication credentials.

        Args:
            credentials: Current credentials

        Returns:
            FlextResult containing refreshed credentials or error

        """
        return FlextResult[FlextTypes.Dict].fail("Refresh not supported by this plugin")


# Plugin Manager for discovery and loading


class PluginManager:
    """Manager for plugin discovery, loading, and lifecycle management.

    Provides centralized plugin management:
    - Plugin discovery from modules/packages
    - Plugin loading and initialization
    - Plugin dependency resolution
    - Plugin lifecycle management

    Integrates with FlextApiRegistry for plugin registration.
    """

    def __init__(self) -> None:
        """Initialize plugin manager."""
        self.logger = FlextLogger(__name__)
        self._loaded_plugins: dict[str, BasePlugin] = {}

    def load_plugin(
        self,
        plugin: BasePlugin,
    ) -> FlextResult[None]:
        """Load and initialize a plugin.

        Args:
            plugin: Plugin instance to load

        Returns:
            FlextResult indicating success or failure

        """
        if plugin.name in self._loaded_plugins:
            return FlextResult[None].fail(f"Plugin '{plugin.name}' already loaded")

        # Initialize plugin
        init_result = plugin.initialize()
        if init_result.is_failure:
            return FlextResult[None].fail(
                f"Failed to initialize plugin '{plugin.name}': {init_result.error}"
            )

        self._loaded_plugins[plugin.name] = plugin
        self.logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")

        return FlextResult[None].ok(None)

    def unload_plugin(
        self,
        plugin_name: str,
    ) -> FlextResult[None]:
        """Unload and shutdown a plugin.

        Args:
            plugin_name: Name of plugin to unload

        Returns:
            FlextResult indicating success or failure

        """
        if plugin_name not in self._loaded_plugins:
            return FlextResult[None].fail(f"Plugin '{plugin_name}' not loaded")

        plugin = self._loaded_plugins[plugin_name]

        # Shutdown plugin
        shutdown_result = plugin.shutdown()
        if shutdown_result.is_failure:
            self.logger.warning(
                f"Plugin shutdown warning: {shutdown_result.error}",
                extra={"plugin": plugin_name},
            )

        del self._loaded_plugins[plugin_name]
        self.logger.info(f"Unloaded plugin: {plugin_name}")

        return FlextResult[None].ok(None)

    def get_plugin(
        self,
        plugin_name: str,
    ) -> FlextResult[BasePlugin]:
        """Get loaded plugin by name.

        Args:
            plugin_name: Plugin name

        Returns:
            FlextResult containing plugin or error

        """
        if plugin_name not in self._loaded_plugins:
            return FlextResult[BasePlugin].fail(f"Plugin '{plugin_name}' not loaded")

        return FlextResult[BasePlugin].ok(self._loaded_plugins[plugin_name])

    def list_loaded_plugins(self) -> FlextTypes.StringList:
        """Get list of loaded plugin names.

        Returns:
            List of loaded plugin names

        """
        return list(self._loaded_plugins.keys())

    def get_plugins_by_type(
        self,
        plugin_type: type[BasePlugin],
    ) -> list[BasePlugin]:
        """Get all loaded plugins of specific type.

        Args:
            plugin_type: Plugin type class

        Returns:
            List of plugins matching the type

        """
        return [
            plugin
            for plugin in self._loaded_plugins.values()
            if isinstance(plugin, plugin_type)
        ]

    def shutdown_all(self) -> FlextResult[None]:
        """Shutdown and unload all plugins.

        Returns:
            FlextResult indicating success or failure

        """
        failed_plugins: FlextTypes.StringList = []

        for plugin_name in list(self._loaded_plugins.keys()):
            result = self.unload_plugin(plugin_name)
            if result.is_failure:
                failed_plugins.append(plugin_name)

        if failed_plugins:
            return FlextResult[None].fail(
                f"Failed to unload plugins: {', '.join(failed_plugins)}"
            )

        return FlextResult[None].ok(None)


__all__ = [
    "AuthenticationPlugin",
    "BasePlugin",
    "PluginManager",
    "ProtocolPlugin",
    "SchemaPlugin",
    "TransportPlugin",
]
