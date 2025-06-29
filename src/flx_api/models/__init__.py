"""Pydantic models for the FLX API - Enterprise Management Models."""

# Monitoring models
# Authentication models
from flx_api.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserAPI,
)
from flx_api.monitoring import HealthResponse, SystemStatsResponse

# Pipeline models
from flx_api.pipeline import (
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
from flx_api.plugin import (
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
from flx_api.system import (
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
