"""Pydantic models for the FLEXT API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.models.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserAPI,
)
from flext_api.models.monitoring import HealthResponse, SystemStatsResponse

# Pipeline models - restored after fixing syntax errors
from flext_api.models.pipeline import (
    PipelineCreateRequest,
    PipelineExecutionRequest,
    PipelineExecutionResponse,
    PipelineListResponse,
    PipelineResponse,
    PipelineStatsResponse,
    PipelineStatus,
    PipelineUpdateRequest,
)

# Plugin models - restored after confirming no syntax errors
from flext_api.models.plugin import (
    APIPluginUninstallRequest,
    APIPluginUpdateRequest,
    PluginConfigRequest,
    PluginDiscoveryResponse,
    PluginInstallationResponse,
    PluginInstallRequest,
    PluginListResponse,
    PluginResponse,
    PluginStatsResponse,
    PluginType,
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
    "APIPluginUninstallRequest",
    "APIPluginUpdateRequest",
    "HealthResponse",
    "LoginRequest",
    "LoginResponse",
    "MaintenanceRequest",
    "MaintenanceResponse",
    "PipelineCreateRequest",
    "PipelineExecutionRequest",
    "PipelineExecutionResponse",
    "PipelineListResponse",
    "PipelineResponse",
    "PipelineStatsResponse",
    "PipelineStatus",
    "PipelineUpdateRequest",
    "PluginConfigRequest",
    "PluginDiscoveryResponse",
    "PluginInstallRequest",
    "PluginInstallationResponse",
    "PluginListResponse",
    "PluginResponse",
    "PluginStatsResponse",
    "PluginType",
    "RegisterRequest",
    "RegisterResponse",
    "SystemBackupRequest",
    "SystemBackupResponse",
    "SystemConfigurationRequest",
    "SystemStatsResponse",
    "SystemStatusResponse",
    "UserAPI",
]
