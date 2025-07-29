"""Plugin application service using flext-core patterns.

This module provides the application service for plugin management
implementing business logic using domain entities and clean architecture.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core import FlextResult, get_logger

# Use centralized logger from flext-infrastructure.monitoring.flext-observability
from flext_api.application.services.base import PluginBaseService
from flext_api.domain.entities import Plugin, PluginType

if TYPE_CHECKING:
    from uuid import UUID

    from flext_api.domain.ports import PluginRepository

# Create logger using flext-core get_logger function
logger = get_logger(__name__)


class PluginService(PluginBaseService):
    """Application service for plugin management.

    This service implements business logic for plugin operations
    coordinating between domain entities and infrastructure.
    """

    def __init__(self, plugin_repo: PluginRepository) -> None:
        super().__init__(plugin_repo)
        # Use repository directly
        self.plugin_repo = self.repository

    async def install_plugin(
        self,
        name: str,
        version: str,
        plugin_type: PluginType,
        description: str | None = None,
        config: dict[str, Any] | None = None,
        capabilities: list[str] | None = None,
    ) -> FlextResult[Any]:
        """Install a new plugin.

        Args:
            name: Plugin name.,
            version: Plugin version.,
            plugin_type: Plugin type (extractor, loader, transformer).,
            description: Optional plugin description.,
            config: Optional plugin configuration.,
            capabilities: Optional plugin capabilities.,

        Returns:
            FlextResult containing installed plugin.

        """
        try:
            # Create plugin entity
            plugin = Plugin(
                name=name,
                plugin_version=version,
                plugin_type=plugin_type,
                description=description,
            )

            # Save to repository
            saved_result = await self.plugin_repo.create(plugin)
            if not saved_result.success:
                return saved_result

            saved_plugin = saved_result.data
            if saved_plugin is None:
                return FlextResult.fail("Plugin creation returned None")

            logger.info(
                "Plugin installed successfully",
                extra={
                    "plugin_id": str(saved_plugin.id),
                    "version": saved_plugin.plugin_version,
                    "type": saved_plugin.plugin_type,
                },
            )
            return FlextResult.ok(saved_plugin)

        except Exception as e:
            logger.exception("Operation failed")
            return FlextResult.fail(f"Failed to install plugin: {e}")

    async def get_plugin(self, plugin_id: UUID) -> FlextResult[Any]:
        """Get plugin by ID.

        Args:
            plugin_id: Plugin unique identifier.,

        Returns:
            FlextResult containing requested plugin.

        """
        try:
            plugin_result = await self.plugin_repo.get(str(plugin_id))
            if not plugin_result.success:
                return plugin_result

            plugin = plugin_result.data
            return FlextResult.ok(plugin)

        except Exception as e:
            logger.exception(
                "Failed to get plugin",
                extra={"plugin_id": str(plugin_id), "error": str(e)},
            )
            return FlextResult.fail(f"Failed to get plugin: {e}")

    async def list_plugins(
        self,
        plugin_type: str | None = None,
        *,
        enabled: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> FlextResult[Any]:
        """List plugins with optional filtering.

        Args:
            plugin_type: Optional plugin type filter.,
            enabled: Optional enabled status filter.,
            limit: Maximum number of results.,
            offset: Results offset for pagination.,

        Returns:
            FlextResult containing list of plugins.

        """
        try:
            plugins_result = await self.plugin_repo.list(
                plugin_type=plugin_type,
                status="active" if enabled else None,
                limit=limit,
                offset=offset,
            )

            if not plugins_result.success:
                return plugins_result

            plugins = plugins_result.data
            return FlextResult.ok(plugins)

        except Exception as e:
            logger.exception("Operation failed")
            return FlextResult.fail(f"Failed to list plugins: {e}")

    async def update_plugin(
        self,
        plugin_id: UUID,
        name: str | None = None,
        description: str | None = None,
        config: dict[str, Any] | None = None,
        *,
        enabled: bool | None = None,
        capabilities: list[str] | None = None,
    ) -> FlextResult[Any]:
        """Update an existing plugin.

        Args:
            plugin_id: Plugin unique identifier.,
            name: Optional new name.,
            description: Optional new description.,
            config: Optional new configuration.,
            enabled: Optional new enabled status.,
            capabilities: Optional new capabilities list.,

        Returns:
            FlextResult containing updated plugin.

        """
        try:
            # Get existing plugin
            existing_result = await self.get_plugin(plugin_id)
            if not existing_result.success:
                return existing_result

            plugin = existing_result.data
            if plugin is None:
                return FlextResult.fail("Plugin not found")

            # Apply updates (only fields that exist in Plugin entity)
            if name is not None:
                plugin.name = name
            if description is not None:
                plugin.description = description

            # Save updates
            updated_result = await self.plugin_repo.update(plugin)
            if not updated_result.success:
                return updated_result

            updated_plugin = updated_result.data
            if updated_plugin is None:
                return FlextResult.fail("Plugin update returned None")

            logger.info(
                "Plugin updated successfully",
                extra={
                    "plugin_id": str(plugin_id),
                    "enabled": updated_plugin.enabled,
                },
            )
            return FlextResult.ok(updated_plugin)

        except Exception as e:
            logger.exception(
                "Failed to update plugin",
                extra={"plugin_id": str(plugin_id), "error": str(e)},
            )
            return FlextResult.fail(f"Failed to update plugin: {e}")

    async def uninstall_plugin(self, plugin_id: UUID) -> FlextResult[Any]:
        """Uninstall a plugin.

        Args:
            plugin_id: Plugin unique identifier.,

        Returns:
            FlextResult indicating uninstallation success.

        """
        try:
            # Get existing plugin
            existing_result = await self.get_plugin(plugin_id)
            if not existing_result.success:
                return FlextResult.fail("Plugin not found")

            plugin = existing_result.data
            if plugin is None:
                return FlextResult.fail("Plugin not found")

            # Delete from repository
            delete_result = await self.plugin_repo.delete(str(plugin_id))
            if not delete_result.success:
                return FlextResult.fail(
                    delete_result.error or "Failed to delete plugin",
                )

            logger.info(
                f"Plugin uninstalled successfully - plugin_id: {plugin_id}, name: {plugin.name}",
            )
            return FlextResult.ok(
                {
                    "plugin_id": str(plugin_id),
                    "name": plugin.name,
                    "plugin_version": plugin.plugin_version,
                    "uninstalled": True,
                },
            )

        except Exception as e:
            logger.exception(
                "Failed to uninstall plugin",
                extra={"plugin_id": str(plugin_id), "error": str(e)},
            )
            return FlextResult.fail(f"Failed to uninstall plugin: {e}")
