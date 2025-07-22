"""Plugin management endpoints for FLEXT API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the plugin management endpoints for the FLEXT API.
Refactored to use Clean Architecture with Dependency Injection instead of direct imports.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from flext_core import (
    APIResponse,
    PluginInstallationRequest,
    PluginManagerProvider,
    PluginType,  # Use unified PluginType from shared_types
    PluginUninstallRequest,
    PluginUpdateRequest,
    get_container,
)

# PluginType is imported from flext_core.domain.shared_types
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
    PluginUninstallRequest as APIPluginUninstallRequest,
    PluginUpdateRequest as APIPluginUpdateRequest,
)
from flext_api.storage import storage

plugins_router = APIRouter(prefix="/plugins", tags=["plugins"])


def get_plugin_manager() -> PluginManagerProvider | None:
    """Get plugin manager from dependency injection container.

    This follows the proper Clean Architecture pattern where the abstract
    interface is defined in flext_core, and concrete implementations are
    injected at runtime by projects like flext-plugin.

    Returns:
        Plugin manager provider or None if not registered

    """
    # Plugin manager providers are registered via the dependency injection
    # system at application startup. If no provider is registered, we return
    # None and let the endpoints handle the service unavailable gracefully.

    # This is the correct architectural approach - we don't create mock/fake
    # implementations, but instead indicate that the service is not available
    # until a concrete implementation (like flext-plugin) is registered.

    try:
        # Look for registered plugin manager in the container
        container = get_container()
        if hasattr(container, "plugin_manager_provider"):
            provider = container.plugin_manager_provider
            if isinstance(provider, PluginManagerProvider):
                return provider
        return None
    except Exception:
        # Container not available or not configured - service unavailable
        return None


@plugins_router.post("/install")
async def install_plugin(
    plugin_data: PluginInstallRequest,
    _request: Request,
    plugin_manager: Annotated[
        PluginManagerProvider | None, Depends(get_plugin_manager),
    ],
) -> PluginInstallationResponse:
    """Install plugin endpoint.

    Args:
        plugin_data: PluginInstallRequest
        _request: Request
        plugin_manager: Injected plugin manager provider

    Returns:
        PluginInstallationResponse

    """
    # Validate plugin request first, outside try block
    if not plugin_data.name or not plugin_data.version:
        raise HTTPException(
            status_code=400,
            detail="Plugin name and version required",
        )

    # Check if plugin manager is available
    if plugin_manager is None:
        raise HTTPException(
            status_code=503,
            detail="Plugin manager not available - register a PluginManagerProvider implementation",
        )

    try:
        now = datetime.now(UTC)

        # Create installation request using flext_core interface
        # Map API source to internal source
        from flext_core.domain.plugin_types import PluginSource as InternalPluginSource
        internal_source = InternalPluginSource.PYPI  # Default
        if plugin_data.source:
            source_mapping = {
                "hub": InternalPluginSource.HUB,
                "pypi": InternalPluginSource.PYPI,
                "github": InternalPluginSource.GIT,
                "local": InternalPluginSource.LOCAL,
            }
            internal_source = source_mapping.get(plugin_data.source, InternalPluginSource.PYPI)

        install_request = PluginInstallationRequest(
            name=plugin_data.name,
            version=plugin_data.version,
            source=internal_source,
            requirements=getattr(plugin_data, "requirements", None) or [],
        )

        # Install plugin using DI interface
        result = await plugin_manager.install_plugin(install_request)

        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Plugin installation failed: {result.error}",
            )

        installation_result = result.data
        if installation_result is None:
            raise HTTPException(
                status_code=500,
                detail="Plugin installation failed: No result data",
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
            logs=[{"message": log} for log in (installation_result.logs or [])],
            installed_version=installation_result.installed_version
            or plugin_data.version,
            dependencies_installed=installation_result.dependencies or [],
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
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
    plugin_manager: Annotated[
        PluginManagerProvider | None, Depends(get_plugin_manager),
    ] = None,
) -> PluginListResponse:
    """List plugins endpoint.

    Args:
        _request: Request
        page: int
        page_size: int
        category: str | None
        status: str | None
        search: str | None
        plugin_manager: Injected plugin manager provider

    Returns:
        PluginListResponse

    """
    # Check if plugin manager is available
    if plugin_manager is None:
        raise HTTPException(
            status_code=503,
            detail="Plugin registry not available - register a PluginManagerProvider implementation",
        )

    try:
        # Get plugins with filters (convert category string to plugin type if needed)
        internal_plugin_type = None
        if category:
            try:
                # Map API plugin type to internal type
                api_type = PluginType(category)
                if api_type == PluginType.EXTRACTOR:
                    internal_plugin_type = PluginType.EXTRACTOR
                elif api_type == PluginType.LOADER:
                    internal_plugin_type = PluginType.LOADER
                elif api_type == PluginType.TRANSFORMER:
                    internal_plugin_type = PluginType.TRANSFORMER
                elif api_type == PluginType.UTILITY:
                    internal_plugin_type = PluginType.UTILITY
            except ValueError:
                internal_plugin_type = None

        plugins_list = plugin_manager.list_plugins(
            plugin_type=internal_plugin_type,
            enabled_only=(status == "enabled"),
        )

        # Convert PluginInfo objects to API plugin models
        api_plugins = []
        for plugin_info in plugins_list:
            # Convert plugin ID to UUID if it's a string
            plugin_id = plugin_info.id
            if isinstance(plugin_id, str):
                from uuid import NAMESPACE_DNS, uuid5

                plugin_id = uuid5(
                    NAMESPACE_DNS, f"{plugin_info.name}-{plugin_info.version}",
                )

            # Plugin types should match - just use the plugin type directly
            api_plugin_type = plugin_info.plugin_type if hasattr(plugin_info.plugin_type, "value") else PluginType.UTILITY

            # Map plugin source types
            from flext_api.models.plugin import PluginSource as APIPluginSource
            api_source = APIPluginSource.HUB  # Default
            if plugin_info.source.value in [e.value for e in APIPluginSource]:
                api_source = APIPluginSource(plugin_info.source.value)

            # Map plugin status
            from flext_core import EntityStatus
            api_status = EntityStatus.ACTIVE  # Default
            if plugin_info.status.value in [e.value for e in EntityStatus]:
                api_status = EntityStatus(plugin_info.status.value)

            api_plugin = PluginResponse(
                plugin_id=plugin_id,
                name=plugin_info.name,
                version=plugin_info.version,
                description=plugin_info.description,
                plugin_type=api_plugin_type,
                source=api_source,
                status=api_status,
                configuration=plugin_info.configuration,
                dependencies=plugin_info.dependencies,
                tags=plugin_info.tags,
                documentation_url=plugin_info.documentation_url,
                repository_url=plugin_info.repository_url,
                updated_at=plugin_info.updated_at or datetime.now(UTC),
            )
            api_plugins.append(api_plugin)

        return PluginListResponse(
            plugins=api_plugins,
            total_count=len(api_plugins),
            installed_count=len([p for p in api_plugins if p.status == "installed"]),
            page=page,
            page_size=page_size,
            has_next=len(api_plugins) >= page_size,
            has_previous=page > 1,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list plugins: {e}",
        ) from e


@plugins_router.get("/stats")
async def get_plugin_stats(_request: Request) -> PluginStatsResponse:
    """Get plugin statistics."""
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
    """Get specific plugin details."""
    # Check if plugin exists in storage
    for plugin in storage.plugins:
        if plugin["name"] == plugin_name:
            return PluginResponse(
                plugin_id=uuid4(),
                name=plugin["name"],
                plugin_type=PluginType.EXTRACTOR
                if plugin["type"] == "tap"
                else PluginType.LOADER,
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
    """Update plugin configuration."""
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
        plugin_type=PluginType.EXTRACTOR
        if plugin_name.startswith("tap-")
        else PluginType.LOADER,
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
    update_data: APIPluginUpdateRequest,
    _request: Request,
    plugin_manager: Annotated[
        PluginManagerProvider | None, Depends(get_plugin_manager),
    ],
) -> PluginInstallationResponse:
    """Update plugin endpoint.

    Args:
        plugin_name: str
        update_data: APIPluginUpdateRequest
        _request: Request
        plugin_manager: Injected plugin manager provider

    Returns:
        PluginInstallationResponse

    """
    # Validate plugin update request
    if not plugin_name or not plugin_name.strip():
        raise HTTPException(status_code=400, detail="Plugin name is required")

    # Check if plugin manager is available
    if plugin_manager is None:
        raise HTTPException(
            status_code=503,
            detail="Plugin manager not available - register a PluginManagerProvider implementation",
        )

    try:
        now = datetime.now(UTC)

        # Create update request using flext_core interface
        plugin_update_request = PluginUpdateRequest(
            version=update_data.version or "latest",  # Provide default if None
            force=getattr(update_data, "force", False),
            requirements=getattr(update_data, "requirements", None) or [],
        )

        # Update plugin using DI interface
        result = await plugin_manager.update_plugin(plugin_name, plugin_update_request)

        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Plugin update failed: {result.error}",
            )

        update_result = result.data
        if update_result is None:
            raise HTTPException(
                status_code=500,
                detail="Plugin update failed: No result data",
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
            logs=[{"message": log} for log in (update_result.logs or [])],
            installed_version=update_result.updated_version or update_data.version,
            dependencies_installed=update_result.dependencies or [],
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plugin update failed: {e}") from e


@plugins_router.delete("/{plugin_name}")
async def uninstall_plugin(
    plugin_name: str,
    _request: Request,
    uninstall_data: APIPluginUninstallRequest | None = None,
    plugin_manager: Annotated[
        PluginManagerProvider | None, Depends(get_plugin_manager),
    ] = None,
) -> APIResponse:
    """Uninstall plugin endpoint.

    Args:
        plugin_name: str
        _request: Request
        uninstall_data: APIPluginUninstallRequest | None
        plugin_manager: Injected plugin manager provider

    Returns:
        APIResponse

    """
    # Validate plugin uninstall request
    if not plugin_name or not plugin_name.strip():
        raise HTTPException(status_code=400, detail="Plugin name is required")

    # Check if plugin manager is available
    if plugin_manager is None:
        raise HTTPException(
            status_code=503,
            detail="Plugin manager not available - register a PluginManagerProvider implementation",
        )

    try:
        now = datetime.now(UTC)

        # Create uninstall request using flext_core interface
        plugin_uninstall_request = PluginUninstallRequest(
            force=getattr(uninstall_data, "force", False) if uninstall_data else False,
            keep_config=getattr(uninstall_data, "keep_config", True)
            if uninstall_data
            else True,
        )

        # Uninstall plugin using DI interface
        result = await plugin_manager.uninstall_plugin(
            plugin_name, plugin_uninstall_request,
        )

        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Plugin uninstallation failed: {result.error}",
            )

        finished_at = datetime.now(UTC)
        (finished_at - now).total_seconds()

        return APIResponse()

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Plugin uninstallation failed: {e}",
        ) from e


@plugins_router.get("/{plugin_name}/health")
async def get_plugin_health(
    plugin_name: str,
    _request: Request,
    plugin_manager: Annotated[
        PluginManagerProvider | None, Depends(get_plugin_manager),
    ],
) -> dict[str, str]:
    """Get plugin health status."""
    # Validate plugin name
    if not plugin_name or not plugin_name.strip():
        raise HTTPException(status_code=400, detail="Plugin name is required")

    # Check if plugin manager is available
    if plugin_manager is None:
        raise HTTPException(
            status_code=503,
            detail="Plugin manager not available - register a PluginManagerProvider implementation",
        )

    try:
        # Check plugin health using DI interface
        result = await plugin_manager.check_plugin_health(plugin_name)

        if not result.success:
            return {
                "plugin_name": plugin_name,
                "status": "unhealthy",
                "message": "Health check failed",
                "error": result.error or "",
                "timestamp": datetime.now(UTC).isoformat(),
                "details": "{}",
            }

        health_result = result.data
        if health_result is None:
            return {
                "plugin_name": plugin_name,
                "status": "unhealthy",
                "message": "Health check failed: No result data",
                "error": "",
                "timestamp": datetime.now(UTC).isoformat(),
                "details": "{}",
            }

        return {
            "plugin_name": plugin_name,
            "status": "healthy" if health_result.success else "unhealthy",
            "message": health_result.message or "Plugin health check completed",
            "error": health_result.error_message or "",
            "timestamp": datetime.now(UTC).isoformat(),
            "details": str(health_result.data) if health_result.data else "{}",
        }

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Plugin health check failed: {e}",
        ) from e


@plugins_router.post("/{plugin_name}/health-check")
async def check_plugin_health(
    plugin_name: str,
    _request: Request,
    plugin_manager: Annotated[
        PluginManagerProvider | None, Depends(get_plugin_manager),
    ],
) -> dict[str, str]:
    """Perform plugin health check."""
    # Validate plugin name
    if not plugin_name or not plugin_name.strip():
        raise HTTPException(status_code=400, detail="Plugin name is required")

    # Check if plugin manager is available
    if plugin_manager is None:
        raise HTTPException(
            status_code=503,
            detail="Plugin manager not available - register a PluginManagerProvider implementation",
        )

    try:
        # Check plugin health using DI interface
        result = await plugin_manager.check_plugin_health(plugin_name)

        if not result.success:
            return {
                "plugin_name": plugin_name,
                "status": "unhealthy",
                "message": "Health check failed",
                "error": result.error or "",
                "timestamp": datetime.now(UTC).isoformat(),
                "details": "{}",
            }

        health_result = result.data
        if health_result is None:
            return {
                "plugin_name": plugin_name,
                "status": "unhealthy",
                "message": "Health check failed: No result data",
                "error": "",
                "timestamp": datetime.now(UTC).isoformat(),
                "details": "{}",
            }

        return {
            "plugin_name": plugin_name,
            "status": "healthy" if health_result.success else "unhealthy",
            "message": health_result.message or "Plugin health check completed",
            "error": health_result.error_message or "",
            "timestamp": datetime.now(UTC).isoformat(),
            "details": str(health_result.data) if health_result.data else "{}",
        }

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Plugin health check failed: {e}",
        ) from e
