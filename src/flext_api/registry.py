"""Plugin Registry for flext-api.

Centralized registry system for protocols, schemas, transports, and authentication providers.
Extends FlextRegistry from flext-core for consistency.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar, cast

from flext_core import FlextRegistry, r
from flext_core.protocols import p

from flext_api.plugins import FlextApiPlugins
from flext_api.typings import t


class FlextApiRegistry(FlextRegistry):
    """Central registry for API plugins, protocols, schemas, and transports.

    Extends FlextRegistry to provide domain-specific registration for:
    - Protocol plugins (HTTP, WebSocket, GraphQL, gRPC, SSE)
    - Schema plugins (OpenAPI, API, JSON Schema, Protobuf, GraphQL Schema)
    - Transport plugins (httpx, websockets, gql, grpcio)
    - Authentication plugins (via FlextAuth integration)

    Uses the generic plugin API from FlextRegistry for consistent patterns.
    """

    # Plugin category constants
    PROTOCOLS: ClassVar[str] = "protocols"
    SCHEMAS: ClassVar[str] = "schemas"
    TRANSPORTS: ClassVar[str] = "transports"
    AUTH_PROVIDERS: ClassVar[str] = "auth_providers"

    _global_instance: ClassVar[FlextApiRegistry | None] = None

    def __init__(self, dispatcher: p.CommandBus | None = None) -> None:
        """Initialize API registry."""
        super().__init__(dispatcher=dispatcher)
        self.logger.debug("FlextApiRegistry initialized")

    @classmethod
    def get_global(cls) -> FlextApiRegistry:
        """Get global singleton registry instance."""
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
        """Register a protocol plugin."""
        return self.register_plugin(
            self.PROTOCOLS, name, cast("t.GeneralValueType", plugin)
        )

    def get_protocol(self, name: str) -> r[FlextApiPlugins.Protocol]:
        """Get registered protocol plugin by name."""
        result = self.get_plugin(self.PROTOCOLS, name)
        if result.is_success and isinstance(result.value, FlextApiPlugins.Protocol):
            return r[FlextApiPlugins.Protocol].ok(result.value)
        if result.is_failure:
            return r[FlextApiPlugins.Protocol].fail(result.error)
        return r[FlextApiPlugins.Protocol].fail("Plugin is not a Protocol type")

    def list_protocols(self) -> r[list[str]]:
        """List all registered protocol names."""
        return self.list_plugins(self.PROTOCOLS)

    def unregister_protocol(self, name: str) -> r[bool]:
        """Unregister a protocol plugin."""
        return self.unregister_plugin(self.PROTOCOLS, name)

    # Schema Registration

    def register_schema(
        self,
        name: str,
        plugin: FlextApiPlugins.Schema,
    ) -> r[bool]:
        """Register a schema plugin."""
        return self.register_plugin(
            self.SCHEMAS, name, cast("t.GeneralValueType", plugin)
        )

    def get_schema(self, name: str) -> r[FlextApiPlugins.Schema]:
        """Get registered schema plugin by name."""
        result = self.get_plugin(self.SCHEMAS, name)
        if result.is_success and isinstance(result.value, FlextApiPlugins.Schema):
            return r[FlextApiPlugins.Schema].ok(result.value)
        if result.is_failure:
            return r[FlextApiPlugins.Schema].fail(result.error)
        return r[FlextApiPlugins.Schema].fail("Plugin is not a Schema type")

    def list_schemas(self) -> r[list[str]]:
        """List all registered schema system names."""
        return self.list_plugins(self.SCHEMAS)

    def unregister_schema(self, name: str) -> r[bool]:
        """Unregister a schema plugin."""
        return self.unregister_plugin(self.SCHEMAS, name)

    # Transport Registration

    def register_transport(
        self,
        name: str,
        plugin: FlextApiPlugins.Transport,
    ) -> r[bool]:
        """Register a transport plugin."""
        return self.register_plugin(
            self.TRANSPORTS, name, cast("t.GeneralValueType", plugin)
        )

    def get_transport(self, name: str) -> r[FlextApiPlugins.Transport]:
        """Get registered transport plugin by name."""
        result = self.get_plugin(self.TRANSPORTS, name)
        if result.is_success and isinstance(result.value, FlextApiPlugins.Transport):
            return r[FlextApiPlugins.Transport].ok(result.value)
        if result.is_failure:
            return r[FlextApiPlugins.Transport].fail(result.error)
        return r[FlextApiPlugins.Transport].fail("Plugin is not a Transport type")

    def list_transports(self) -> r[list[str]]:
        """List all registered transport names."""
        return self.list_plugins(self.TRANSPORTS)

    def unregister_transport(self, name: str) -> r[bool]:
        """Unregister a transport plugin."""
        return self.unregister_plugin(self.TRANSPORTS, name)

    # Authentication Provider Registration

    def register_auth_provider(
        self,
        name: str,
        plugin: FlextApiPlugins.Authentication,
    ) -> r[bool]:
        """Register an authentication provider plugin."""
        return self.register_plugin(
            self.AUTH_PROVIDERS, name, cast("t.GeneralValueType", plugin)
        )

    def get_auth_provider(self, name: str) -> r[FlextApiPlugins.Authentication]:
        """Get registered authentication provider by name."""
        result = self.get_plugin(self.AUTH_PROVIDERS, name)
        if result.is_success and isinstance(
            result.value, FlextApiPlugins.Authentication
        ):
            return r[FlextApiPlugins.Authentication].ok(result.value)
        if result.is_failure:
            return r[FlextApiPlugins.Authentication].fail(result.error)
        return r[FlextApiPlugins.Authentication].fail(
            "Plugin is not an Authentication type"
        )

    def list_auth_providers(self) -> r[list[str]]:
        """List all registered authentication provider names."""
        return self.list_plugins(self.AUTH_PROVIDERS)

    def unregister_auth_provider(self, name: str) -> r[bool]:
        """Unregister an authentication provider."""
        return self.unregister_plugin(self.AUTH_PROVIDERS, name)

    # Utility Methods

    def get_registry_status(self) -> r[dict[str, int]]:
        """Get current registry status with plugin counts."""
        protocols = self.list_plugins(self.PROTOCOLS).value or []
        schemas = self.list_plugins(self.SCHEMAS).value or []
        transports = self.list_plugins(self.TRANSPORTS).value or []
        auth_providers = self.list_plugins(self.AUTH_PROVIDERS).value or []

        status = {
            "protocols": len(protocols),
            "schemas": len(schemas),
            "transports": len(transports),
            "auth_providers": len(auth_providers),
            "total": len(protocols)
            + len(schemas)
            + len(transports)
            + len(auth_providers),
        }
        return r[dict[str, int]].ok(status)

    def clear_all(self) -> r[bool]:
        """Clear all registered plugins (mainly for testing)."""
        for category in [
            self.PROTOCOLS,
            self.SCHEMAS,
            self.TRANSPORTS,
            self.AUTH_PROVIDERS,
        ]:
            plugins = self.list_plugins(category).value or []
            for name in plugins:
                self.unregister_plugin(category, name)

        self.logger.info("Cleared all registry plugins")
        return r[bool].ok(True)


__all__ = ["FlextApiRegistry"]
