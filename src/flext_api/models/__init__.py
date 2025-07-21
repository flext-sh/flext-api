"""Pydantic models for the FLEXT API - Enterprise Management Models.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides Pydantic models for the FLEXT API, including authentication,
monitoring, pipeline, plugin, and system models.
"""

# Re-export shared models from flext_core
# Monitoring models
# Authentication models
# Re-export shared models from flext_core
from __future__ import annotations

from flext_core.domain.pydantic_base import (
    DomainBaseModel as APIResponse,  # Use DomainBaseModel as base for API responses
)
from flext_core.domain.types import PluginType

from flext_api.models.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserAPI,
)
from flext_api.models.monitoring import HealthResponse, SystemStatsResponse

# Pipeline models
from flext_api.models.pipeline import (
    ExecutionResponse,
    PipelineCreateRequest,
    PipelineExecutionRequest,
    PipelineExecutionResponse,
    PipelineListResponse,
    PipelineResponse,
    PipelineStatsResponse,
    PipelineUpdateRequest,
    RunPipelineRequest,
)

# Plugin models
from flext_api.models.plugin import (
    PluginConfigRequest,
    PluginInstallationResponse,
    PluginInstallRequest,
    PluginListResponse,
    PluginResponse,
    PluginStatsResponse,
    PluginUninstallRequest,
    PluginUpdateRequest,
)

# System models
from flext_api.models.system import (
    MaintenanceRequest,
    MaintenanceResponse,
    SystemBackupRequest,
    SystemBackupResponse,
    SystemConfigurationRequest,
    SystemStatusResponse,
)

__all__ = [
    # Re-exported from flext_core
    "APIResponse",
    # Pipeline models
    "ExecutionResponse",
    # Monitoring models
    "HealthResponse",
    # Authentication models
    "LoginRequest",
    "LoginResponse",
    # System models
    "MaintenanceRequest",
    "MaintenanceResponse",
    "PipelineCreateRequest",
    "PipelineExecutionRequest",
    "PipelineExecutionResponse",
    "PipelineListResponse",
    "PipelineResponse",
    "PipelineStatsResponse",
    "PipelineUpdateRequest",
    # Plugin models
    "PluginConfigRequest",
    "PluginInstallRequest",
    "PluginInstallationResponse",
    "PluginListResponse",
    "PluginResponse",
    "PluginStatsResponse",
    "PluginType",
    "PluginUninstallRequest",
    "PluginUpdateRequest",
    "RegisterRequest",
    "RegisterResponse",
    "RunPipelineRequest",
    "SystemBackupRequest",
    "SystemBackupResponse",
    "SystemConfigurationRequest",
    "SystemStatsResponse",
    "SystemStatusResponse",
    "UserAPI",
]
