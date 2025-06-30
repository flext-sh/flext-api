"""Pydantic models for the FLEXT API - Enterprise Management Models."""

# Monitoring models
# Authentication models
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
    SystemHealthResponse,
    SystemStatusResponse,
)

__all__ = [
    # Legacy compatibility
    "ExecutionResponse",
    "HealthResponse",
    # Authentication models
    "LoginRequest",
    "LoginResponse",
    # System models
    "MaintenanceRequest",
    "MaintenanceResponse",
    # Modern pipeline models
    "PipelineCreateRequest",
    "PipelineExecutionRequest",
    "PipelineExecutionResponse",
    "PipelineListResponse",
    "PipelineResponse",
    "PipelineStatsResponse",
    "PipelineUpdateRequest",
    # Modern plugin models
    "PluginConfigRequest",
    "PluginInstallRequest",
    "PluginInstallationResponse",
    "PluginListResponse",
    "PluginResponse",
    "PluginStatsResponse",
    "PluginUninstallRequest",
    "PluginUpdateRequest",
    "RegisterRequest",
    "RegisterResponse",
    "RunPipelineRequest",
    "SystemBackupRequest",
    "SystemBackupResponse",
    "SystemConfigurationRequest",
    "SystemHealthResponse",
    "SystemStatsResponse",
    "SystemStatusResponse",
    "UserAPI",
]
