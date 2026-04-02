"""Plugin Registry for flext-api.

Centralized registry system for protocols, schemas, transports, and authentication providers.
Extends FlextRegistry from flext-core for consistency.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from typing import ClassVar

from flext_api import FlextApiPlugins, p, t
from flext_core import FlextRegistry, r


class FlextApiRegistry(FlextRegistry):
    """Central registry for API plugins, protocols, schemas, and transports.

    Extends FlextRegistry to provide domain-specific registration for:
    - Protocol plugins (HTTP, WebSocket, GraphQL, gRPC, SSE)
    - Schema plugins (OpenAPI, API, JSON Schema, Protobuf, GraphQL Schema)
    - Transport plugins (httpx, websockets, gql, grpcio)
    - Authentication plugins (via FlextAuth integration)

    Uses the generic plugin API from FlextRegistry for consistent patterns.
    """

    PROTOCOLS: ClassVar[str] = "protocols"
    SCHEMAS: ClassVar[str] = "schemas"
    TRANSPORTS: ClassVar[str] = "transports"
    AUTH_PROVIDERS: ClassVar[str] = "auth_providers"
    _global_instance: ClassVar[FlextApiRegistry | None] = None
    _protocol_cache: MutableMapping[str, FlextApiPlugins.Protocol]
    _schema_cache: MutableMapping[str, FlextApiPlugins.Schema]
    _transport_cache: MutableMapping[str, FlextApiPlugins.Transport]
    _auth_cache: MutableMapping[str, FlextApiPlugins.Authentication]

    def __init__(self, dispatcher: p.Dispatcher | None = None) -> None:
        """Initialize API registry."""
        super().__init__(dispatcher=dispatcher)
        self._protocol_cache: MutableMapping[str, FlextApiPlugins.Protocol] = {}
        self._schema_cache: MutableMapping[str, FlextApiPlugins.Schema] = {}
        self._transport_cache: MutableMapping[str, FlextApiPlugins.Transport] = {}
        self._auth_cache: MutableMapping[str, FlextApiPlugins.Authentication] = {}
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
        return r[bool].ok(value=True)

    def get_auth_provider(self, name: str) -> r[FlextApiPlugins.Authentication]:
        """Get registered authentication provider by name."""
        if name in self._auth_cache:
            return r[FlextApiPlugins.Authentication].ok(self._auth_cache[name])
        result = self.get_plugin(self.AUTH_PROVIDERS, name)
        if result.is_failure:
            return r[FlextApiPlugins.Authentication].fail(result.error)
        return r[FlextApiPlugins.Authentication].fail(
            "Plugin is not an Authentication type",
        )

    def get_protocol(self, name: str) -> r[FlextApiPlugins.Protocol]:
        """Get registered protocol plugin by name."""
        if name in self._protocol_cache:
            return r[FlextApiPlugins.Protocol].ok(self._protocol_cache[name])
        result = self.get_plugin(self.PROTOCOLS, name)
        if result.is_failure:
            return r[FlextApiPlugins.Protocol].fail(result.error)
        return r[FlextApiPlugins.Protocol].fail("Plugin is not a Protocol type")

    def get_registry_status(self) -> r[Mapping[str, int]]:
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
        return r[Mapping[str, int]].ok(status)

    def get_schema(self, name: str) -> r[FlextApiPlugins.Schema]:
        """Get registered schema plugin by name."""
        if name in self._schema_cache:
            return r[FlextApiPlugins.Schema].ok(self._schema_cache[name])
        result = self.get_plugin(self.SCHEMAS, name)
        if result.is_failure:
            return r[FlextApiPlugins.Schema].fail(result.error)
        return r[FlextApiPlugins.Schema].fail("Plugin is not a Schema type")

    def get_transport(self, name: str) -> r[FlextApiPlugins.Transport]:
        """Get registered transport plugin by name."""
        if name in self._transport_cache:
            return r[FlextApiPlugins.Transport].ok(self._transport_cache[name])
        result = self.get_plugin(self.TRANSPORTS, name)
        if result.is_failure:
            return r[FlextApiPlugins.Transport].fail(result.error)
        return r[FlextApiPlugins.Transport].fail("Plugin is not a Transport type")

    def list_auth_providers(self) -> r[t.StrSequence]:
        """List all registered authentication provider names."""
        return self.list_plugins(self.AUTH_PROVIDERS)

    def list_protocols(self) -> r[t.StrSequence]:
        """List all registered protocol names."""
        return self.list_plugins(self.PROTOCOLS)

    def list_schemas(self) -> r[t.StrSequence]:
        """List all registered schema system names."""
        return self.list_plugins(self.SCHEMAS)

    def list_transports(self) -> r[t.StrSequence]:
        """List all registered transport names."""
        return self.list_plugins(self.TRANSPORTS)

    def register_auth_provider(
        self,
        name: str,
        plugin: FlextApiPlugins.Authentication,
    ) -> r[bool]:
        """Register an authentication provider plugin."""
        self._auth_cache[name] = plugin
        return self.register_plugin(self.AUTH_PROVIDERS, name, plugin.name)

    def register_protocol(self, name: str, plugin: FlextApiPlugins.Protocol) -> r[bool]:
        """Register a protocol plugin."""
        self._protocol_cache[name] = plugin
        return self.register_plugin(self.PROTOCOLS, name, plugin.name)

    def register_schema(self, name: str, plugin: FlextApiPlugins.Schema) -> r[bool]:
        """Register a schema plugin."""
        self._schema_cache[name] = plugin
        return self.register_plugin(self.SCHEMAS, name, plugin.name)

    def register_transport(
        self,
        name: str,
        plugin: FlextApiPlugins.Transport,
    ) -> r[bool]:
        """Register a transport plugin."""
        self._transport_cache[name] = plugin
        return self.register_plugin(self.TRANSPORTS, name, plugin.name)

    def unregister_auth_provider(self, name: str) -> r[bool]:
        """Unregister an authentication provider."""
        return self.unregister_plugin(self.AUTH_PROVIDERS, name)

    def unregister_protocol(self, name: str) -> r[bool]:
        """Unregister a protocol plugin."""
        return self.unregister_plugin(self.PROTOCOLS, name)

    def unregister_schema(self, name: str) -> r[bool]:
        """Unregister a schema plugin."""
        return self.unregister_plugin(self.SCHEMAS, name)

    def unregister_transport(self, name: str) -> r[bool]:
        """Unregister a transport plugin."""
        return self.unregister_plugin(self.TRANSPORTS, name)


__all__ = ["FlextApiRegistry"]
