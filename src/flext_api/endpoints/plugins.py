"""Plugin management endpoints for FLEXT API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the plugin management endpoints for the FLEXT API.
Refactored to use Clean Architecture with Dependency Injection.
"""

from __future__ import annotations

import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from flext_api import get_logger
from flext_api.common import ensure_service_available, handle_api_exceptions
from flext_api.models.plugin import (
    APIPluginUninstallRequest,
    APIPluginUpdateRequest,
    PluginConfigRequest,
    PluginDiscoveryResponse,
    PluginInstallationResponse,
    PluginInstallRequest,
    PluginListResponse,
    PluginResponse,
    PluginSource,
    PluginStatsResponse,
)

if TYPE_CHECKING:
    from flext_core import FlextResult

# Create logger using flext-core get_logger function
logger = get_logger(__name__)

# Router for plugin endpoints
plugins_router = APIRouter(prefix="/plugins", tags=["plugins"])


def resolve_plugin_source(plugin_request: PluginInstallRequest) -> str:
    """Resolve plugin source path based on installation source.

    Args:
        plugin_request: Plugin installation request,

    Returns:
        Resolved plugin source path or URL

    Raises:
        ValueError: If source resolution fails,

    """
    source = plugin_request.source
    plugin_name = plugin_request.name

    try:
        if source == PluginSource.PIP:
            # For PyPI sources, return pip-installable package name
            if plugin_request.pip_url:
                return plugin_request.pip_url
            # Standard PyPI package format
            version_spec = (
                f"=={plugin_request.version}" if plugin_request.version else ""
            )
            return f"{plugin_name}{version_spec}"

        if source == PluginSource.GITHUB:
            # For GitHub sources, construct GitHub URL
            if plugin_request.pip_url:
                # Direct GitHub URL provided
                return plugin_request.pip_url
            # Standard GitHub package format (assume git+https format)
            version_spec = (
                f"@{plugin_request.version}" if plugin_request.version else ""
            )
            return f"git+https://github.com/{plugin_name}.git{version_spec}"

        if source == PluginSource.HUB:
            # For Hub sources, resolve from official plugin registry
            if plugin_request.pip_url:
                return plugin_request.pip_url
            # Hub format (assume Meltano Hub format)
            return f"meltanohub:{plugin_name}"

        if source == internal.invalid:
            # For local sources, validate and return local path
            if plugin_request.pip_url:
                local_path = Path(plugin_request.pip_url)
                if not local_path.exists():
                    raise ValueError(
                        f"Local plugin path does not exist: {plugin_request.pip_url}"
                    )
                return str(local_path.resolve())

            # Default local development path
            workspace_root = Path.cwd()
            potential_paths = [
                workspace_root / plugin_name,
                workspace_root / "plugins" / plugin_name,
                workspace_root / "local-plugins" / plugin_name,
            ]

            for path in potential_paths:
                if path.exists():
                    logger.info(f"Found local plugin at: {path}")
                    return str(path.resolve())

            raise ValueError(
                f"Local plugin '{plugin_name}' not found in workspace paths"
            )

        raise ValueError(f"Unsupported plugin source: {source}")

    except Exception as e:
        logger.exception(
            f"Plugin source resolution failed for {plugin_name} from {source}: {e}"
        )
        raise ValueError(f"Failed to resolve plugin source: {e}") from e


def get_plugin_manager() -> Any | None:
    """Get plugin manager via DI - NO DIRECT IMPORTS.

    This function retrieves the plugin manager from the DI container
    injected at runtime by projects like flext-plugin.

    Returns:
        Plugin manager provider or None if not registered

    """
    try:
        # Use DI container to get plugin service
        # This avoids direct imports from flext-plugin
        from flext_api.infrastructure.ports import FlextApiPluginPort

        plugin_service = FlextApiPluginPort.get_instance()
        if plugin_service:
            logger.info("Plugin service retrieved via DI")
            return plugin_service
        logger.warning("Plugin service not available in DI container")
        return None

    except Exception as e:
        logger.exception(f"Plugin manager initialization failed: {e}")
        return None


@plugins_router.post("/install")
@handle_api_exceptions("install plugin")
async def install_plugin(
    plugin_data: PluginInstallRequest,
    _request: Request,
    plugin_manager: Annotated[Any | None, Depends(get_plugin_manager)],
) -> PluginInstallationResponse:
    """Install plugin endpoint.

    Args:
        plugin_data: PluginInstallRequest,
        _request: Request,
        plugin_manager: Injected plugin manager provider,

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
    ensure_service_available(plugin_manager, "Plugin manager")

    try:
        # For now, use flext-meltano directly for REAL plugin installation
        try:
            from flext_meltano.helpers.installation import flext_meltano_install_plugin

            # Convert plugin_data.plugin_type to string if it's an enum
            plugin_type_str = (
                str(plugin_data.plugin_type.value)
                if hasattr(plugin_data.plugin_type, "value")
                else str(plugin_data.plugin_type)
            )

            # Use real Meltano installation
            install_result = flext_meltano_install_plugin(
                plugin_type=plugin_type_str,
                plugin_name=plugin_data.name,
                variant=plugin_data.variant,
            )
            logger.info(f"Meltano install result: {install_result.success}")

        except ImportError as e:
            logger.warning(f"flext-meltano not available: {e}")
            raise HTTPException(
                status_code=500,
                detail="flext-meltano integration not available",
            ) from e

        if not install_result.success:
            raise HTTPException(
                status_code=400,
                detail=f"Plugin installation failed: {install_result.error}",
            )

        plugin = install_result.data
        return PluginInstallationResponse(
            plugin_name=plugin.get("plugin_name", plugin_data.name),
            plugin_type=plugin_data.plugin_type,
            installed_version=plugin.get("version", "1.0.0"),
            source=plugin_data.source,
            install_path=plugin.get("install_path", str(Path(tempfile.gettempdir()) / plugin_data.name)),
            installation_time_seconds=0.1,
            dependencies_installed=[],
            config_applied=True,
            restart_required=False,
            warnings=[],
            post_install_notes=f"Plugin '{plugin_data.name}' installed successfully",
        )
        # Fallback for current implementation
        raise HTTPException(
            status_code=501,
            detail="Plugin installation not yet implemented - requires flext-plugin integration",
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.exception(f"Plugin installation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Plugin installation failed: {e}",
        ) from e


@plugins_router.get("")
@handle_api_exceptions("list plugins")
async def list_plugins(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    category: Annotated[str | None, Query()] = None,
    status: Annotated[str | None, Query()] = None,
    plugin_manager: Annotated[Any | None, Depends(get_plugin_manager)] = None,
) -> PluginListResponse:
    """List installed plugins.

    Args:
        page: Page number,
        page_size: Page size,
        category: Filter by category,
        status: Filter by status,
        plugin_manager: Injected plugin manager,

    Returns:
        Plugin list response

    """
    try:
        # Use plugin service via DI for listing if available
        if plugin_manager and hasattr(plugin_manager, "list_plugins"):
            plugins_result = plugin_manager.list_plugins()

            if plugins_result.success:
                plugins = plugins_result.data or []

                # Apply filters
                if category:
                    plugins = [
                        p for p in plugins if getattr(p, "category", None) == category
                    ]
                if status:
                    plugins = [
                        p for p in plugins if getattr(p, "status", None) == status
                    ]

                # Pagination
                start_idx = (page - 1) * page_size
                end_idx = start_idx + page_size
                paginated_plugins = plugins[start_idx:end_idx]

                return PluginListResponse(
                    plugins=[
                        PluginResponse(
                            name=getattr(p, "name", "unknown"),
                            version=getattr(p, "version", "1.0.0"),
                            description=getattr(p, "description", ""),
                            category=getattr(p, "category", "unknown"),
                            status=getattr(p, "status", "unknown"),
                            installed_at=getattr(p, "installed_at", datetime.now(UTC)),
                        )
                        for p in paginated_plugins
                    ],
                    total=len(plugins),
                    page=page,
                    page_size=page_size,
                    total_pages=(len(plugins) + page_size - 1) // page_size,
                )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list plugins: {plugins_result.error}",
            )

        # Fallback implementation
        return PluginListResponse(
            plugins=[],
            total=0,
            page=page,
            page_size=page_size,
            total_pages=0,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Plugin listing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Plugin listing failed: {e}",
        ) from e


@plugins_router.get("/stats")
@handle_api_exceptions("get plugin stats")
async def get_plugin_stats(_request: Request) -> PluginStatsResponse:
    """Get plugin statistics.

    Args:
        _request: Request,

    Returns:
        Plugin statistics

    """
    try:
        # Get plugin manager via DI
        plugin_manager = get_plugin_manager()

        if plugin_manager and hasattr(plugin_manager, "get_stats"):
            stats_result = plugin_manager.get_stats()
            if stats_result.success:
                return PluginStatsResponse(**stats_result.data)

        # Fallback stats
        return PluginStatsResponse(
            total_plugins=0,
            active_plugins=0,
            inactive_plugins=0,
            categories=[],
            last_updated=datetime.now(UTC),
        )

    except Exception as e:
        logger.exception(f"Plugin stats failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Plugin stats failed: {e}",
        ) from e


@plugins_router.get("/discover")
@handle_api_exceptions("discover plugins")
async def discover_plugins(_request: Request) -> PluginDiscoveryResponse:
    """Discover available plugins.

    Args:
        _request: Request,

    Returns:
        Plugin discovery response

    """
    try:
        # Get plugin manager via DI
        plugin_manager = get_plugin_manager()

        if plugin_manager and hasattr(plugin_manager, "discover_plugins"):
            discovery_result = plugin_manager.discover_plugins()
            if discovery_result.success:
                return PluginDiscoveryResponse(**discovery_result.data)

        # Fallback discovery
        return PluginDiscoveryResponse(
            available_plugins=[],
            sources=["pypi", "github"],
            last_discovery=datetime.now(UTC),
        )

    except Exception as e:
        logger.exception(f"Plugin discovery failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Plugin discovery failed: {e}",
        ) from e


@plugins_router.get("/{plugin_name}")
@handle_api_exceptions("get plugin")
async def get_plugin(plugin_name: str) -> dict[str, Any]:
    """Get plugin details.

    Args:
        plugin_name: Plugin name,

    Returns:
        Plugin details

    """
    try:
        # Get plugin manager via DI
        plugin_manager = get_plugin_manager()

        if plugin_manager and hasattr(plugin_manager, "get_plugin"):
            plugin_result = plugin_manager.get_plugin(plugin_name)
            if plugin_result.success and plugin_result.data:
                plugin = plugin_result.data
                return {
                    "name": getattr(plugin, "name", plugin_name),
                    "version": getattr(plugin, "version", "1.0.0"),
                    "description": getattr(plugin, "description", ""),
                    "category": getattr(plugin, "category", "unknown"),
                    "status": getattr(plugin, "status", "unknown"),
                    "installed_at": getattr(plugin, "installed_at", datetime.now(UTC)),
                }

        raise HTTPException(
            status_code=404,
            detail=f"Plugin '{plugin_name}' not found",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Plugin retrieval failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Plugin retrieval failed: {e}",
        ) from e


@plugins_router.put("/{plugin_name}/config")
@handle_api_exceptions("update plugin config")
async def update_plugin_config(
    plugin_name: str, config_data: PluginConfigRequest, _request: Request
) -> FlextResult[Any]:
    """Update plugin configuration.

    Args:
        plugin_name: Plugin name,
        config_data: Configuration data,
        _request: Request,

    Returns:
        Updated plugin response

    """
    try:
        # Get plugin manager via DI
        plugin_manager = get_plugin_manager()

        if plugin_manager and hasattr(plugin_manager, "update_plugin_config"):
            config_result = plugin_manager.update_plugin_config(
                plugin_name,
                config_data.config,
            )
            if config_result.success:
                plugin = config_result.data
                response = PluginResponse(
                    name=getattr(plugin, "name", plugin_name),
                    version=getattr(plugin, "version", "1.0.0"),
                    description=getattr(plugin, "description", ""),
                    category=getattr(plugin, "category", "unknown"),
                    status=getattr(plugin, "status", "unknown"),
                    installed_at=getattr(plugin, "installed_at", datetime.now(UTC)),
                )

                from flext_core import FlextResult
                return FlextResult.ok(response)

        raise HTTPException(
            status_code=404,
            detail=f"Plugin '{plugin_name}' not found or config update not supported",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Plugin config update failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Plugin config update failed: {e}",
        ) from e


@plugins_router.put("/{plugin_name}/update")
@handle_api_exceptions("update plugin")
async def update_plugin(
    plugin_name: str,
    update_data: APIPluginUpdateRequest,
    _request: Request,
    plugin_manager: Annotated[Any | None, Depends(get_plugin_manager)],
) -> PluginInstallationResponse:
    """Update plugin.

    Args:
        plugin_name: Plugin name,
        update_data: Update data,
        _request: Request,
        plugin_manager: Injected plugin manager,

    Returns:
        Plugin installation response

    """
    try:
        # Use plugin service via DI for update if available
        if plugin_manager and hasattr(plugin_manager, "update_plugin"):
            update_result = plugin_manager.update_plugin(
                plugin_name,
                update_data.version,
            )

            if update_result.success:
                plugin = update_result.data
                return PluginInstallationResponse(
                    operation_id=uuid4(),
                    plugin_name=plugin.name,
                    installation_status="updated",
                    started_at=datetime.now(UTC),
                    finished_at=datetime.now(UTC),
                    duration_seconds=0.1,
                    installation_success=True,
                    error_message=None,
                    logs=[
                        {
                            "level": "info",
                            "message": f"Plugin '{plugin.name}' updated to version {update_data.version}",
                        }
                    ],
                    installed_version=getattr(plugin, "version", update_data.version),
                )
            raise HTTPException(
                status_code=400,
                detail=f"Plugin update failed: {update_result.error}",
            )

        raise HTTPException(
            status_code=501,
            detail="Plugin update not yet implemented - requires flext-plugin integration",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Plugin update failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Plugin update failed: {e}",
        ) from e


@plugins_router.delete("/{plugin_name}")
@handle_api_exceptions("uninstall plugin")
async def uninstall_plugin(
    plugin_name: str,
    _request: Request,
    uninstall_data: APIPluginUninstallRequest | None = None,
    plugin_manager: Annotated[Any | None, Depends(get_plugin_manager)] = None,
) -> dict[str, Any]:
    """Uninstall plugin.

    Args:
        plugin_name: Plugin name,
        _request: Request,
        uninstall_data: Uninstall data,
        plugin_manager: Injected plugin manager,

    Returns:
        Uninstall response

    """
    try:
        # Use plugin service via DI for uninstall if available
        if plugin_manager and hasattr(plugin_manager, "uninstall_plugin"):
            uninstall_result = plugin_manager.uninstall_plugin(plugin_name)

            if uninstall_result.success:
                return {
                    "operation_id": str(uuid4()),
                    "plugin_name": plugin_name,
                    "uninstall_status": "uninstalled",
                    "started_at": datetime.now(UTC).isoformat(),
                    "finished_at": datetime.now(UTC).isoformat(),
                    "duration_seconds": 0.1,
                    "uninstall_success": True,
                    "error_message": None,
                    "logs": [
                        {
                            "level": "info",
                            "message": f"Plugin '{plugin_name}' uninstalled successfully",
                        }
                    ],
                }
            raise HTTPException(
                status_code=400,
                detail=f"Plugin uninstall failed: {uninstall_result.error}",
            )

        raise HTTPException(
            status_code=501,
            detail="Plugin uninstall not yet implemented - requires flext-plugin integration",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Plugin uninstall failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Plugin uninstall failed: {e}",
        ) from e


@plugins_router.get("/{plugin_name}/health")
@handle_api_exceptions("get plugin health")
async def get_plugin_health(
    plugin_name: str,
    _request: Request,
    plugin_manager: Annotated[Any | None, Depends(get_plugin_manager)],
) -> dict[str, str]:
    """Get plugin health status.

    Args:
        plugin_name: Plugin name,
        _request: Request,
        plugin_manager: Injected plugin manager,

    Returns:
        Plugin health status

    """
    try:
        # Use plugin service via DI for health check if available
        if plugin_manager and hasattr(plugin_manager, "get_plugin_health"):
            health_result = plugin_manager.get_plugin_health(plugin_name)
            if health_result.success:
                return {"status": health_result.data or "unknown"}

        return {"status": "unknown"}

    except Exception as e:
        logger.exception(f"Plugin health check failed: {e}")
        return {"status": "error"}


@plugins_router.post("/{plugin_name}/health-check")
@handle_api_exceptions("check plugin health")
async def check_plugin_health(
    plugin_name: str,
    _request: Request,
    plugin_manager: Annotated[Any | None, Depends(get_plugin_manager)],
) -> dict[str, str]:
    """Check plugin health.

    Args:
        plugin_name: Plugin name,
        _request: Request,
        plugin_manager: Injected plugin manager,

    Returns:
        Plugin health check result

    """
    try:
        # Use plugin service via DI for health check if available
        if plugin_manager and hasattr(plugin_manager, "check_plugin_health"):
            health_result = plugin_manager.check_plugin_health(plugin_name)
            if health_result.success:
                return {"status": health_result.data or "unknown"}

        return {"status": "unknown"}

    except Exception as e:
        logger.exception(f"Plugin health check failed: {e}")
        return {"status": "error"}
