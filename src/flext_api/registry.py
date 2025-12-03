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
    FlextRegistry,
    r,
)

from flext_api.plugins import FlextApiPlugins


class FlextApiRegistry(FlextRegistry):
    """Central registry for API plugins, protocols, schemas, and transports.

    Extends FlextRegistry to provide domain-specific registration for:
    - Protocol plugins (HTTP, WebSocket, GraphQL, gRPC, SSE)
    - Schema plugins (OpenAPI, API, JSON Schema, Protobuf, GraphQL Schema)
    - Transport plugins (httpx, websockets, gql, grpcio)
    - Authentication plugins (via FlextAuth integration)

    Usage:
        registry = FlextApiRegistry.get_global()
        registry.register_protocol(FlextApiConstants.HTTP.PROTOCOL_HTTP, FlextWebProtocolPlugin())
        registry.register_schema("openapi", OpenApiSchemaPlugin())
        registry.register_transport("httpx", FlextWebxTransport())

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
        # Create default dispatcher if not provided
        if dispatcher is None:
            dispatcher = FlextDispatcher()

        super().__init__(dispatcher=dispatcher)
        # Logger inherited from parent FlextService - no assignment needed

        # Plugin storage by category
        self._protocols: dict[str, FlextApiPlugins.Protocol] = {}
        self._schemas: dict[str, FlextApiPlugins.Schema] = {}
        self._transports: dict[str, FlextApiPlugins.Transport] = {}
        self._auth_providers: dict[str, FlextApiPlugins.Authentication] = {}

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
        plugin: FlextApiPlugins.Protocol,
    ) -> r[bool]:
        """Register a protocol plugin.

        Args:
            name: Protocol name (e.g., "http", "websocket", "graphql")
            plugin: Protocol plugin instance

        Returns:
            FlextResult indicating success or failure

        Example:
            >>> registry = FlextApiRegistry.get_global()
            >>> result = registry.register_protocol("http", FlextWebProtocolPlugin())
            >>> assert result.is_success

        """
        if not name:
            return r[bool].fail("Protocol name cannot be empty")

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

        return r[bool].ok(True)

    def get_protocol(self, name: str) -> r[FlextApiPlugins.Protocol]:
        """Get registered protocol plugin by name.

        Args:
        name: Protocol name

        Returns:
        FlextResult containing protocol plugin or error

        """
        if name not in self._protocols:
            return r[FlextApiPlugins.Protocol].fail(
                f"Protocol '{name}' not registered. "
                f"Available: {', '.join(self._protocols.keys())}"
            )

        return r[FlextApiPlugins.Protocol].ok(self._protocols[name])

    def list_protocols(self) -> r[list[str]]:
        """List all registered protocol names.

        Returns:
        FlextResult containing list of protocol names

        """
        return r[list[str]].ok(list(self._protocols.keys()))

    def unregister_protocol(self, name: str) -> r[bool]:
        """Unregister a protocol plugin.

        Args:
        name: Protocol name to unregister

        Returns:
        FlextResult indicating success or failure

        """
        if name not in self._protocols:
            return r[bool].fail(f"Protocol '{name}' not registered")

        del self._protocols[name]
        self.logger.info(f"Unregistered protocol: {name}", protocol=name)
        return r[bool].ok(True)

    # Schema Registration

    def register_schema(
        self,
        name: str,
        plugin: FlextApiPlugins.Schema,
    ) -> r[bool]:
        """Register a schema plugin.

        Args:
            name: Schema system name (e.g., "openapi", "jsonschema", "graphql")
            plugin: Schema plugin instance

        Returns:
            FlextResult indicating success or failure

        """
        if not name:
            return r[bool].fail("Schema name cannot be empty")

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

        return r[bool].ok(True)

    def get_schema(self, name: str) -> r[FlextApiPlugins.Schema]:
        """Get registered schema plugin by name.

        Args:
        name: Schema system name

        Returns:
        FlextResult containing schema plugin or error

        """
        if name not in self._schemas:
            return r[FlextApiPlugins.Schema].fail(
                f"Schema '{name}' not registered. "
                f"Available: {', '.join(self._schemas.keys())}"
            )

        return r[FlextApiPlugins.Schema].ok(self._schemas[name])

    def list_schemas(self) -> r[list[str]]:
        """List all registered schema system names.

        Returns:
        FlextResult containing list of schema names

        """
        return r[list[str]].ok(list(self._schemas.keys()))

    def unregister_schema(self, name: str) -> r[bool]:
        """Unregister a schema plugin.

        Args:
        name: Schema name to unregister

        Returns:
        FlextResult indicating success or failure

        """
        if name not in self._schemas:
            return r[bool].fail(f"Schema '{name}' not registered")

        del self._schemas[name]
        self.logger.info(f"Unregistered schema: {name}", schema=name)
        return r[bool].ok(True)

    # Transport Registration

    def register_transport(
        self,
        name: str,
        plugin: FlextApiPlugins.Transport,
    ) -> r[bool]:
        """Register a transport plugin.

        Args:
            name: Transport name (e.g., "httpx", "websockets", "gql")
            plugin: Transport plugin instance

        Returns:
            FlextResult indicating success or failure

        """
        if not name:
            return r[bool].fail("Transport name cannot be empty")

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

        return r[bool].ok(True)

    def get_transport(self, name: str) -> r[FlextApiPlugins.Transport]:
        """Get registered transport plugin by name.

        Args:
        name: Transport name

        Returns:
        FlextResult containing transport plugin or error

        """
        if name not in self._transports:
            return r[FlextApiPlugins.Transport].fail(
                f"Transport '{name}' not registered. "
                f"Available: {', '.join(self._transports.keys())}"
            )

        return r[FlextApiPlugins.Transport].ok(self._transports[name])

    def list_transports(self) -> r[list[str]]:
        """List all registered transport names.

        Returns:
        FlextResult containing list of transport names

        """
        return r[list[str]].ok(list(self._transports.keys()))

    def unregister_transport(self, name: str) -> r[bool]:
        """Unregister a transport plugin.

        Args:
        name: Transport name to unregister

        Returns:
        FlextResult indicating success or failure

        """
        if name not in self._transports:
            return r[bool].fail(f"Transport '{name}' not registered")

        del self._transports[name]
        self.logger.info(f"Unregistered transport: {name}", transport=name)
        return r[bool].ok(True)

    # Authentication Provider Registration

    def register_auth_provider(
        self,
        name: str,
        plugin: FlextApiPlugins.Authentication,
    ) -> r[bool]:
        """Register an authentication provider plugin.

        Args:
            name: Auth provider name (e.g., "bearer", "oauth2", "jwt")
            plugin: Authentication plugin instance

        Returns:
            FlextResult indicating success or failure

        """
        if not name:
            return r[bool].fail("Auth provider name cannot be empty")

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

        return r[bool].ok(True)

    def get_auth_provider(self, name: str) -> r[FlextApiPlugins.Authentication]:
        """Get registered authentication provider by name.

        Args:
        name: Auth provider name

        Returns:
        FlextResult containing auth plugin or error

        """
        if name not in self._auth_providers:
            return r[FlextApiPlugins.Authentication].fail(
                f"Auth provider '{name}' not registered. "
                f"Available: {', '.join(self._auth_providers.keys())}"
            )

        return r[FlextApiPlugins.Authentication].ok(self._auth_providers[name])

    def list_auth_providers(self) -> r[list[str]]:
        """List all registered authentication provider names.

        Returns:
        FlextResult containing list of auth provider names

        """
        return r[list[str]].ok(list(self._auth_providers.keys()))

    def unregister_auth_provider(self, name: str) -> r[bool]:
        """Unregister an authentication provider.

        Args:
        name: Auth provider name to unregister

        Returns:
        FlextResult indicating success or failure

        """
        if name not in self._auth_providers:
            return r[bool].fail(f"Auth provider '{name}' not registered")

        del self._auth_providers[name]
        self.logger.info(
            f"Unregistered auth provider: {name}", extra={"auth_provider": name}
        )
        return r[bool].ok(True)

    # Utility Methods

    def get_registry_status(self) -> r[dict[str, int]]:
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

        return r[dict[str, int]].ok(status)

    def clear_all(self) -> r[bool]:
        """Clear all registered plugins (mainly for testing).

        Returns:
        FlextResult indicating success

        """
        self._protocols.clear()
        self._schemas.clear()
        self._transports.clear()
        self._auth_providers.clear()

        self.logger.info("Cleared all registry plugins")
        return r[bool].ok(True)


__all__ = ["FlextApiRegistry"]
