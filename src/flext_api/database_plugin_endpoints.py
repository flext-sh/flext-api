"""FLEXT API Database Plugin Endpoints - Modern Python 3.13 + Clean Architecture.

Copyright (c) 2025 FLEXT Team. All rights reserved.

Database-backed plugin API endpoints with enterprise features:
- Plugin CRUD operations with persistence
- Plugin discovery and registry integration
- Installation status tracking and lifecycle management
- Configuration management with validation
- Version management and dependency resolution
- Health monitoring and status tracking
- Enterprise security and access control
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import NoReturn

from fastapi import Depends
from fastapi import HTTPException
from pydantic import Field

from flext_api.dependencies import get_db_session
from flext_api.repositories.plugin import DatabasePluginRepository
from flext_core.config import get_config
from flext_core.domain.pydantic_base import APIRequest
from flext_core.domain.pydantic_base import APIResponse

if TYPE_CHECKING:
    from fastapi import Request
    from sqlalchemy.ext.asyncio import AsyncSession

    from flext_api.models.plugin import PluginInstallationResponse
    from flext_api.models.plugin import PluginInstallRequest
    from flext_api.models.plugin import PluginListResponse
    from flext_api.models.plugin import PluginResponse
    from flext_api.models.plugin import PluginUpdateRequest


def _raise_bad_request_error(message: str) -> NoReturn:
    """Raise HTTP 400 Bad Request error."""
    raise HTTPException(status_code=400, detail=message)


def _raise_unauthorized_error(message: str) -> NoReturn:
    """Raise HTTP 401 Unauthorized error."""
    raise HTTPException(status_code=401, detail=message)


def _raise_not_found_error(message: str) -> NoReturn:
    """Raise HTTP 404 Not Found error."""
    raise HTTPException(status_code=404, detail=message)


def _raise_internal_error(message: str) -> NoReturn:
    """Raise HTTP 500 Internal Server error."""
    raise HTTPException(status_code=500, detail=message)


# Get configuration
config = get_config()


class PluginListParams(APIRequest):
    """Parameters for plugin listing operations."""

    page: int = Field(default=1, ge=1, description="Page number for pagination")
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page",
    )
    plugin_type: str | None = Field(
        default=None,
        description="Filter by plugin type",
    )
    status: str | None = Field(default=None, description="Filter by plugin status")
    search: str | None = Field(
        default=None,
        description="Search term for name/description",
    )


async def install_plugin_db(
    plugin_data: PluginInstallRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> PluginInstallationResponse:
    """Install a plugin using database backend.

    Args:
        plugin_data: Plugin installation request data
        request: FastAPI request object
        session: Database session

    Returns:
        PluginInstallationResponse: Installation result with status

    Raises:
        HTTPException: If authentication fails or installation errors occur

    """
    # Get authenticated user from request state
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    # Create repository and execute operation
    repo = DatabasePluginRepository(session)
    result = await repo.install_plugin(
        plugin_data=plugin_data,
        installed_by=user.get("username", "unknown"),
    )

    # Handle service result
    if result.is_success:
        return result.value
    error = result.error
    if error.error_type == "ValidationError":
        _raise_bad_request_error(error.message)
    elif error.error_type == "ConflictError":
        _raise_bad_request_error("Plugin already installed")
    elif error.error_type == "InternalError":
        _raise_internal_error(error.message)
    else:
        _raise_internal_error("Unknown error occurred")


async def get_plugin_db(
    plugin_id: str,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> PluginResponse:
    """Get a plugin by ID from database.

    Args:
        plugin_id: Plugin identifier string
        request: FastAPI request object
        session: Database session

    Returns:
        PluginResponse: Plugin data and metadata

    Raises:
        HTTPException: If authentication fails or plugin not found

    """
    # Get authenticated user from request state
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    # Create repository and execute operation
    repo = DatabasePluginRepository(session)
    result = await repo.get_plugin(plugin_id)

    # Handle service result
    if result.is_success:
        return result.value
    error = result.error
    if error.error_type == "NotFoundError":
        _raise_not_found_error("Plugin not found")
    elif error.error_type == "InternalError":
        _raise_internal_error(error.message)
    _raise_internal_error("Unknown error occurred")


async def update_plugin_db(
    plugin_id: str,
    plugin_data: PluginUpdateRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> PluginResponse:
    """Update a plugin configuration in database.

    Args:
        plugin_id: Plugin identifier string
        plugin_data: Plugin update request data
        request: FastAPI request object
        session: Database session

    Returns:
        PluginResponse: Updated plugin data

    Raises:
        HTTPException: If authentication fails or update errors occur

    """
    # Get authenticated user from request state
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    # Create repository and execute operation
    repo = DatabasePluginRepository(session)
    result = await repo.update_plugin(
        plugin_id=plugin_id,
        plugin_data=plugin_data,
        updated_by=user.get("username", "unknown"),
    )

    # Handle service result
    if result.is_success:
        return result.value
    error = result.error
    if error.error_type == "NotFoundError":
        _raise_not_found_error("Plugin not found")
    elif error.error_type == "ValidationError":
        _raise_bad_request_error(error.message)
    elif error.error_type == "InternalError":
        _raise_internal_error(error.message)
    _raise_internal_error("Unknown error occurred")


async def uninstall_plugin_db(
    plugin_id: str,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> APIResponse:
    """Uninstall a plugin from database.

    Args:
        plugin_id: Plugin identifier string
        request: FastAPI request object
        session: Database session

    Returns:
        APIResponse: Uninstallation success response

    Raises:
        HTTPException: If authentication fails or uninstallation errors occur

    """
    # Get authenticated user from request state
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    # Create repository and execute operation
    repo = DatabasePluginRepository(session)
    result = await repo.uninstall_plugin(plugin_id)

    # Handle service result
    if result.is_success:
        return APIResponse(success=True, message="Plugin uninstalled successfully")
    error = result.error
    if error.error_type == "NotFoundError":
        _raise_not_found_error("Plugin not found")
    elif error.error_type == "InternalError":
        _raise_internal_error(error.message)
    _raise_internal_error("Unknown error occurred")


async def list_plugins_db(
    request: Request,
    params: PluginListParams = PluginListParams(),
    session: AsyncSession = Depends(get_db_session),
) -> PluginListResponse:
    """List plugins with pagination and filtering.

    Args:
        request: FastAPI request object
        params: Pagination and filtering parameters
        session: Database session

    Returns:
        PluginListResponse: Paginated plugin list with metadata

    Raises:
        HTTPException: If authentication fails or listing errors occur

    """
    # Get authenticated user from request state
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    # Create repository and execute operation
    repo = DatabasePluginRepository(session)
    result = await repo.list_plugins(
        page=params.page,
        page_size=params.page_size,
        plugin_type_filter=params.plugin_type,
        status_filter=params.status,
        search_term=params.search,
    )

    # Handle service result
    if result.is_success:
        return result.value
    error = result.error
    if error.error_type == "InternalError":
        _raise_internal_error(error.message)
    _raise_internal_error("Unknown error occurred")


async def discover_plugins_db(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """Discover available plugins from registry.

    Args:
        request: FastAPI request object
        session: Database session

    Returns:
        dict[str, Any]: Available plugins discovery result

    Raises:
        HTTPException: If authentication fails or discovery errors occur

    """
    # Get authenticated user from request state
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    # Create repository and execute operation
    repo = DatabasePluginRepository(session)
    result = await repo.discover_plugins()

    # Handle service result
    if result.is_success:
        return {"discovered_plugins": result.value}
    error = result.error
    if error.error_type == "InternalError":
        _raise_internal_error(error.message)
    _raise_internal_error("Unknown error occurred")
