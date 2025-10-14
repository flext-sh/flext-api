"""Lifecycle Management for FlextApiClient.

This module contains lifecycle management functionality extracted from FlextApiClient
to handle initialization, startup, shutdown, and resource management.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Protocol

from flext_core import FlextCore

# Optional imports for protocol plugins
try:
    from flext_api.protocol_impls.graphql import (
        GraphQLProtocolPlugin,
    )
except ImportError:
    GraphQLProtocolPlugin = None

try:
    from flext_api.protocol_impls.http import (
        HttpProtocolPlugin,
    )
except ImportError:
    HttpProtocolPlugin = None

try:
    from flext_api.protocol_impls.websocket import (
        WebSocketProtocolPlugin,
    )
except ImportError:
    WebSocketProtocolPlugin = None
from flext_api.protocols import FlextApiProtocols
from flext_api.registry import FlextApiRegistry


class LifecycleError(Exception):
    """Exception raised for lifecycle management errors."""


class ResourceProtocol(Protocol):
    """Protocol for resources that can be managed by lifecycle manager."""

    def close(self) -> None:
        """Close the resource synchronously."""
        ...

    async def aclose(self) -> None:
        """Close the resource asynchronously."""
        ...

    def cleanup(self) -> None:
        """Cleanup the resource synchronously."""
        ...


class LifecycleManager:
    """Lifecycle management for FlextApiClient initialization and cleanup."""

    def __init__(self) -> None:
        """Initialize lifecycle manager."""
        self._logger = logging.getLogger(__name__)
        self._initialized = False
        self._registry: FlextApiRegistry | None = None
        self._protocols: FlextApiProtocols | None = None
        self._resources: list[ResourceProtocol | object] = []

    @property
    def initialized(self) -> bool:
        """Check if lifecycle manager is initialized."""
        return self._initialized

    @property
    def registry(self) -> FlextApiRegistry | None:
        """Get the protocol registry."""
        return self._registry

    @property
    def protocols(self) -> FlextApiProtocols | None:
        """Get the protocols interface."""
        return self._protocols

    async def initialize(
        self, config: dict[str, object] | None = None
    ) -> FlextCore.Result[None]:
        """Initialize the client lifecycle.

        Args:
            config: Optional initialization configuration

        Returns:
            FlextCore.Result indicating success or failure

        """
        try:
            if self._initialized:
                return FlextCore.Result[None].ok(None)  # Already initialized

            # Initialize registry
            self._registry = FlextApiRegistry()
            await self._initialize_registry()

            # Initialize protocols
            self._protocols = FlextApiProtocols()
            await self._initialize_protocols()

            # Initialize other resources
            await self._initialize_resources(config)

            self._initialized = True
            return FlextCore.Result[None].ok(None)

        except Exception as e:
            await self._cleanup_resources()
            return FlextCore.Result[None].fail(f"Initialization failed: {e}")

    async def _initialize_registry(self) -> None:
        """Initialize the protocol registry."""
        if self._registry is None:
            return

        # Register core protocols
        try:
            # Register HTTP protocol
            if HttpProtocolPlugin is not None:
                self._registry.register_protocol("http", HttpProtocolPlugin())

            # Try to register other protocols if available
            if GraphQLProtocolPlugin is not None:
                try:
                    self._registry.register_protocol("graphql", GraphQLProtocolPlugin())
                except (ImportError, AttributeError) as e:
                    self._logger.debug("GraphQL protocol not available: %s", e)

            if WebSocketProtocolPlugin is not None:
                try:
                    self._registry.register_protocol(
                        "websocket", WebSocketProtocolPlugin()
                    )
                except (ImportError, AttributeError) as e:
                    self._logger.debug("WebSocket protocol not available: %s", e)

        except Exception as e:
            # Continue without optional protocols
            self._logger.warning("Failed to initialize optional protocols: %s", e)

    async def _initialize_protocols(self) -> None:
        """Initialize protocol interfaces."""
        # Protocol interfaces are initialized on-demand

    async def _initialize_resources(
        self, config: dict[str, object] | None = None
    ) -> None:
        """Initialize additional resources."""
        # Initialize any additional resources needed

    async def shutdown(self) -> FlextCore.Result[None]:
        """Shutdown the client lifecycle and cleanup resources.

        Returns:
            FlextCore.Result indicating success or failure

        """
        try:
            if not self._initialized:
                return FlextCore.Result[None].ok(None)  # Not initialized

            # Cleanup resources
            await self._cleanup_resources()

            # Reset state
            self._registry = None
            self._protocols = None
            self._resources.clear()
            self._initialized = False

            return FlextCore.Result[None].ok(None)

        except Exception as e:
            return FlextCore.Result[None].fail(f"Shutdown failed: {e}")

    async def _cleanup_resources(self) -> None:
        """Cleanup all managed resources."""
        for resource in self._resources:
            try:
                if hasattr(resource, "close"):
                    if asyncio.iscoroutinefunction(resource.close):
                        await resource.close()
                    else:
                        resource.close()
                elif hasattr(resource, "cleanup"):
                    if asyncio.iscoroutinefunction(resource.cleanup):
                        await resource.cleanup()
                    else:
                        resource.cleanup()
            except Exception as e:
                # Continue cleanup even if one resource fails
                self._logger.warning("Failed to cleanup resource: %s", e)

        self._resources.clear()

    def add_resource(self, resource: ResourceProtocol | object) -> None:
        """Add a resource to be managed by the lifecycle.

        Args:
            resource: Resource with close() or cleanup() method

        """
        self._resources.append(resource)

    def remove_resource(self, resource: ResourceProtocol | object) -> None:
        """Remove a resource from lifecycle management.

        Args:
            resource: Resource to remove

        """
        if resource in self._resources:
            self._resources.remove(resource)

    @asynccontextmanager
    async def lifecycle_context(
        self, config: dict[str, object] | None = None
    ) -> AbstractAsyncContextManager[LifecycleManager]:
        """Context manager for lifecycle management.

        Args:
            config: Optional initialization configuration

        Yields:
            LifecycleManager instance

        Raises:
            LifecycleError: If initialization fails

        """
        init_result = await self.initialize(config)
        if init_result.is_failure:
            msg = f"Failed to initialize lifecycle: {init_result.error}"
            raise LifecycleError(msg)

        try:
            yield self
        finally:
            shutdown_result = await self.shutdown()
            if shutdown_result.is_failure:
                # Log error but don't raise to avoid masking original exceptions
                pass

    def get_status(self) -> dict[str, object]:
        """Get lifecycle status for monitoring."""
        return {
            "initialized": self._initialized,
            "registry_available": self._registry is not None,
            "protocols_available": self._protocols is not None,
            "managed_resources": len(self._resources),
            "registry_protocols": (
                getattr(self._registry, "list_protocols", list)()
                if self._registry
                else []
            ),
        }

    def health_check(self) -> FlextCore.Result[bool]:
        """Perform health check on lifecycle components.

        Returns:
            FlextCore.Result with health status

        """
        try:
            if not self._initialized:
                return FlextCore.Result[bool].fail("Lifecycle not initialized")

            # Check registry
            if self._registry is None:
                return FlextCore.Result[bool].fail("Registry not available")

            # Check protocols
            if self._protocols is None:
                return FlextCore.Result[bool].fail("Protocols not available")

            # Check resources
            unhealthy_resources = []
            for i, resource in enumerate(self._resources):
                if hasattr(resource, "health_check"):
                    if asyncio.iscoroutinefunction(resource.health_check):
                        # For async health checks, assume healthy for now
                        pass
                    else:
                        try:
                            health = resource.health_check()
                            if not health:
                                unhealthy_resources.append(f"resource_{i}")
                        except Exception as e:
                            unhealthy_resources.append(f"resource_{i}: {e}")

            if unhealthy_resources:
                return FlextCore.Result[bool].fail(
                    f"Unhealthy resources: {unhealthy_resources}"
                )

            return FlextCore.Result[bool].ok(True)

        except Exception as e:
            return FlextCore.Result[bool].fail(f"Health check failed: {e}")


__all__ = ["LifecycleManager"]
