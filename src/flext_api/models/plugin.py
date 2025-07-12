"""Plugin API Models - Enterprise Plugin Management.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides Pydantic models for plugin management.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic import field_validator

from flext_core.domain.pydantic_base import APIRequest
from flext_core.domain.pydantic_base import APIResponse
from flext_core.domain.types import PluginType
from flext_core.domain.types import StrEnum


class PluginStatus(StrEnum):
    """Plugin status enumeration."""

    INSTALLED = "installed"
    NOT_INSTALLED = "not_installed"
    INSTALLING = "installing"
    UNINSTALLING = "uninstalling"
    ERROR = "error"
    UPDATING = "updating"


class PluginSource(StrEnum):
    """Plugin source enumeration."""

    HUB = "hub"
    PYPI = "pypi"
    GIT = "git"
    LOCAL = "local"
    CUSTOM = "custom"


# --- Request Models ---


class PluginInstallRequest(APIRequest):
    """Request model for plugin installation."""

    name: str = Field(
        min_length=1,
        max_length=255,
        description="The name of the plugin to install",
    )
    plugin_type: PluginType = Field(
        description="The type of the plugin",
    )
    variant: str | None = Field(
        default=None,
        max_length=255,
        description="The variant of the plugin to install",
    )
    version: str | None = Field(
        default=None,
        max_length=50,
        description="Specific version to install (defaults to latest)",
    )
    source: PluginSource = Field(
        default=PluginSource.HUB,
        description="Source to install plugin from",
    )
    pip_url: str | None = Field(
        default=None,
        description="Custom pip URL for installation",
    )
    configuration: dict[str, Any] = Field(
        default_factory=dict,
        description="Initial plugin configuration",
    )
    force_reinstall: bool = Field(
        default=False,
        description="Force reinstall if already installed",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional installation metadata",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate plugin name format.

        Args:
            v: Plugin name to validate.

        Returns:
            Validated plugin name.

        Raises:
            ValueError: If name format is invalid.

        """
        if not v.replace("-", "").replace("_", "").isalnum():
            msg = "Plugin name must contain only alphanumeric characters, hyphens, and underscores"
            raise ValueError(msg)
        return v.lower()


class PluginUninstallRequest(APIRequest):
    """Request model for plugin uninstallation."""

    force: bool = Field(
        default=False,
        description="Force uninstall even if plugin is in use",
    )
    cleanup_config: bool = Field(
        default=True,
        description="Remove plugin configuration after uninstall",
    )
    backup_config: bool = Field(
        default=True,
        description="Backup plugin configuration before removal",
    )


class PluginUpdateRequest(APIRequest):
    """Request model for plugin updates."""

    version: str | None = Field(
        default=None,
        max_length=50,
        description="Target version (defaults to latest)",
    )
    force_update: bool = Field(
        default=False,
        description="Force update even if same version",
    )
    preserve_config: bool = Field(
        default=True,
        description="Preserve existing configuration during update",
    )


class PluginConfigRequest(APIRequest):
    """Request model for plugin configuration updates."""

    configuration: dict[str, Any] = Field(
        description="Plugin configuration settings",
    )
    environment: str | None = Field(
        default=None,
        description="Target environment for configuration",
    )
    validate_config: bool = Field(
        default=True,
        description="Validate configuration before applying",
    )
    backup_current: bool = Field(
        default=True,
        description="Backup current configuration before update",
    )


class PluginDiscoveryRequest(APIRequest):
    """Request model for plugin discovery."""

    plugin_type: PluginType | None = Field(
        default=None,
        description="Filter by plugin type",
    )
    source: PluginSource | None = Field(
        default=None,
        description="Filter by plugin source",
    )
    search_term: str | None = Field(
        default=None,
        max_length=255,
        description="Search term for plugin name or description",
    )
    include_installed: bool = Field(
        default=True,
        description="Include already installed plugins",
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Page number",
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Page size",
    )


# --- Response Models ---


class PluginResponse(APIResponse):
    """Response model for plugin information."""

    plugin_id: UUID = Field(description="Unique plugin identifier")
    name: str = Field(description="Plugin name")
    plugin_type: PluginType = Field(description="Plugin type")
    variant: str | None = Field(default=None, description="Plugin variant")
    version: str | None = Field(default=None, description="Installed version")
    latest_version: str | None = Field(
        default=None,
        description="Latest available version",
    )
    description: str | None = Field(default=None, description="Plugin description")
    status: PluginStatus = Field(description="Plugin installation status")
    source: PluginSource = Field(description="Plugin source")
    pip_url: str | None = Field(default=None, description="Custom pip URL")
    configuration: dict[str, Any] = Field(
        default_factory=dict,
        description="Plugin configuration",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Plugin metadata",
    )
    installed_at: datetime | None = Field(
        default=None,
        description="Installation timestamp",
    )
    updated_at: datetime | None = Field(
        default=None,
        description="Last update timestamp",
    )
    installed_by: str | None = Field(
        default=None,
        description="User who installed the plugin",
    )
    installation_log: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Installation log entries",
    )
    dependencies: list[str] = Field(
        default_factory=list,
        description="Plugin dependencies",
    )
    supported_platforms: list[str] = Field(
        default_factory=list,
        description="Supported platforms",
    )
    documentation_url: str | None = Field(default=None, description="Documentation URL")
    repository_url: str | None = Field(default=None, description="Repository URL")
    license: str | None = Field(default=None, description="Plugin license")
    tags: list[str] = Field(
        default_factory=list,
        description="Plugin tags",
    )
    health_status: str = Field(
        default="unknown",
        description="Plugin health status",
    )
    last_health_check: datetime | None = Field(
        default=None,
        description="Last health check timestamp",
    )


class PluginInstallationResponse(APIResponse):
    """Response model for plugin installation operations."""

    operation_id: UUID = Field(description="Unique operation identifier")
    plugin_name: str = Field(description="Plugin name")
    status: str = Field(description="Installation status")
    started_at: datetime = Field(description="Installation start timestamp")
    finished_at: datetime | None = Field(description="Installation finish timestamp")
    duration_seconds: float | None = Field(description="Installation duration")
    success: bool = Field(description="Installation success status")
    error_message: str | None = Field(description="Error message if failed")
    logs: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Installation logs",
    )
    installed_version: str | None = Field(description="Version that was installed")
    dependencies_installed: list[str] = Field(
        default_factory=list,
        description="Dependencies that were installed",
    )


class PluginListResponse(APIResponse):
    """Response model for plugin list operations."""

    plugins: list[PluginResponse] = Field(description="List of plugins")
    total_count: int = Field(description="Total number of plugins")
    installed_count: int = Field(description="Number of installed plugins")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Page size")
    has_next: bool = Field(description="Whether there are more pages")
    has_previous: bool = Field(description="Whether there are previous pages")


class PluginDiscoveryResponse(APIResponse):
    """Response model for plugin discovery operations."""

    available_plugins: list[dict[str, Any]] = Field(description="Available plugins")
    total_available: int = Field(description="Total available plugins")
    installed_plugins: list[str] = Field(description="List of installed plugin names")
    recommended_plugins: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Recommended plugins based on current setup",
    )
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Page size")
    has_next: bool = Field(description="Whether there are more pages")
    has_previous: bool = Field(description="Whether there are previous pages")


class PluginHealthResponse(APIResponse):
    """Response model for plugin health information."""

    plugin_name: str = Field(description="Plugin name")
    health_status: str = Field(description="Overall health status")
    last_check: datetime = Field(description="Last health check timestamp")
    checks: list[dict[str, Any]] = Field(description="Individual health checks")
    performance_metrics: dict[str, Any] = Field(
        default_factory=dict,
        description="Performance metrics",
    )
    resource_usage: dict[str, Any] = Field(
        default_factory=dict,
        description="Resource usage statistics",
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Health recommendations",
    )


class PluginStatsResponse(APIResponse):
    """Response model for plugin statistics."""

    total_plugins: int = Field(description="Total number of plugins")
    installed_plugins: int = Field(description="Number of installed plugins")
    plugins_by_type: dict[str, int] = Field(description="Plugin count by type")
    plugins_by_status: dict[str, int] = Field(description="Plugin count by status")
    plugins_by_source: dict[str, int] = Field(description="Plugin count by source")
    recent_installations: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Recent plugin installations",
    )
    update_available_count: int = Field(
        description="Number of plugins with updates available",
    )
    health_summary: dict[str, int] = Field(description="Plugin health summary")


# --- Filter and Search Models ---


class PluginFilterRequest(APIRequest):
    """Request model for filtering plugins."""

    plugin_type: PluginType | None = Field(
        default=None,
        description="Filter by plugin type",
    )
    status: PluginStatus | None = Field(
        default=None,
        description="Filter by plugin status",
    )
    source: PluginSource | None = Field(
        default=None,
        description="Filter by plugin source",
    )
    has_updates: bool | None = Field(
        default=None,
        description="Filter by update availability",
    )
    health_status: str | None = Field(
        default=None,
        description="Filter by health status",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Filter by tags (AND operation)",
    )
    installed_after: datetime | None = Field(
        default=None,
        description="Filter by installation date (after)",
    )
    installed_before: datetime | None = Field(
        default=None,
        description="Filter by installation date (before)",
    )
    search: str | None = Field(
        default=None,
        description="Search in name and description",
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Page number",
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Page size",
    )
    sort_by: str = Field(
        default="name",
        description="Sort field",
    )
    sort_order: str = Field(
        default="asc",
        pattern="^(asc|desc)$",
        description="Sort order",
    )


# --- Legacy Models for Backward Compatibility ---


class LegacyPluginInstallRequest(APIRequest):
    """Legacy plugin installation request model."""

    name: str = Field(description="The name of the plugin to install")
    type: str = Field(description="The type of the plugin")
    variant: str | None = Field(description="The variant of the plugin to install")

    def to_modern_request(self) -> PluginInstallRequest:
        """Convert legacy request to modern format.

        Returns:
            Modern plugin install request.

        """
        plugin_type_mapping = {
            "extractor": PluginType.TAP,
            "tap": PluginType.TAP,
            "loader": PluginType.TARGET,
            "target": PluginType.TARGET,
            "transformer": PluginType.TRANSFORM,
            "transform": PluginType.TRANSFORM,
            "utility": PluginType.UTILITY,
        }

        return PluginInstallRequest(
            name=self.name,
            plugin_type=plugin_type_mapping.get(self.type, PluginType.UTILITY),
            variant=self.variant,
        )


class LegacyPluginResponse(APIResponse):
    """Legacy plugin response model."""

    name: str = Field(description="The name of the plugin")
    type: str = Field(description="The type of the plugin")
    variant: str | None = Field(description="The variant of the plugin")
    version: str | None = Field(description="The installed version of the plugin")
    description: str | None = Field(description="A brief description of the plugin")
    installed: bool = Field(description="Whether the plugin is currently installed")
    installed_at: datetime | None = Field(
        description="The timestamp when the plugin was installed",
    )

    @classmethod
    def from_modern_response(cls, response: PluginResponse) -> LegacyPluginResponse:
        """Convert modern response to legacy format.

        Args:
            response: Modern plugin response.

        Returns:
            Legacy plugin response.

        """
        return cls(
            name=response.name,
            type=response.plugin_type,
            variant=response.variant,
            version=response.version,
            description=response.description,
            installed=response.status == PluginStatus.INSTALLED,
            installed_at=response.installed_at,
        )
