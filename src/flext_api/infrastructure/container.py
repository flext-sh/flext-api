"""Dependency injection container for FLEXT API infrastructure.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the dependency injection container setup and configuration
for the FLEXT API infrastructure components.
"""

from __future__ import annotations

from typing import Any

from flext_core import DIContainer, get_container

from flext_api.domain.ports import PipelineRepository, PluginRepository
from flext_api.infrastructure.repositories.pipeline_repository import (
    InMemoryPipelineRepository,
)
from flext_api.infrastructure.repositories.plugin_repository import (
    InMemoryPluginRepository,
)

# TYPE_CHECKING imports here if needed


class FlextAPIContainer:
    """Dependency injection container for FLEXT API."""

    def __init__(self) -> None:
        """Initialize the FLEXT API container."""
        self._container = get_container()
        self._configure_dependencies()

    def _configure_dependencies(self) -> None:
        """Configure all infrastructure dependencies."""
        from typing import cast

        # Register repository implementations (no need to register concrete with concrete)
        self._container.register_singleton(
            cast("type[Any]", PipelineRepository),  # Abstract base properly typed
            InMemoryPipelineRepository,
        )
        self._container.register_singleton(
            cast("type[Any]", PluginRepository),  # Abstract base properly typed
            InMemoryPluginRepository,
        )

    def get(self, service_type: type[Any]) -> Any:
        """Get a service from the container."""
        return self._container.resolve(service_type)

    @property
    def container(self) -> DIContainer:
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


def configure_api_container() -> FlextAPIContainer:
    """Configure and get the API container."""
    global _api_container
    _api_container = FlextAPIContainer()
    return _api_container
