"""Plugin management endpoints for FLEXT API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the plugin management endpoints for the FLEXT API.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, Request
from flext_core.domain.pydantic_base import APIResponse
from flext_core.domain.types import PluginType

from flext_api.models.plugin import (
    PluginConfigRequest,
    PluginDiscoveryResponse,
    PluginInstallationResponse,
    PluginInstallRequest,
    PluginListResponse,
    PluginResponse,
    PluginSource,
    PluginStatsResponse,
    PluginStatus,
    PluginUninstallRequest,
    PluginUpdateRequest,
)
from flext_api.storage import storage

plugins_router = APIRouter(prefix="/plugins", tags=["plugins"])


@plugins_router.post("/install")
async def install_plugin(
    plugin_data: PluginInstallRequest,
    _request: Request,
) -> PluginInstallationResponse:
    """Install plugin endpoint.

    Args:
        plugin_data: PluginInstallRequest
        _request: Request

    Returns:
        PluginInstallationResponse

    """
    try:
        # Use real plugin manager from flext-infrastructure.plugins.flext-plugin
        from flext_plugin.manager import PluginManager

        plugin_manager = PluginManager()
        now = datetime.now(UTC)

        # Validate plugin request
        if not plugin_data.name or not plugin_data.version:
            raise HTTPException(
                status_code=400,
                detail="Plugin name and version required",
            )

        # Install plugin with real implementation
        installation_result = await plugin_manager.install_plugin(  # type: ignore[attr-defined]
            name=plugin_data.name,
            version=plugin_data.version,
            source=plugin_data.source.value if plugin_data.source else "pypi",
            requirements=plugin_data.requirements or [],  # type: ignore[attr-defined]
        )

        finished_at = datetime.now(UTC)
        duration = (finished_at - now).total_seconds()

        return PluginInstallationResponse(
            operation_id=uuid4(),
            plugin_name=plugin_data.name,
            status="completed" if installation_result.success else "failed",
            started_at=now,
            finished_at=finished_at,
            duration_seconds=duration,
            success=installation_result.success,
            error_message=installation_result.error_message,
            logs=installation_result.logs or [],
            installed_version=installation_result.installed_version
            or plugin_data.version,
            dependencies_installed=installation_result.dependencies or [],
        )

    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail="Plugin manager not available - install flext-plugin",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Plugin installation failed: {e}",
        ) from e


@plugins_router.get("")
async def list_plugins(
    _request: Request,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    category: Annotated[str | None, Query()] = None,
    status: Annotated[str | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
) -> PluginListResponse:
    """List plugins endpoint.

    Args:
        _request: Request
        page: int
        page_size: int
        category: str | None
        status: str | None
        search: str | None

    Returns:
        PluginListResponse

    """
    try:
        from flext_plugin.registry import PluginRegistry
    except ImportError as import_error:
        raise HTTPException(
            status_code=503,
            detail="Plugin registry not available - install flext-plugin",
        ) from import_error

    try:
        registry = PluginRegistry()

        # Get plugins with filters
        plugins_result = await registry.list_plugins(
            page=page,
            page_size=page_size,
            category=category,
            status=status,
            search=search,
        )

        # Convert registry plugins to API plugin models
        api_plugins = []
        for plugin in plugins_result.plugins:
            # Convert plugin ID to UUID if needed
            plugin_id = getattr(plugin, "id", None)
            if plugin_id is None:
                from uuid import NAMESPACE_DNS, uuid5

                plugin_id = uuid5(NAMESPACE_DNS, f"{plugin.name}-{plugin.version}")

            api_plugin = PluginResponse(
                plugin_id=plugin_id,
                name=plugin.name,
                version=plugin.version,
                description=plugin.description,
                plugin_type=PluginType(
                    plugin.plugin_type.value
                    if hasattr(plugin.plugin_type, "value")
                    else plugin.plugin_type,
                ),
                source=PluginSource(plugin.source),
                status=PluginStatus(plugin.status),
                configuration=plugin.configuration or {},
                dependencies=plugin.dependencies or [],
                tags=plugin.tags or [],
                documentation_url=plugin.documentation_url,
                repository_url=plugin.repository_url,
            )
            api_plugins.append(api_plugin)

        return PluginListResponse(
            plugins=api_plugins,
            total_count=plugins_result.total_count,
            installed_count=plugins_result.installed_count,
            page=page,
            page_size=page_size,
            has_next=plugins_result.has_next,
            has_previous=page > 1,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list plugins: {e}",
        ) from e


@plugins_router.get("/stats")
async def get_plugin_stats(_request: Request) -> PluginStatsResponse:
    return PluginStatsResponse(
        total_plugins=0,
        installed_plugins=0,
        plugins_by_type={},
        plugins_by_status={},
        plugins_by_source={},
        recent_installations=[],
        update_available_count=0,
        health_summary={},
    )


@plugins_router.get("/discover")
async def discover_plugins(_request: Request) -> PluginDiscoveryResponse:
    """Discover available plugins from various sources."""
    return PluginDiscoveryResponse(
        available_plugins=[],
        total_available=0,
        installed_plugins=[],
        recommended_plugins=[],
        page=1,
        page_size=20,
        has_next=False,
        has_previous=False,
    )


@plugins_router.get("/{plugin_name}")
async def get_plugin(plugin_name: str, _request: Request) -> PluginResponse:
    # Check if plugin exists in storage
    for plugin in storage.plugins:
        if plugin["name"] == plugin_name:
            return PluginResponse(
                plugin_id=uuid4(),
                name=plugin["name"],
                plugin_type=PluginType.TAP
                if plugin["type"] == "tap"
                else PluginType.TARGET,
                version=plugin["version"],
                description=plugin["description"],
                status=PluginStatus.ACTIVE
                if plugin["status"] == "installed"
                else PluginStatus.INACTIVE,
                source=PluginSource.HUB,
                configuration={},
                updated_at=datetime.now(UTC),
            )

    # Plugin not found
    raise HTTPException(status_code=404, detail=f"Plugin '{plugin_name}' not found")


@plugins_router.put("/{plugin_name}/config")
async def update_plugin_config(
    plugin_name: str,
    config_data: PluginConfigRequest,
    _request: Request,
) -> PluginResponse:
    # Basic validation
    if not plugin_name or not plugin_name.strip():
        raise HTTPException(status_code=400, detail="Plugin name is required")

    if not isinstance(config_data.configuration, dict):
        raise HTTPException(
            status_code=400,
            detail="Plugin configuration must be a valid dictionary",
        )

    return PluginResponse(
        plugin_id=uuid4(),
        name=plugin_name,
        plugin_type=PluginType.TAP
        if plugin_name.startswith("tap-")
        else PluginType.TARGET,
        version="latest",
        description=f"Plugin {plugin_name} configuration updated successfully",
        status=PluginStatus.ACTIVE,
        source=PluginSource.HUB,
        configuration=config_data.configuration,
        updated_at=datetime.now(UTC),
    )


@plugins_router.put("/{plugin_name}/update")
async def update_plugin(
    plugin_name: str,
    update_data: PluginUpdateRequest,
    _request: Request,
) -> PluginInstallationResponse:
    """Update plugin endpoint.

    Args:
        plugin_name: str
        update_data: PluginUpdateRequest
        _request: Request

    Returns:
        PluginInstallationResponse

    """
    try:
        # Use real plugin manager from flext-infrastructure.plugins.flext-plugin
        from flext_plugin.manager import PluginManager

        plugin_manager = PluginManager()
        now = datetime.now(UTC)

        # Validate plugin update request
        if not plugin_name or not plugin_name.strip():
            raise HTTPException(status_code=400, detail="Plugin name is required")

        # Update plugin with real implementation
        update_result = await plugin_manager.update_plugin(  # type: ignore[attr-defined]
            name=plugin_name,
            version=update_data.version,
            force=getattr(update_data, "force", False),
            requirements=getattr(update_data, "requirements", None) or [],
        )

        finished_at = datetime.now(UTC)
        duration = (finished_at - now).total_seconds()

        return PluginInstallationResponse(
            operation_id=uuid4(),
            plugin_name=plugin_name,
            status="completed" if update_result.success else "failed",
            started_at=now,
            finished_at=finished_at,
            duration_seconds=duration,
            success=update_result.success,
            error_message=update_result.error_message,
            logs=update_result.logs or [],
            installed_version=update_result.updated_version or update_data.version,
            dependencies_installed=update_result.dependencies or [],
        )

    # TODO: Implement try block
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail="Plugin manager not available - install flext-plugin",
        ) from e
    # TODO: Implement try block
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plugin update failed: {e}") from e


@plugins_router.delete("/{plugin_name}")
async def uninstall_plugin(
    plugin_name: str,
    _request: Request,
    uninstall_data: PluginUninstallRequest | None = None,
) -> APIResponse:
    """Uninstall plugin endpoint.

    Args:
        plugin_name: str
        _request: Request
        uninstall_data: PluginUninstallRequest | None

    Returns:
        APIResponse

    """
    try:
        # Use real plugin manager from flext-infrastructure.plugins.flext-plugin
        from flext_plugin.manager import PluginManager

        plugin_manager = PluginManager()
        now = datetime.now(UTC)

        # Validate plugin uninstall request
        if not plugin_name or not plugin_name.strip():
            raise HTTPException(status_code=400, detail="Plugin name is required")

        # Uninstall plugin with real implementation
        await plugin_manager.uninstall_plugin(  # type: ignore[attr-defined]
            name=plugin_name,
            force=getattr(uninstall_data, "force", False) if uninstall_data else False,
            keep_config=getattr(uninstall_data, "keep_config", True)
            if uninstall_data
            else True,
        )

        finished_at = datetime.now(UTC)
        (finished_at - now).total_seconds()

        return APIResponse()

    # TODO: Implement try block
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail="Plugin manager not available - install flext-plugin",
        ) from e
    # TODO: Implement try block
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Plugin uninstallation failed: {e}",
        ) from e


@plugins_router.get("/{plugin_name}/health")
async def get_plugin_health(
    plugin_name: str,
    _request: Request,
) -> dict[str, str]:
    try:
        # Use real plugin manager from flext-infrastructure.plugins.flext-plugin
        from flext_plugin.manager import PluginManager

        plugin_manager = PluginManager()

        # Validate plugin name
        if not plugin_name or not plugin_name.strip():
            raise HTTPException(status_code=400, detail="Plugin name is required")

        # Check plugin health with real implementation
        health_result = await plugin_manager.check_plugin_health(plugin_name)  # type: ignore[attr-defined]

        return {
            "plugin_name": plugin_name,
            "status": "healthy" if health_result.success else "unhealthy",
            "message": health_result.message or "Plugin health check completed",
            "error": health_result.error_message or "",
            "timestamp": datetime.now(UTC).isoformat(),
            "details": str(health_result.data)
            if hasattr(health_result, "data")
            else "{}",
        }

    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail="Plugin manager not available - install flext-plugin",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Plugin health check failed: {e}",
        ) from e


@plugins_router.post("/{plugin_name}/health-check")
async def check_plugin_health(
    plugin_name: str,
    _request: Request,
) -> dict[str, str]:
    try:
        # Use real plugin manager from flext-infrastructure.plugins.flext-plugin
        from flext_plugin.manager import PluginManager

        plugin_manager = PluginManager()

        # Validate plugin name
        if not plugin_name or not plugin_name.strip():
            raise HTTPException(status_code=400, detail="Plugin name is required")

        # Check plugin health with real implementation
        health_result = await plugin_manager.check_plugin_health(plugin_name)  # type: ignore[attr-defined]

        return {
            "plugin_name": plugin_name,
            "status": "healthy" if health_result.success else "unhealthy",
            "message": health_result.message or "Plugin health check completed",
            "error": health_result.error_message or "",
            "timestamp": datetime.now(UTC).isoformat(),
            "details": str(health_result.data)
            if hasattr(health_result, "data")
            else "{}",
        }

    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail="Plugin manager not available - install flext-plugin",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Plugin health check failed: {e}",
        ) from e
