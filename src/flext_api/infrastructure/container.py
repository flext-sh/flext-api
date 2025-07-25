"""Dependency injection container for FLEXT API infrastructure.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the dependency injection container setup and configuration
for the FLEXT API infrastructure components.
"""

from __future__ import annotations

from typing import Any

from flext_core import FlextContainer, get_flext_container

from flext_api.infrastructure.repositories.pipeline_repository import (
    FlextInMemoryPipelineRepository,
)
from flext_api.infrastructure.repositories.plugin_repository import (
    FlextInMemoryPluginRepository,
)


class FlextAPIContainer:
    """Dependency injection container for FLEXT API."""

    def __init__(self) -> None:
        """Initialize the FLEXT API container."""
        self._container = get_flext_container()
        self._configure_dependencies()

    def _configure_dependencies(self) -> None:
        """Configure all infrastructure dependencies."""
        # Register repository implementations using correct FlextContainer API
        pipeline_repo = FlextInMemoryPipelineRepository()
        plugin_repo = FlextInMemoryPluginRepository()

        self._container.register("PipelineRepository", pipeline_repo)
        self._container.register("PluginRepository", plugin_repo)

    def get(self, service_name: str) -> Any:
        """Get a service using FLEXT service resolution pattern."""
        from flext_core import FlextError

        result = self._container.get(service_name)
        if result.is_success:
            return result.data
        # Use proper FLEXT exception hierarchy instead of generic RuntimeError
        msg = f"Service {service_name} not found"
        msg = f"{msg}: {result.error}"
        raise FlextError(msg)

    @property
    def container(self) -> FlextContainer:
        """Get the underlying DI container."""
        return self._container


# Global container instance
_api_container: FlextAPIContainer | None = None


def get_api_container() -> FlextAPIContainer:
    """Get the global API container instance."""
    global _api_container
    if _api_container is None:
        _api_container = FlextAPIContainer()
    return _api_container
