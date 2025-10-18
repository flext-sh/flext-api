"""Generic Resource Lifecycle Manager - Domain-agnostic resource management.

This module provides HttpLifecycleManager for managing resource
initialization, cleanup, and lifecycle with flext-core patterns.
Completely domain-agnostic and reusable.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Protocol

from flext_core import FlextResult


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

    def health_check(self) -> bool:
        """Check if the resource is healthy."""
        ...


class LifecycleError(Exception):
    """Exception raised for lifecycle management errors."""


class HttpLifecycleManager:
    """Generic lifecycle management for resource initialization and cleanup.

    Manages the complete lifecycle of resources with proper error handling
    and cleanup guarantees. Domain-agnostic and reusable across any system.
    """

    def __init__(self) -> None:
        """Initialize lifecycle manager."""
        self._logger = logging.getLogger(__name__)
        self._initialized = False
        self._resources: list[ResourceProtocol] = []

    @property
    def initialized(self) -> bool:
        """Check if lifecycle manager is initialized."""
        return self._initialized

    async def initialize(
        self, config: dict[str, Any] | None = None
    ) -> FlextResult[None]:
        """Initialize resources with comprehensive error handling."""
        try:
            if self._initialized:
                return FlextResult[None].ok(None)

            # Initialize resources
            await self._initialize_resources(config)

            self._initialized = True
            return FlextResult[None].ok(None)

        except Exception as e:
            await self._cleanup_resources()
            return FlextResult[None].fail(f"Initialization failed: {e}")

    async def _initialize_resources(self, config: dict[str, Any] | None = None) -> None:
        """Initialize additional resources."""
        # Initialize any additional resources needed

    async def shutdown(self) -> FlextResult[None]:
        """Shutdown lifecycle and cleanup all resources."""
        try:
            if not self._initialized:
                return FlextResult[None].ok(None)

            await self._cleanup_resources()

            self._resources.clear()
            self._initialized = False

            return FlextResult[None].ok(None)

        except Exception as e:
            return FlextResult[None].fail(f"Shutdown failed: {e}")

    async def _cleanup_resources(self) -> None:
        """Cleanup all managed resources with error resilience."""
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
                self._logger.warning("Failed to cleanup resource: %s", e)

        self._resources.clear()

    def add_resource(self, resource: ResourceProtocol) -> None:
        """Add a resource to be managed by the lifecycle."""
        self._resources.append(resource)

    def remove_resource(self, resource: ResourceProtocol) -> None:
        """Remove a resource from lifecycle management."""
        if resource in self._resources:
            self._resources.remove(resource)

    @asynccontextmanager
    async def lifecycle_context(
        self, config: dict[str, Any] | None = None
    ) -> AsyncIterator[HttpLifecycleManager]:
        """Context manager for lifecycle management with automatic cleanup."""
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

    def get_status(self) -> dict[str, Any]:
        """Get lifecycle status for monitoring."""
        return {
            "initialized": self._initialized,
            "managed_resources": len(self._resources),
        }

    def health_check(self) -> FlextResult[bool]:
        """Perform health check on lifecycle components."""
        try:
            if not self._initialized:
                return FlextResult[bool].fail("Lifecycle not initialized")

            # Check resources
            unhealthy_resources = []
            for i, resource in enumerate(self._resources):
                if hasattr(resource, "health_check"):
                    if asyncio.iscoroutinefunction(resource.health_check):
                        # Assume healthy for async health checks
                        pass
                    else:
                        try:
                            health = resource.health_check()
                            if not health:
                                unhealthy_resources.append(f"resource_{i}")
                        except Exception as e:
                            unhealthy_resources.append(f"resource_{i}: {e}")

            if unhealthy_resources:
                return FlextResult[bool].fail(
                    f"Unhealthy resources: {unhealthy_resources}"
                )

            return FlextResult[bool].ok(True)

        except Exception as e:
            return FlextResult[bool].fail(f"Health check failed: {e}")
