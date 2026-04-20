"""Plugin registry for flext-api over the canonical core registry DSL.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Callable,
    MutableMapping,
)
from typing import ClassVar

from flext_api import FlextApiPlugins, c, p, r, t, u


class FlextApiRegistry:
    """Central registry for API plugins backed by `p.Registry`."""

    PROTOCOLS: ClassVar[str] = "protocols"
    SCHEMAS: ClassVar[str] = "schemas"
    TRANSPORTS: ClassVar[str] = "transports"
    AUTH_PROVIDERS: ClassVar[str] = "auth_providers"
    _global_instance: ClassVar[FlextApiRegistry | None] = None

    _registry: p.Registry
    _protocol_cache: MutableMapping[str, FlextApiPlugins.Protocol]
    _schema_cache: MutableMapping[str, FlextApiPlugins.Schema]
    _transport_cache: MutableMapping[str, FlextApiPlugins.Transport]
    _auth_cache: MutableMapping[str, FlextApiPlugins.Authentication]

    def __init__(self, dispatcher: p.Dispatcher | None = None) -> None:
        """Initialize API registry."""
        self._registry = u.build_registry(dispatcher=dispatcher)
        self._protocol_cache = {}
        self._schema_cache = {}
        self._transport_cache = {}
        self._auth_cache = {}
        u.fetch_logger(__name__).debug("FlextApiRegistry initialized")

    @property
    def registry(self) -> p.Registry:
        """Underlying canonical registry instance."""
        return self._registry

    @classmethod
    def instance(cls) -> FlextApiRegistry:
        """Get global singleton registry instance."""
        if cls._global_instance is None:
            cls._global_instance = cls()
        return cls._global_instance

    @classmethod
    def reset_global(cls) -> None:
        """Reset global registry instance (mainly for testing)."""
        cls._global_instance = None

    def clear_all(self) -> p.Result[bool]:
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
        u.fetch_logger(__name__).info("Cleared all registry plugins")
        return r[bool].ok(value=True)

    def resolve_auth_provider(
        self, name: str
    ) -> p.Result[FlextApiPlugins.Authentication]:
        """Get registered authentication provider by name."""
        if name in self._auth_cache:
            return r[FlextApiPlugins.Authentication].ok(self._auth_cache[name])
        result = self.fetch_plugin(self.AUTH_PROVIDERS, name)
        if result.failure:
            return r[FlextApiPlugins.Authentication].fail(result.error)
        return r[FlextApiPlugins.Authentication].fail(
            "Plugin is not an Authentication type",
        )

    def resolve_protocol(self, name: str) -> p.Result[FlextApiPlugins.Protocol]:
        """Get registered protocol plugin by name."""
        if name in self._protocol_cache:
            return r[FlextApiPlugins.Protocol].ok(self._protocol_cache[name])
        result = self.fetch_plugin(self.PROTOCOLS, name)
        if result.failure:
            return r[FlextApiPlugins.Protocol].fail(result.error)
        return r[FlextApiPlugins.Protocol].fail("Plugin is not a Protocol type")

    def registry_status(self) -> p.Result[t.IntMapping]:
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
        return r[t.IntMapping].ok(status)

    def resolve_schema(self, name: str) -> p.Result[FlextApiPlugins.Schema]:
        """Get registered schema plugin by name."""
        if name in self._schema_cache:
            return r[FlextApiPlugins.Schema].ok(self._schema_cache[name])
        result = self.fetch_plugin(self.SCHEMAS, name)
        if result.failure:
            return r[FlextApiPlugins.Schema].fail(result.error)
        return r[FlextApiPlugins.Schema].fail("Plugin is not a Schema type")

    def resolve_transport(self, name: str) -> p.Result[FlextApiPlugins.Transport]:
        """Get registered transport plugin by name."""
        if name in self._transport_cache:
            return r[FlextApiPlugins.Transport].ok(self._transport_cache[name])
        result = self.fetch_plugin(self.TRANSPORTS, name)
        if result.failure:
            return r[FlextApiPlugins.Transport].fail(result.error)
        return r[FlextApiPlugins.Transport].fail("Plugin is not a Transport type")

    def list_auth_providers(self) -> p.Result[t.StrSequence]:
        """List all registered authentication provider names."""
        return self.list_plugins(self.AUTH_PROVIDERS)

    def list_protocols(self) -> p.Result[t.StrSequence]:
        """List all registered protocol names."""
        return self.list_plugins(self.PROTOCOLS)

    def list_schemas(self) -> p.Result[t.StrSequence]:
        """List all registered schema system names."""
        return self.list_plugins(self.SCHEMAS)

    def list_transports(self) -> p.Result[t.StrSequence]:
        """List all registered transport names."""
        return self.list_plugins(self.TRANSPORTS)

    def register_auth_provider(
        self,
        name: str,
        plugin: FlextApiPlugins.Authentication,
    ) -> p.Result[bool]:
        """Register an authentication provider plugin."""
        self._auth_cache[name] = plugin
        return self.register_plugin(self.AUTH_PROVIDERS, name, plugin.name)

    def register_protocol(
        self, name: str, plugin: FlextApiPlugins.Protocol
    ) -> p.Result[bool]:
        """Register a protocol plugin."""
        self._protocol_cache[name] = plugin
        return self.register_plugin(self.PROTOCOLS, name, plugin.name)

    def register_schema(
        self, name: str, plugin: FlextApiPlugins.Schema
    ) -> p.Result[bool]:
        """Register a schema plugin."""
        self._schema_cache[name] = plugin
        return self.register_plugin(self.SCHEMAS, name, plugin.name)

    def register_transport(
        self,
        name: str,
        plugin: FlextApiPlugins.Transport,
    ) -> p.Result[bool]:
        """Register a transport plugin."""
        self._transport_cache[name] = plugin
        return self.register_plugin(self.TRANSPORTS, name, plugin.name)

    def unregister_auth_provider(self, name: str) -> p.Result[bool]:
        """Unregister an authentication provider."""
        return self.unregister_plugin(self.AUTH_PROVIDERS, name)

    def unregister_protocol(self, name: str) -> p.Result[bool]:
        """Unregister a protocol plugin."""
        return self.unregister_plugin(self.PROTOCOLS, name)

    def unregister_schema(self, name: str) -> p.Result[bool]:
        """Unregister a schema plugin."""
        return self.unregister_plugin(self.SCHEMAS, name)

    def unregister_transport(self, name: str) -> p.Result[bool]:
        """Unregister a transport plugin."""
        return self.unregister_plugin(self.TRANSPORTS, name)

    def fetch_plugin(
        self,
        category: str,
        name: str,
        *,
        scope: c.RegistrationScope = c.RegistrationScope.INSTANCE,
    ) -> p.Result[t.RuntimeData | None]:
        """Delegate plugin lookup to the canonical registry."""
        return r[t.RuntimeData | None].from_result(
            self._registry.fetch_plugin(category, name, scope=scope),
        )

    def list_plugins(
        self,
        category: str,
        *,
        scope: c.RegistrationScope = c.RegistrationScope.INSTANCE,
    ) -> p.Result[t.StrSequence]:
        """Delegate plugin listing to the canonical registry."""
        return r[t.StrSequence].from_result(
            self._registry.list_plugins(category, scope=scope),
        )

    def register_plugin(
        self,
        category: str,
        name: str,
        plugin: t.RegistrablePlugin,
        *,
        validate: Callable[[t.RegistrablePlugin], p.Result[bool]] | None = None,
        scope: c.RegistrationScope = c.RegistrationScope.INSTANCE,
    ) -> p.Result[bool]:
        """Delegate plugin registration to the canonical registry."""
        return r[bool].from_result(
            self._registry.register_plugin(
                category,
                name,
                plugin,
                validate=validate,
                scope=scope,
            ),
        )

    def unregister_plugin(
        self,
        category: str,
        name: str,
        *,
        scope: c.RegistrationScope = c.RegistrationScope.INSTANCE,
    ) -> p.Result[bool]:
        """Delegate plugin removal to the canonical registry."""
        return r[bool].from_result(
            self._registry.unregister_plugin(category, name, scope=scope),
        )


__all__: list[str] = ["FlextApiRegistry"]
