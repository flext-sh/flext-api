"""Plugin repository implementation using flext-core patterns.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the repository implementation for plugin persistence
using clean architecture and dependency injection patterns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.config.base import injectable
from flext_observability.logging import get_logger

if TYPE_CHECKING:
    from uuid import UUID

    from flext_api.domain.entities import Plugin

logger = get_logger(__name__)


@injectable()
class PluginRepository:
    """Repository for plugin persistence.

    This repository handles plugin data persistence using
    clean architecture patterns and dependency injection.
    """

    def __init__(self) -> None:
        self._storage: dict[UUID, Plugin] = {}

    async def save(self, plugin: Plugin) -> Plugin:
        """Save plugin to repository.

        Args:
            plugin: Plugin entity to save.

        Returns:
            Saved plugin entity.

        Raises:
            Exception: If save operation fails.

        """
        try:
            # In production, this would use actual database
            self._storage[plugin.id] = plugin

            logger.info(
                "Plugin saved successfully",
                plugin_id=str(plugin.id),
                name=plugin.name,
            )

            return plugin

        except Exception as e:
            logger.exception(
                "Failed to save plugin",
                plugin_id=str(plugin.id),
                error=str(e),
            )
            raise

    async def get_by_id(self, plugin_id: UUID) -> Plugin | None:
        """Get plugin by ID.

        Args:
            plugin_id: Unique identifier of the plugin.

        Returns:
            Plugin entity if found, None otherwise.

        Raises:
            Exception: If retrieval operation fails.

        """
        try:
            plugin = self._storage.get(plugin_id)

            if plugin:
                logger.debug("Plugin retrieved", plugin_id=str(plugin_id))
            else:
                logger.warning("Plugin not found", plugin_id=str(plugin_id))

            return plugin

        except Exception as e:
            logger.exception(
                "Failed to get plugin",
                plugin_id=str(plugin_id),
                error=str(e),
            )
            raise

    async def list_plugins(
        self,
        type: str | None = None,
        enabled: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Plugin]:
        """List plugins with optional filters and pagination.

        Args:
            type: Filter by plugin type.
            enabled: Filter by enabled status.
            limit: Maximum number of plugins to return.
            offset: Number of plugins to skip.

        Returns:
            List of plugin entities matching the criteria.

        Raises:
            Exception: If list operation fails.

        """
        try:
            plugins = list(self._storage.values())

            # Apply filters
            if type:
                plugins = [p for p in plugins if p.type == type]

            if enabled is not None:
                plugins = [p for p in plugins if p.enabled == enabled]

            # Apply pagination
            total_count = len(plugins)
            plugins = plugins[offset : offset + limit]

            logger.debug(
                "Plugins listed",
                count=len(plugins),
                total=total_count,
                type=type,
                enabled=enabled,
            )

            return plugins

        except Exception as e:
            logger.exception("Failed to list plugins", error=str(e))
            raise

    async def delete(self, plugin_id: UUID) -> bool:
        """Delete plugin by ID.

        Args:
            plugin_id: Unique identifier of the plugin to delete.

        Returns:
            True if plugin was deleted, False if not found.

        Raises:
            Exception: If delete operation fails.

        """
        try:
            if plugin_id in self._storage:
                del self._storage[plugin_id]
                logger.info("Plugin deleted", plugin_id=str(plugin_id))
                return True

            logger.warning("Plugin not found for deletion", plugin_id=str(plugin_id))
            return False

        except Exception as e:
            logger.exception(
                "Failed to delete plugin",
                plugin_id=str(plugin_id),
                error=str(e),
            )
            raise

    async def get_by_name_and_version(self, name: str, version: str) -> Plugin | None:
        """Get plugin by name and version.

        Args:
            name: Name of the plugin.
            version: Version of the plugin.

        Returns:
            Plugin entity if found, None otherwise.

        Raises:
            Exception: If retrieval operation fails.

        """
        try:
            for plugin in self._storage.values():
                if plugin.name == name and plugin.version == version:
                    return plugin

            return None

        except Exception as e:
            logger.exception(
                "Failed to get plugin by name and version",
                name=name,
                version=version,
                error=str(e),
            )
            raise

    async def count_plugins(
        self,
        plugin_type: str | None = None,
        *,
        enabled: bool | None = None,
    ) -> int:
        """Count plugins with optional filters.

        Args:
            type: Filter by plugin type.
            enabled: Filter by enabled status.

        Returns:
            Number of plugins matching the criteria.

        Raises:
            Exception: If count operation fails.

        """
        try:
            plugins = await self.list_plugins(
                type=type,
                enabled=enabled,
                limit=1000000,  # Large limit to get all
                offset=0,
            )

            return len(plugins)

        except Exception as e:
            logger.exception("Failed to count plugins", error=str(e))
            raise
