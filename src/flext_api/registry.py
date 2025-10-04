"""Plugin Registry for flext-api.

Centralized registry system for protocols, schemas, transports, and authentication providers.
Extends FlextRegistry from flext-core for consistency.

See TRANSFORMATION_PLAN.md - Phase 1 for architecture details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import (
    FlextDispatcher,
    FlextLogger,
    FlextRegistry,
    FlextResult,
    FlextTypes,
)

from flext_api.plugins import (
    AuthenticationPlugin,
    ProtocolPlugin,
    SchemaPlugin,
    TransportPlugin,
)


class FlextApiRegistry(FlextRegistry):
    """Central registry for API plugins, protocols, schemas, and transports.

    Extends FlextRegistry to provide domain-specific registration for:
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
        - FlextResult-based error handling
    """

    _global_instance: FlextApiRegistry | None = None

    def __init__(self, dispatcher: FlextDispatcher | None = None) -> None:
        """Initialize API registry with plugin storage.

        Args:
            dispatcher: Optional FlextDispatcher for event emission

        """
        super().__init__(dispatcher=dispatcher)
        self._logger = FlextLogger(__name__)

        # Plugin storage by category
        self._protocols: dict[str, ProtocolPlugin] = {}
        self._schemas: dict[str, SchemaPlugin] = {}
        self._transports: dict[str, TransportPlugin] = {}
        self._auth_providers: dict[str, AuthenticationPlugin] = {}

        self._logger.debug("FlextApiRegistry initialized")

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
    ) -> FlextResult[None]:
        """Register a protocol plugin.

        Args:
            name: Protocol name (e.g., "http", "websocket", "graphql")
            plugin: Protocol plugin instance

        Returns:
            FlextResult indicating success or failure

        Example:
            >>> registry = FlextApiRegistry.get_global()
            >>> result = registry.register_protocol("http", HttpProtocolPlugin())
            >>> assert result.is_success

        """
        if not name:
            return FlextResult[None].fail("Protocol name cannot be empty")

        if name in self._protocols:
            self._logger.warning(
                f"Protocol '{name}' already registered, overwriting",
                extra={"protocol": name},
            )

        self._protocols[name] = plugin
        self._logger.info(
            f"Registered protocol: {name}",
            extra={"protocol": name, "plugin_type": type(plugin).__name__},
        )

        return FlextResult[None].ok(None)

    def get_protocol(self, name: str) -> FlextResult[ProtocolPlugin]:
        """Get registered protocol plugin by name.

        Args:
            name: Protocol name

        Returns:
            FlextResult containing protocol plugin or error

        """
        if name not in self._protocols:
            return FlextResult[ProtocolPlugin].fail(
                f"Protocol '{name}' not registered. "
                f"Available: {', '.join(self._protocols.keys())}"
            )

        return FlextResult[ProtocolPlugin].ok(self._protocols[name])

    def list_protocols(self) -> FlextResult[FlextTypes.StringList]:
        """List all registered protocol names.

        Returns:
            FlextResult containing list of protocol names

        """
        return FlextResult[FlextTypes.StringList].ok(list(self._protocols.keys()))

    def unregister_protocol(self, name: str) -> FlextResult[None]:
        """Unregister a protocol plugin.

        Args:
            name: Protocol name to unregister

        Returns:
            FlextResult indicating success or failure

        """
        if name not in self._protocols:
            return FlextResult[None].fail(f"Protocol '{name}' not registered")

        del self._protocols[name]
        self._logger.info(f"Unregistered protocol: {name}", extra={"protocol": name})
        return FlextResult[None].ok(None)

    # Schema Registration

    def register_schema(
        self,
        name: str,
        plugin: SchemaPlugin,
    ) -> FlextResult[None]:
        """Register a schema plugin.

        Args:
            name: Schema system name (e.g., "openapi", "jsonschema", "graphql")
            plugin: Schema plugin instance

        Returns:
            FlextResult indicating success or failure

        """
        if not name:
            return FlextResult[None].fail("Schema name cannot be empty")

        if name in self._schemas:
            self._logger.warning(
                f"Schema '{name}' already registered, overwriting",
                extra={"schema": name},
            )

        self._schemas[name] = plugin
        self._logger.info(
            f"Registered schema: {name}",
            extra={"schema": name, "plugin_type": type(plugin).__name__},
        )

        return FlextResult[None].ok(None)

    def get_schema(self, name: str) -> FlextResult[SchemaPlugin]:
        """Get registered schema plugin by name.

        Args:
            name: Schema system name

        Returns:
            FlextResult containing schema plugin or error

        """
        if name not in self._schemas:
            return FlextResult[SchemaPlugin].fail(
                f"Schema '{name}' not registered. "
                f"Available: {', '.join(self._schemas.keys())}"
            )

        return FlextResult[SchemaPlugin].ok(self._schemas[name])

    def list_schemas(self) -> FlextResult[FlextTypes.StringList]:
        """List all registered schema system names.

        Returns:
            FlextResult containing list of schema names

        """
        return FlextResult[FlextTypes.StringList].ok(list(self._schemas.keys()))

    def unregister_schema(self, name: str) -> FlextResult[None]:
        """Unregister a schema plugin.

        Args:
            name: Schema name to unregister

        Returns:
            FlextResult indicating success or failure

        """
        if name not in self._schemas:
            return FlextResult[None].fail(f"Schema '{name}' not registered")

        del self._schemas[name]
        self._logger.info(f"Unregistered schema: {name}", extra={"schema": name})
        return FlextResult[None].ok(None)

    # Transport Registration

    def register_transport(
        self,
        name: str,
        plugin: TransportPlugin,
    ) -> FlextResult[None]:
        """Register a transport plugin.

        Args:
            name: Transport name (e.g., "httpx", "websockets", "gql")
            plugin: Transport plugin instance

        Returns:
            FlextResult indicating success or failure

        """
        if not name:
            return FlextResult[None].fail("Transport name cannot be empty")

        if name in self._transports:
            self._logger.warning(
                f"Transport '{name}' already registered, overwriting",
                extra={"transport": name},
            )

        self._transports[name] = plugin
        self._logger.info(
            f"Registered transport: {name}",
            extra={"transport": name, "plugin_type": type(plugin).__name__},
        )

        return FlextResult[None].ok(None)

    def get_transport(self, name: str) -> FlextResult[TransportPlugin]:
        """Get registered transport plugin by name.

        Args:
            name: Transport name

        Returns:
            FlextResult containing transport plugin or error

        """
        if name not in self._transports:
            return FlextResult[TransportPlugin].fail(
                f"Transport '{name}' not registered. "
                f"Available: {', '.join(self._transports.keys())}"
            )

        return FlextResult[TransportPlugin].ok(self._transports[name])

    def list_transports(self) -> FlextResult[FlextTypes.StringList]:
        """List all registered transport names.

        Returns:
            FlextResult containing list of transport names

        """
        return FlextResult[FlextTypes.StringList].ok(list(self._transports.keys()))

    def unregister_transport(self, name: str) -> FlextResult[None]:
        """Unregister a transport plugin.

        Args:
            name: Transport name to unregister

        Returns:
            FlextResult indicating success or failure

        """
        if name not in self._transports:
            return FlextResult[None].fail(f"Transport '{name}' not registered")

        del self._transports[name]
        self._logger.info(f"Unregistered transport: {name}", extra={"transport": name})
        return FlextResult[None].ok(None)

    # Authentication Provider Registration

    def register_auth_provider(
        self,
        name: str,
        plugin: AuthenticationPlugin,
    ) -> FlextResult[None]:
        """Register an authentication provider plugin.

        Args:
            name: Auth provider name (e.g., "bearer", "oauth2", "jwt")
            plugin: Authentication plugin instance

        Returns:
            FlextResult indicating success or failure

        """
        if not name:
            return FlextResult[None].fail("Auth provider name cannot be empty")

        if name in self._auth_providers:
            self._logger.warning(
                f"Auth provider '{name}' already registered, overwriting",
                extra={"auth_provider": name},
            )

        self._auth_providers[name] = plugin
        self._logger.info(
            f"Registered auth provider: {name}",
            extra={"auth_provider": name, "plugin_type": type(plugin).__name__},
        )

        return FlextResult[None].ok(None)

    def get_auth_provider(self, name: str) -> FlextResult[AuthenticationPlugin]:
        """Get registered authentication provider by name.

        Args:
            name: Auth provider name

        Returns:
            FlextResult containing auth plugin or error

        """
        if name not in self._auth_providers:
            return FlextResult[AuthenticationPlugin].fail(
                f"Auth provider '{name}' not registered. "
                f"Available: {', '.join(self._auth_providers.keys())}"
            )

        return FlextResult[AuthenticationPlugin].ok(self._auth_providers[name])

    def list_auth_providers(self) -> FlextResult[FlextTypes.StringList]:
        """List all registered authentication provider names.

        Returns:
            FlextResult containing list of auth provider names

        """
        return FlextResult[FlextTypes.StringList].ok(list(self._auth_providers.keys()))

    def unregister_auth_provider(self, name: str) -> FlextResult[None]:
        """Unregister an authentication provider.

        Args:
            name: Auth provider name to unregister

        Returns:
            FlextResult indicating success or failure

        """
        if name not in self._auth_providers:
            return FlextResult[AuthenticationPlugin].fail(
                f"Auth provider '{name}' not registered"
            )

        del self._auth_providers[name]
        self._logger.info(
            f"Unregistered auth provider: {name}", extra={"auth_provider": name}
        )
        return FlextResult[None].ok(None)

    # Utility Methods

    def get_registry_status(self) -> FlextResult[dict[str, int]]:
        """Get current registry status with plugin counts.

        Returns:
            FlextResult containing registry status dict

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

        return FlextResult[dict[str, int]].ok(status)

    def clear_all(self) -> FlextResult[None]:
        """Clear all registered plugins (mainly for testing).

        Returns:
            FlextResult indicating success

        """
        self._protocols.clear()
        self._schemas.clear()
        self._transports.clear()
        self._auth_providers.clear()

        self._logger.info("Cleared all registry plugins")
        return FlextResult[None].ok(None)


__all__ = ["FlextApiRegistry"]
