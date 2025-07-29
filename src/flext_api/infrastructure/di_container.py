"""Dependency injection configuration for FLEXT-API using flext-core DI.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the dependency injection configuration for the FLEXT API.
"""

from __future__ import annotations

from typing import Any

from flext_core import (
    FlextError,
    get_flext_container,
)

from flext_api.application.services.auth_service import FlextAuthService
from flext_api.application.services.pipeline_service import PipelineService
from flext_api.application.services.plugin_service import PluginService
from flext_api.application.services.system_service import SystemService
from flext_api.infrastructure.config import APIConfig
from flext_api.infrastructure.repositories.pipeline_repository import (
    FlextInMemoryPipelineRepository,
)


def configure_api_dependencies() -> None:
    """Configure API dependencies using DI - NO DIRECT IMPORTS."""
    container = get_flext_container()
    settings = APIConfig()

    # Register settings with string key
    container.register("APIConfig", settings)

    # Register repositories as factories with string keys
    container.register_factory(
        "FlextInMemoryPipelineRepository",
        FlextInMemoryPipelineRepository,
    )

    # Register auth service with DI - NO DIRECT IMPORTS
    def create_flext_auth_service() -> FlextAuthService:
        """Create auth service using DI container."""
        try:
            # Use DI container to get auth services
            # This avoids direct imports from flext-auth
            from flext_api.infrastructure.ports import FlextApiAuthPort

            auth_port = FlextApiAuthPort.get_instance()
            if auth_port:
                # Get services from auth port
                auth_service = getattr(auth_port, "auth_service", None)
                session_service = getattr(auth_port, "session_service", None)

                return FlextAuthService(
                    auth_service=auth_service,
                    session_service=session_service,
                )
            # Fallback to service without external dependencies
            return FlextAuthService()

        except Exception as e:
            msg = f"Failed to create auth service: {e}"
            raise FlextError(msg) from e

    container.register_factory(
        "FlextAuthService",
        create_flext_auth_service,
    )

    # Register gRPC service with DI - NO DIRECT IMPORTS
    def create_flext_grpc_service() -> Any:
        """Create gRPC service using DI container."""
        try:
            from flext_api.infrastructure.ports import FlextApiGrpcPort

            grpc_port = FlextApiGrpcPort.get_instance()
            if grpc_port:
                return grpc_port
            return None

        except Exception as e:
            msg = f"Failed to create gRPC service: {e}"
            raise FlextError(msg) from e

    container.register_factory(
        "FlextGrpcService",
        create_flext_grpc_service,
    )

    # Register plugin service with DI - NO DIRECT IMPORTS
    def create_flext_plugin_service() -> Any:
        """Create plugin service using DI container."""
        try:
            from flext_api.infrastructure.ports import FlextApiPluginPort

            plugin_port = FlextApiPluginPort.get_instance()
            if plugin_port:
                return plugin_port
            return None

        except Exception as e:
            msg = f"Failed to create plugin service: {e}"
            raise FlextError(msg) from e

    container.register_factory(
        "FlextPluginService",
        create_flext_plugin_service,
    )

    # Application services are auto-registered via @injectable decorator
    # Just need to ensure they're imported
    _ = FlextAuthService
    _ = PipelineService
    _ = PluginService
    _ = SystemService

    # Configure any flext-core dependencies needed
    settings.configure_dependencies(container)
