"""Plugin application service using flext-core patterns.

This module provides the application service for plugin management,
implementing business logic using domain entities and clean architecture.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_api.domain.entities import Plugin
from flext_core.config.base import injectable
from flext_core.domain.types import ServiceResult

# Use centralized logger from flext-observability
from flext_observability.logging import get_logger

if TYPE_CHECKING:
    from uuid import UUID

    from flext_api.infrastructure.repositories import PluginRepository

logger = get_logger(__name__)


@injectable()
class PluginService:
    """Application service for plugin management.

    This service implements business logic for plugin operations,
    coordinating between domain entities and infrastructure.
    """

    def __init__(self, plugin_repo: PluginRepository) -> None:
        self.plugin_repo = plugin_repo

    async def install_plugin(
        self,
        name: str,
        type: str,
        version: str,
        description: str | None = None,
        config: dict | None = None,
        author: str | None = None,
        repository_url: str | None = None,
        documentation_url: str | None = None,
        capabilities: list[str] | None = None,
    ) -> ServiceResult[Plugin]:
        """Install a new plugin.

        Args:
            name: Plugin name.
            type: Plugin type.
            version: Plugin version.
            description: Optional plugin description.
            config: Optional plugin configuration.
            author: Optional plugin author.
            repository_url: Optional repository URL.
            documentation_url: Optional documentation URL.
            capabilities: Optional list of capabilities.

        Returns:
            ServiceResult containing installed plugin.

        """
        try:
            plugin = Plugin(
                name=name,
                type=type,
                version=version,
                description=description,
                config=config or {},
                enabled=True,
                author=author,
                repository_url=repository_url,
                documentation_url=documentation_url,
                capabilities=capabilities or [],
            )

            # Validate business rules
            if await self._is_duplicate_plugin(plugin.name, plugin.version):
                return ServiceResult.fail(
                    "Plugin with same name and version already exists",
                )

            # Save to repository
            saved_plugin = await self.plugin_repo.save(plugin)

            logger.info(
                "Plugin installed successfully",
                plugin_id=str(saved_plugin.id),
                name=saved_plugin.name,
                version=saved_plugin.version,
                type=saved_plugin.type,
            )

            return ServiceResult.ok(saved_plugin)

        except Exception as e:
            logger.exception("Failed to install plugin", error=str(e))
            return ServiceResult.fail(f"Failed to install plugin: {e}")

    async def get_plugin(self, plugin_id: UUID) -> ServiceResult[Plugin]:
        """Get plugin by ID.

        Args:
            plugin_id: Plugin unique identifier.

        Returns:
            ServiceResult containing requested plugin.

        """
        try:
            plugin = await self.plugin_repo.get_by_id(plugin_id)
            if not plugin:
                return ServiceResult.fail("Plugin not found")

            return ServiceResult.ok(plugin)

        except Exception as e:
            logger.exception(
                "Failed to get plugin",
                plugin_id=str(plugin_id),
                error=str(e),
            )
            return ServiceResult.fail(f"Failed to get plugin: {e}")

    async def list_plugins(
        self,
        type: str | None = None,
        enabled: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> ServiceResult[list[Plugin]]:
        """List plugins with optional filtering.

        Args:
            type: Optional plugin type filter.
            enabled: Optional enabled status filter.
            limit: Maximum number of results.
            offset: Results offset for pagination.

        Returns:
            ServiceResult containing list of plugins.

        """
        try:
            plugins = await self.plugin_repo.list_plugins(
                type=type,
                enabled=enabled,
                limit=limit,
                offset=offset,
            )

            return ServiceResult.ok(plugins)

        except Exception as e:
            logger.exception("Failed to list plugins", error=str(e))
            return ServiceResult.fail(f"Failed to list plugins: {e}")

    async def update_plugin(
        self,
        plugin_id: UUID,
        name: str | None = None,
        description: str | None = None,
        config: dict | None = None,
        enabled: bool | None = None,
        capabilities: list[str] | None = None,
    ) -> ServiceResult[Plugin]:
        """Update an existing plugin.

        Args:
            plugin_id: Plugin unique identifier.
            name: Optional new name.
            description: Optional new description.
            config: Optional new configuration.
            enabled: Optional new enabled status.
            capabilities: Optional new capabilities list.

        Returns:
            ServiceResult containing updated plugin.

        """
        try:
            # Get existing plugin
            existing_result = await self.get_plugin(plugin_id)
            if not existing_result.success:
                return existing_result

            plugin = existing_result.unwrap()

            # Apply updates
            if name is not None:
                plugin.name = name
            if description is not None:
                plugin.description = description
            if config is not None:
                plugin.config = config
            if enabled is not None:
                plugin.enabled = enabled
            if capabilities is not None:
                plugin.capabilities = capabilities

            # Save updates
            updated_plugin = await self.plugin_repo.save(plugin)

            logger.info(
                "Plugin updated successfully",
                plugin_id=str(plugin_id),
                name=updated_plugin.name,
                enabled=updated_plugin.enabled,
            )

            return ServiceResult.ok(updated_plugin)

        except Exception as e:
            logger.exception(
                "Failed to update plugin",
                plugin_id=str(plugin_id),
                error=str(e),
            )
            return ServiceResult.fail(f"Failed to update plugin: {e}")

    async def uninstall_plugin(self, plugin_id: UUID) -> ServiceResult[bool]:
        """Uninstall a plugin.

        Args:
            plugin_id: Plugin unique identifier.

        Returns:
            ServiceResult indicating uninstallation success.

        """
        try:
            # Check if plugin exists:
            existing_result = await self.get_plugin(plugin_id)
            if not existing_result.success:
                return ServiceResult.fail("Plugin not found")

            plugin = existing_result.unwrap()

            # Delete from repository
            await self.plugin_repo.delete(plugin_id)

            logger.info(
                "Plugin uninstalled successfully",
                plugin_id=str(plugin_id),
                name=plugin.name,
                version=plugin.version,
            )

            return ServiceResult.ok(True)

        except Exception as e:
            logger.exception(
                "Failed to uninstall plugin",
                plugin_id=str(plugin_id),
                error=str(e),
            )
            return ServiceResult.fail(f"Failed to uninstall plugin: {e}")

    async def enable_plugin(self, plugin_id: UUID) -> ServiceResult[Plugin]:
        """Enable a plugin.

        Args:
            plugin_id: Plugin unique identifier.

        Returns:
            ServiceResult containing enabled plugin.

        """
        return await self.update_plugin(plugin_id, enabled=True)

    async def disable_plugin(self, plugin_id: UUID) -> ServiceResult[Plugin]:
        """Disable a plugin.

        Args:
            plugin_id: Plugin unique identifier.

        Returns:
            ServiceResult containing disabled plugin.

        """
        return await self.update_plugin(plugin_id, enabled=False)

    async def _is_duplicate_plugin(self, name: str, version: str) -> bool:
        try:
            existing_plugins = await self.plugin_repo.list_plugins(limit=1000)

            return any(
                p.name == name and p.version == version for p in existing_plugins
            )

        except Exception:
            # If we can't check, assume no duplicate to avoid blocking installation
            return False
