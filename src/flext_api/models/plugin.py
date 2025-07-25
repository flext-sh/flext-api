"""Plugin API Models - Enterprise Plugin Management.

REFACTORED:
    Uses flext-core patterns with FlextResult and StrEnum.
Zero tolerance for duplication.
"""

from __future__ import annotations

import typing
from enum import StrEnum
from typing import Any

from pydantic import Field, field_validator

from flext_api.base import FlextAPIResponse
from flext_api.common.models import FlextValidatedRequest

if typing.TYPE_CHECKING:
    from datetime import datetime
    from uuid import UUID


class PluginSource(StrEnum):
    """Plugin source enumeration."""

    PIP = "pip"
    GITHUB = "github"
    LOCAL = "local"
    HUB = "hub"
    CUSTOM = "custom"


class PluginType(StrEnum):
    """Plugin type enumeration."""

    EXTRACTOR = "extractor"
    LOADER = "loader"
    TRANSFORM = "transform"
    UTILITY = "utility"
    CUSTOM = "custom"
    ORCHESTRATOR = "orchestrator"
    FILE = "file"
    DATABASE = "database"
    API = "api"


class PluginStatus(StrEnum):
    """Plugin status enumeration."""

    INSTALLED = "installed"
    AVAILABLE = "available"
    UPDATING = "updating"
    ERROR = "error"
    NOT_INSTALLED = "not_installed"
    DEPRECATED = "deprecated"


# --- Request Models ---


class PluginInstallRequest(FlextValidatedRequest):
    """Request model for plugin installation."""

    name: str = Field(min_length=1, max_length=100, description="Plugin name")
    plugin_type: PluginType = Field(description="Type of plugin")
    source: PluginSource = Field(default=PluginSource.PIP, description="Plugin source")
    version: str | None = Field(default=None, description="Specific version to install")
    variant: str | None = Field(default=None, description="Plugin variant")
    pip_url: str | None = Field(default=None, description="PIP package URL")
    github_url: str | None = Field(default=None, description="GitHub repository URL")
    local_path: str | None = Field(default=None, description="Local file path")
    config: dict[str, Any] = Field(default_factory=dict, description="Plugin configuration")
    force_reinstall: bool = Field(default=False, description="Force reinstall if already exists")
    install_extras: list[str] = Field(default_factory=list, description="Extra dependencies to install")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate plugin name."""
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Plugin name must contain only alphanumeric characters, hyphens and underscores")
        return v.lower()


class APIPluginUpdateRequest(FlextValidatedRequest):
    """Request model for plugin updates."""

    name: str = Field(min_length=1, max_length=100, description="Plugin name")
    version: str | None = Field(default=None, description="Target version")
    force_update: bool = Field(default=False, description="Force update even if same version")
    backup_current: bool = Field(default=True, description="Backup current version before update")
    config_updates: dict[str, Any] = Field(default_factory=dict, description="Configuration updates")


class APIPluginUninstallRequest(FlextValidatedRequest):
    """Request model for plugin uninstallation."""

    name: str = Field(min_length=1, max_length=100, description="Plugin name")
    remove_config: bool = Field(default=False, description="Remove plugin configuration")
    remove_data: bool = Field(default=False, description="Remove plugin data")
    force_remove: bool = Field(default=False, description="Force removal even if dependencies exist")


class PluginConfigRequest(FlextValidatedRequest):
    """Request model for plugin configuration updates."""

    name: str = Field(min_length=1, max_length=100, description="Plugin name")
    config: dict[str, Any] = Field(description="Plugin configuration")
    validate_config: bool = Field(default=True, description="Validate configuration before applying")
    restart_required: bool = Field(default=False, description="Whether restart is required after config change")


# --- Response Models ---


class PluginResponse(FlextAPIResponse[dict[str, Any]]):
    """Response model for individual plugin information."""

    name: str = Field(description="Plugin name")
    plugin_type: PluginType = Field(description="Plugin type")
    version: str = Field(description="Installed version")
    status: PluginStatus = Field(description="Plugin status")
    source: PluginSource = Field(description="Plugin source")
    description: str | None = Field(default=None, description="Plugin description")
    author: str | None = Field(default=None, description="Plugin author")
    homepage: str | None = Field(default=None, description="Plugin homepage")
    repository: str | None = Field(default=None, description="Plugin repository URL")
    license: str | None = Field(default=None, description="Plugin license")
    installed_at: datetime | None = Field(default=None, description="Installation timestamp")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp")
    config: dict[str, Any] = Field(default_factory=dict, description="Plugin configuration")
    dependencies: list[str] = Field(default_factory=list, description="Plugin dependencies")
    extras: list[str] = Field(default_factory=list, description="Available extras")
    is_active: bool = Field(default=True, description="Whether plugin is active")
    install_path: str | None = Field(default=None, description="Installation path")
    executable: str | None = Field(default=None, description="Plugin executable path")
    environment: dict[str, str] = Field(default_factory=dict, description="Environment variables")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PluginInstallationResponse(FlextAPIResponse[dict[str, Any]]):
    """Response model for plugin installation."""

    plugin_name: str = Field(description="Installed plugin name")
    plugin_type: PluginType = Field(description="Plugin type")
    installed_version: str = Field(description="Installed version")
    source: PluginSource = Field(description="Installation source")
    install_path: str | None = Field(default=None, description="Installation path")
    installation_time_seconds: float = Field(description="Time taken for installation")
    dependencies_installed: list[str] = Field(default_factory=list, description="Dependencies that were installed")
    config_applied: bool = Field(default=False, description="Whether configuration was applied")
    restart_required: bool = Field(default=False, description="Whether restart is required")
    warnings: list[str] = Field(default_factory=list, description="Installation warnings")
    post_install_notes: str | None = Field(default=None, description="Post-installation notes")


class PluginListResponse(FlextAPIResponse[list[dict[str, Any]]]):
    """Response model for plugin listing."""

    plugins: list[PluginResponse] = Field(description="List of plugins")
    total_count: int = Field(description="Total number of plugins")
    installed_count: int = Field(description="Number of installed plugins")
    available_count: int = Field(description="Number of available plugins")
    plugin_types: list[PluginType] = Field(description="Available plugin types")
    sources: list[PluginSource] = Field(description="Available plugin sources")
    last_updated: datetime | None = Field(default=None, description="Last registry update")


class PluginDiscoveryResponse(FlextAPIResponse[list[dict[str, Any]]]):
    """Response model for plugin discovery."""

    discovered_plugins: list[dict[str, Any]] = Field(description="Discovered plugins")
    discovery_sources: list[PluginSource] = Field(description="Sources that were searched")
    total_discovered: int = Field(description="Total number of discovered plugins")
    discovery_time_seconds: float = Field(description="Time taken for discovery")
    errors: list[str] = Field(default_factory=list, description="Discovery errors")
    cached_results: bool = Field(default=False, description="Whether results are from cache")


class PluginStatsResponse(FlextAPIResponse[dict[str, Any]]):
    """Response model for plugin statistics."""

    total_plugins: int = Field(description="Total number of plugins")
    installed_plugins: int = Field(description="Number of installed plugins")
    active_plugins: int = Field(description="Number of active plugins")
    plugin_types_count: dict[PluginType, int] = Field(description="Count by plugin type")
    sources_count: dict[PluginSource, int] = Field(description="Count by source")
    recent_installations: list[dict[str, Any]] = Field(description="Recent installations")
    disk_usage_mb: float = Field(description="Total disk usage in MB")
    memory_usage_mb: float | None = Field(default=None, description="Current memory usage in MB")
    last_activity: datetime | None = Field(default=None, description="Last plugin activity")
    health_status: str = Field(default="healthy", description="Overall plugin system health")


# Fix Pydantic model rebuild by providing explicit global namespace
def rebuild_plugin_models() -> None:
    """Rebuild all plugin models with proper type resolution."""
    # Module namespace already has UUID and datetime imported above
    # No need to modify module attributes at runtime
    # Rebuild models that use forward references
    PluginInstallRequest.model_rebuild()
    APIPluginUpdateRequest.model_rebuild()
    APIPluginUninstallRequest.model_rebuild()
    PluginConfigRequest.model_rebuild()
    PluginResponse.model_rebuild()
    PluginInstallationResponse.model_rebuild()
    PluginListResponse.model_rebuild()
    PluginDiscoveryResponse.model_rebuild()
    PluginStatsResponse.model_rebuild()


# Module-level flag to track rebuild status
_plugin_models_rebuilt = False


def ensure_plugin_models_rebuilt() -> None:
    """Ensure plugin models are rebuilt with proper type resolution."""
    global _plugin_models_rebuilt
    if _plugin_models_rebuilt:
        return
    # Temporarily disabled due to datetime import issues in TYPE_CHECKING block
    # Only rebuild in runtime, not during static analysis
    # if not typing.TYPE_CHECKING:
    #     try:
    #         rebuild_plugin_models()
    #         _plugin_models_rebuilt = True
    #     except ImportError:
    #         # If import issues remain, models work with limited type safety
    #         pass
    _plugin_models_rebuilt = True  # Mark as processed even if temporarily disabled


# Call the rebuild function when module is imported
# ensure_plugin_models_rebuilt()  # Temporarily disabled
