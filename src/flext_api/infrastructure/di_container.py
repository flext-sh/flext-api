"""Dependency injection configuration for FLEXT-API using flext-core DI.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the dependency injection configuration for the FLEXT API.
"""

from __future__ import annotations

from flext_api.application.services.auth_service import AuthService
from flext_api.application.services.pipeline_service import PipelineService
from flext_api.application.services.plugin_service import PluginService
from flext_api.application.services.system_service import SystemService
from flext_api.config import get_api_settings
from flext_api.infrastructure.repositories.memory_repositories import (
    InMemoryPipelineRepository,
)
from flext_api.infrastructure.repositories.memory_repositories import (
    InMemoryPluginRepository,
)
from flext_core.config import get_container


def configure_api_dependencies() -> None:
    container = get_container()
    settings = get_api_settings()

    # Register settings
    container.register(type(settings), settings)

    # Register repositories as singletons
    container.register_singleton(
        "PipelineRepository",
        InMemoryPipelineRepository,
    )
    container.register_singleton(
        "PluginRepository",
        InMemoryPluginRepository,
    )

    # Register auth service
    container.register_singleton(
        "AuthService",
        AuthService,
    )

    # Application services are auto-registered via @injectable decorator
    # Just need to ensure they're imported
    _ = AuthService
    _ = PipelineService
    _ = PluginService
    _ = SystemService

    # Configure any flext-core dependencies needed
    settings.configure_dependencies(container)
