"""Application layer for FLEXT API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module contains the application services that orchestrate domain logic
and coordinate between the domain and infrastructure layers.

Uses flext-core patterns for clean architecture implementation.
"""

from __future__ import annotations

# ==============================================================================
# COMMAND HANDLERS - Request processing and command handling
# ==============================================================================
from flext_api.application.handlers import (
    FlextApiAuthenticateCommand,
    FlextApiHandler,
    FlextApiResponseHandler,
    FlextAuthenticationHandler,
    FlextCreatePipelineCommand,
    FlextCreatePipelineHandler,
    FlextCreatePluginCommand,
    FlextDeletePipelineCommand,
    FlextDeletePluginCommand,
    FlextGetPipelineCommand,
    FlextGetPluginCommand,
    FlextGetSystemHealthCommand,
    FlextGetSystemHealthHandler,
    FlextGetSystemInfoCommand,
    FlextGetSystemInfoHandler,
    FlextListPipelinesCommand,
    FlextListPluginsCommand,
    FlextUpdatePipelineCommand,
    FlextUpdatePluginCommand,
)

# ==============================================================================
# APPLICATION SERVICES - Core business logic orchestration
# ==============================================================================
from flext_api.application.services.api_service import FlextAPIService
from flext_api.application.services.auth_service import FlextAuthService
from flext_api.application.services.base import (
    AuthenticationService,
    BaseAPIService,
    DualRepositoryService,
    MonitoringService,
    PipelineBaseService,
    PluginBaseService,
    SingleRepositoryService,
)
from flext_api.application.services.pipeline_service import PipelineService
from flext_api.application.services.plugin_service import PluginService
from flext_api.application.services.system_service import SystemService

# ==============================================================================
# PUBLIC APPLICATION API - Organized by semantic category
# ==============================================================================
__all__ = [
    "AuthenticationService"
    "BaseAPIService"
    "DualRepositoryService"
    "FlextAPIService"
    "FlextApiAuthenticateCommand"
    "FlextApiHandler"
    "FlextApiResponseHandler"
    "FlextAuthService"
    "FlextAuthenticationHandler"
    "FlextCreatePipelineCommand"
    "FlextCreatePipelineHandler"
    "FlextCreatePluginCommand"
    "FlextDeletePipelineCommand"
    "FlextDeletePluginCommand"
    "FlextGetPipelineCommand"
    "FlextGetPluginCommand"
    "FlextGetSystemHealthCommand"
    "FlextGetSystemHealthHandler"
    "FlextGetSystemInfoCommand"
    "FlextGetSystemInfoHandler"
    "FlextListPipelinesCommand"
    "FlextListPluginsCommand"
    "FlextUpdatePipelineCommand"
    "FlextUpdatePluginCommand"
    "MonitoringService"
    "PipelineBaseService"
    "PipelineService"
    "PluginBaseService"
    "PluginService"
    "SingleRepositoryService"
    "SystemService",
]
