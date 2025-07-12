"""Pydantic models for the FLEXT API - Enterprise Management Models.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides Pydantic models for the FLEXT API, including authentication,
monitoring, pipeline, plugin, and system models.
"""

# Re-export shared models from flext_core
# Monitoring models
# Authentication models
from flext_api.models.auth import LoginRequest
from flext_api.models.auth import LoginResponse
from flext_api.models.auth import RegisterRequest
from flext_api.models.auth import RegisterResponse
from flext_api.models.auth import UserAPI
from flext_api.models.monitoring import HealthResponse
from flext_api.models.monitoring import SystemStatsResponse

# Pipeline models
from flext_api.models.pipeline import ExecutionResponse
from flext_api.models.pipeline import PipelineCreateRequest
from flext_api.models.pipeline import PipelineExecutionRequest
from flext_api.models.pipeline import PipelineExecutionResponse
from flext_api.models.pipeline import PipelineListResponse
from flext_api.models.pipeline import PipelineResponse
from flext_api.models.pipeline import PipelineStatsResponse
from flext_api.models.pipeline import PipelineUpdateRequest
from flext_api.models.pipeline import RunPipelineRequest

# Plugin models
from flext_api.models.plugin import PluginConfigRequest
from flext_api.models.plugin import PluginInstallationResponse
from flext_api.models.plugin import PluginInstallRequest
from flext_api.models.plugin import PluginListResponse
from flext_api.models.plugin import PluginResponse
from flext_api.models.plugin import PluginStatsResponse
from flext_api.models.plugin import PluginUninstallRequest
from flext_api.models.plugin import PluginUpdateRequest

# System models
from flext_api.models.system import MaintenanceRequest
from flext_api.models.system import MaintenanceResponse
from flext_api.models.system import SystemBackupRequest
from flext_api.models.system import SystemBackupResponse
from flext_api.models.system import SystemConfigurationRequest
from flext_api.models.system import SystemStatusResponse

# Re-export shared models from flext_core
from flext_core.domain.pydantic_base import APIResponse
from flext_core.domain.types import PluginType

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
