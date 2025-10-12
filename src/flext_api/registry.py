"""Plugin Registry for flext-api.

Centralized registry system for protocols, schemas, transports, and authentication providers.
Extends FlextCore.Registry from flext-core for consistency.

See TRANSFORMATION_PLAN.md - Phase 1 for architecture details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextCore

from flext_api.plugins import (
    AuthenticationPlugin,
    ProtocolPlugin,
    SchemaPlugin,
    TransportPlugin,
)


class FlextApiRegistry(FlextCore.Registry):
    """Central registry for API plugins, protocols, schemas, and transports.

    Extends FlextCore.Registry to provide domain-specific registration for:
    - Protocol plugins (HTTP, WebSocket, GraphQL, gRPC, SSE)
    - Schema plugins (OpenAPI, API, JSON Schema, Protobuf, GraphQL Schema)
    - Transport plugins (httpx, websockets, gql, grpcio)
    - Authentication plugins (via FlextAuth integration)

    Usage:
        registry = FlextApiRegistry.get_global()
        registry.register_protocol("http", HttpProtocolPlugin())
        registry.register_schema("openapi", OpenApiSchemaPlugin())
        registry.register_transport("httpx", HttpxTransport())

    Architecture:
        - Singleton pattern via get_global()
        - Type-safe plugin registration
        - Plugin discovery and loading
        - Dependency injection support
        - FlextCore.Result-based error handling
    """

    _global_instance: FlextApiRegistry | None = None

    def __init__(self, dispatcher: FlextCore.Dispatcher | None = None) -> None:
        """Initialize API registry with plugin storage.

        Args:
            dispatcher: Optional FlextCore.Dispatcher for event emission

        """
        super().__init__(dispatcher=dispatcher)
        self.logger = FlextCore.Logger(__name__)

        # Plugin storage by category
        self._protocols: dict[str, ProtocolPlugin] = {}
        self._schemas: dict[str, SchemaPlugin] = {}
        self._transports: dict[str, TransportPlugin] = {}
        self._auth_providers: dict[str, AuthenticationPlugin] = {}

        self.logger.debug("FlextApiRegistry initialized")

    @classmethod
    def get_global(cls) -> FlextApiRegistry:
        """Get global singleton registry instance.

        Returns:
            Global FlextApiRegistry instance

        """
        if cls._global_instance is None:
            cls._global_instance = cls()
        return cls._global_instance

    @classmethod
    def reset_global(cls) -> None:
        """Reset global registry instance (mainly for testing)."""
        cls._global_instance = None

    # Protocol Registration

    def register_protocol(
        self,
        name: str,
        plugin: ProtocolPlugin,
    ) -> FlextCore.Result[None]:
        """Register a protocol plugin.

        Args:
            name: Protocol name (e.g., "http", "websocket", "graphql")
            plugin: Protocol plugin instance

        Returns:
            FlextCore.Result indicating success or failure

        Example:
            >>> registry = FlextApiRegistry.get_global()
            >>> result = registry.register_protocol("http", HttpProtocolPlugin())
            >>> assert result.is_success

        """
        if not name:
            return FlextCore.Result[None].fail("Protocol name cannot be empty")

        if name in self._protocols:
            self.logger.warning(
                f"Protocol '{name}' already registered, overwriting",
                extra={"protocol": name},
            )

        self._protocols[name] = plugin
        self.logger.info(
            f"Registered protocol: {name}",
            extra={"protocol": name, "plugin_type": type(plugin).__name__},
        )

        return FlextCore.Result[None].ok(None)

    def get_protocol(self, name: str) -> FlextCore.Result[ProtocolPlugin]:
        """Get registered protocol plugin by name.

        Args:
            name: Protocol name

        Returns:
            FlextCore.Result containing protocol plugin or error

        """
        if name not in self._protocols:
            return FlextCore.Result[ProtocolPlugin].fail(
                f"Protocol '{name}' not registered. "
                f"Available: {', '.join(self._protocols.keys())}"
            )

        return FlextCore.Result[ProtocolPlugin].ok(self._protocols[name])

    def list_protocols(self) -> FlextCore.Result[FlextCore.Types.StringList]:
        """List all registered protocol names.

        Returns:
            FlextCore.Result containing list of protocol names

        """
        return FlextCore.Result[FlextCore.Types.StringList].ok(
            list(self._protocols.keys())
        )

    def unregister_protocol(self, name: str) -> FlextCore.Result[None]:
        """Unregister a protocol plugin.

        Args:
            name: Protocol name to unregister

        Returns:
            FlextCore.Result indicating success or failure

        """
        if name not in self._protocols:
            return FlextCore.Result[None].fail(f"Protocol '{name}' not registered")

        del self._protocols[name]
        self.logger.info(f"Unregistered protocol: {name}", extra={"protocol": name})
        return FlextCore.Result[None].ok(None)

    # Schema Registration

    def register_schema(
        self,
        name: str,
        plugin: SchemaPlugin,
    ) -> FlextCore.Result[None]:
        """Register a schema plugin.

        Args:
            name: Schema system name (e.g., "openapi", "jsonschema", "graphql")
            plugin: Schema plugin instance

        Returns:
            FlextCore.Result indicating success or failure

        """
        if not name:
            return FlextCore.Result[None].fail("Schema name cannot be empty")

        if name in self._schemas:
            self.logger.warning(
                f"Schema '{name}' already registered, overwriting",
                extra={"schema": name},
            )

        self._schemas[name] = plugin
        self.logger.info(
            f"Registered schema: {name}",
            extra={"schema": name, "plugin_type": type(plugin).__name__},
        )

        return FlextCore.Result[None].ok(None)

    def get_schema(self, name: str) -> FlextCore.Result[SchemaPlugin]:
        """Get registered schema plugin by name.

        Args:
            name: Schema system name

        Returns:
            FlextCore.Result containing schema plugin or error

        """
        if name not in self._schemas:
            return FlextCore.Result[SchemaPlugin].fail(
                f"Schema '{name}' not registered. "
                f"Available: {', '.join(self._schemas.keys())}"
            )

        return FlextCore.Result[SchemaPlugin].ok(self._schemas[name])

    def list_schemas(self) -> FlextCore.Result[FlextCore.Types.StringList]:
        """List all registered schema system names.

        Returns:
            FlextCore.Result containing list of schema names

        """
        return FlextCore.Result[FlextCore.Types.StringList].ok(
            list(self._schemas.keys())
        )

    def unregister_schema(self, name: str) -> FlextCore.Result[None]:
        """Unregister a schema plugin.

        Args:
            name: Schema name to unregister

        Returns:
            FlextCore.Result indicating success or failure

        """
        if name not in self._schemas:
            return FlextCore.Result[None].fail(f"Schema '{name}' not registered")

        del self._schemas[name]
        self.logger.info(f"Unregistered schema: {name}", extra={"schema": name})
        return FlextCore.Result[None].ok(None)

    # Transport Registration

    def register_transport(
        self,
        name: str,
        plugin: TransportPlugin,
    ) -> FlextCore.Result[None]:
        """Register a transport plugin.

        Args:
            name: Transport name (e.g., "httpx", "websockets", "gql")
            plugin: Transport plugin instance

        Returns:
            FlextCore.Result indicating success or failure

        """
        if not name:
            return FlextCore.Result[None].fail("Transport name cannot be empty")

        if name in self._transports:
            self.logger.warning(
                f"Transport '{name}' already registered, overwriting",
                extra={"transport": name},
            )

        self._transports[name] = plugin
        self.logger.info(
            f"Registered transport: {name}",
            extra={"transport": name, "plugin_type": type(plugin).__name__},
        )

        return FlextCore.Result[None].ok(None)

    def get_transport(self, name: str) -> FlextCore.Result[TransportPlugin]:
        """Get registered transport plugin by name.

        Args:
            name: Transport name

        Returns:
            FlextCore.Result containing transport plugin or error

        """
        if name not in self._transports:
            return FlextCore.Result[TransportPlugin].fail(
                f"Transport '{name}' not registered. "
                f"Available: {', '.join(self._transports.keys())}"
            )

        return FlextCore.Result[TransportPlugin].ok(self._transports[name])

    def list_transports(self) -> FlextCore.Result[FlextCore.Types.StringList]:
        """List all registered transport names.

        Returns:
            FlextCore.Result containing list of transport names

        """
        return FlextCore.Result[FlextCore.Types.StringList].ok(
            list(self._transports.keys())
        )

    def unregister_transport(self, name: str) -> FlextCore.Result[None]:
        """Unregister a transport plugin.

        Args:
            name: Transport name to unregister

        Returns:
            FlextCore.Result indicating success or failure

        """
        if name not in self._transports:
            return FlextCore.Result[None].fail(f"Transport '{name}' not registered")

        del self._transports[name]
        self.logger.info(f"Unregistered transport: {name}", extra={"transport": name})
        return FlextCore.Result[None].ok(None)

    # Authentication Provider Registration

    def register_auth_provider(
        self,
        name: str,
        plugin: AuthenticationPlugin,
    ) -> FlextCore.Result[None]:
        """Register an authentication provider plugin.

        Args:
            name: Auth provider name (e.g., "bearer", "oauth2", "jwt")
            plugin: Authentication plugin instance

        Returns:
            FlextCore.Result indicating success or failure

        """
        if not name:
            return FlextCore.Result[None].fail("Auth provider name cannot be empty")

        if name in self._auth_providers:
            self.logger.warning(
                f"Auth provider '{name}' already registered, overwriting",
                extra={"auth_provider": name},
            )

        self._auth_providers[name] = plugin
        self.logger.info(
            f"Registered auth provider: {name}",
            extra={"auth_provider": name, "plugin_type": type(plugin).__name__},
        )

        return FlextCore.Result[None].ok(None)

    def get_auth_provider(self, name: str) -> FlextCore.Result[AuthenticationPlugin]:
        """Get registered authentication provider by name.

        Args:
            name: Auth provider name

        Returns:
            FlextCore.Result containing auth plugin or error

        """
        if name not in self._auth_providers:
            return FlextCore.Result[AuthenticationPlugin].fail(
                f"Auth provider '{name}' not registered. "
                f"Available: {', '.join(self._auth_providers.keys())}"
            )

        return FlextCore.Result[AuthenticationPlugin].ok(self._auth_providers[name])

    def list_auth_providers(self) -> FlextCore.Result[FlextCore.Types.StringList]:
        """List all registered authentication provider names.

        Returns:
            FlextCore.Result containing list of auth provider names

        """
        return FlextCore.Result[FlextCore.Types.StringList].ok(
            list(self._auth_providers.keys())
        )

    def unregister_auth_provider(self, name: str) -> FlextCore.Result[None]:
        """Unregister an authentication provider.

        Args:
            name: Auth provider name to unregister

        Returns:
            FlextCore.Result indicating success or failure

        """
        if name not in self._auth_providers:
            return FlextCore.Result[AuthenticationPlugin].fail(
                f"Auth provider '{name}' not registered"
            )

        del self._auth_providers[name]
        self.logger.info(
            f"Unregistered auth provider: {name}", extra={"auth_provider": name}
        )
        return FlextCore.Result[None].ok(None)

    # Utility Methods

    def get_registry_status(self) -> FlextCore.Result[dict[str, int]]:
        """Get current registry status with plugin counts.

        Returns:
            FlextCore.Result containing registry status dict

        """
        status = {
            "protocols": len(self._protocols),
            "schemas": len(self._schemas),
            "transports": len(self._transports),
            "auth_providers": len(self._auth_providers),
            "total": len(self._protocols)
            + len(self._schemas)
            + len(self._transports)
            + len(self._auth_providers),
        }

        return FlextCore.Result[dict[str, int]].ok(status)

    def clear_all(self) -> FlextCore.Result[None]:
        """Clear all registered plugins (mainly for testing).

        Returns:
            FlextCore.Result indicating success

        """
        self._protocols.clear()
        self._schemas.clear()
        self._transports.clear()
        self._auth_providers.clear()

        self.logger.info("Cleared all registry plugins")
        return FlextCore.Result[None].ok(None)


__all__ = ["FlextApiRegistry"]
