"""Plugin repository implementation using flext-core patterns.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the repository implementation for plugin persistence
using clean architecture and dependency injection patterns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

# Import runtime dependencies
from uuid import UUID  # noqa: TC003

from flext_core.domain.types import ServiceResult
from flext_observability.logging import get_logger

from flext_api.domain.ports import PluginRepository

if TYPE_CHECKING:
    from flext_api.domain.entities import Plugin

logger = get_logger(__name__)


class InMemoryPluginRepository(PluginRepository):
    """Repository for plugin persistence.

    This repository handles plugin data persistence using
    clean architecture patterns and dependency injection.
    """

    def __init__(self) -> None:
        """Initialize plugin repository."""
        self._storage: dict[UUID, Plugin] = {}

    async def create(self, plugin: Plugin) -> ServiceResult[Plugin]:
        """Create a new plugin."""
        try:
            if plugin.id in self._storage:
                return ServiceResult.fail(f"Plugin {plugin.id} already exists")

            self._storage[plugin.id] = plugin
            logger.info("Plugin created successfully: %s", plugin.name)
            return ServiceResult.ok(plugin)
        except Exception as e:
            logger.exception("Failed to create plugin: %s", plugin.name)
            return ServiceResult.fail(f"Failed to create plugin: {e}")

    async def get(self, plugin_id: UUID) -> ServiceResult[Plugin]:
        """Get plugin by ID.

        Args:
            plugin_id: Plugin unique identifier.

        Returns:
            Plugin entity if found, None otherwise.

        """
        try:
            plugin = self._storage.get(plugin_id)
            if plugin:
                logger.debug("Plugin found: %s", plugin.name)
                return ServiceResult.ok(plugin)
            logger.debug("Plugin not found: %s", plugin_id)
            return ServiceResult.fail(f"Plugin {plugin_id} not found")
        except Exception as e:
            logger.exception("Failed to get plugin: %s", plugin_id)
            return ServiceResult.fail(f"Failed to get plugin: {e}")

    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
        plugin_type: str | None = None,
        status: str | None = None,
    ) -> ServiceResult[list[Plugin]]:
        """List plugins with filtering and pagination.

        Args:
            limit: Maximum number of plugins to return.
            offset: Number of plugins to skip.
            plugin_type: Filter by plugin type.
            enabled: Filter by enabled status.

        Returns:
            List of plugin entities.

        """
        try:
            all_plugins = list(self._storage.values())

            # Apply filters
            if plugin_type:
                all_plugins = [
                    p
                    for p in all_plugins
                    if getattr(p, "plugin_type", None) == plugin_type
                ]

            if status:
                all_plugins = [
                    p for p in all_plugins if getattr(p, "status", "active") == status
                ]

            # Apply pagination
            paginated = all_plugins[offset : offset + limit]

            logger.debug(
                "Listed %d plugins (limit=%d, offset=%d)",
                len(paginated),
                limit,
                offset,
            )
            return ServiceResult.ok(paginated)

        except Exception as e:
            logger.exception("Failed to list plugins")
            return ServiceResult.fail(f"Failed to list plugins: {e}")

    async def update(self, plugin: Plugin) -> ServiceResult[Plugin]:
        """Update existing plugin."""
        try:
            if plugin.id not in self._storage:
                return ServiceResult.fail(f"Plugin {plugin.id} not found")

            self._storage[plugin.id] = plugin
            logger.info("Plugin updated successfully: %s", plugin.name)
            return ServiceResult.ok(plugin)
        except Exception as e:
            logger.exception("Failed to update plugin: %s", plugin.name)
            return ServiceResult.fail(f"Failed to update plugin: {e}")

    async def delete(self, plugin_id: UUID) -> ServiceResult[bool]:
        """Delete plugin by ID.

        Args:
            plugin_id: Plugin unique identifier.

        Returns:
            True if plugin was deleted, False if not found.

        """
        try:
            if plugin_id in self._storage:
                plugin = self._storage.pop(plugin_id)
                logger.info("Plugin deleted successfully: %s", plugin.name)
                return True
            logger.warning("Plugin not found for deletion: %s", plugin_id)
            return False
        except Exception:
            logger.exception("Failed to delete plugin: %s", plugin_id)
            return False

    async def exists(self, plugin_id: UUID) -> bool:
        """Check if plugin exists.

        Args:
            plugin_id: Plugin unique identifier.

        Returns:
            True if plugin exists, False otherwise.

        """
        try:
            exists = plugin_id in self._storage
            logger.debug("Plugin exists check: %s = %s", plugin_id, exists)
            return exists
        except Exception:
            logger.exception("Failed to check plugin existence: %s", plugin_id)
            return False

    async def count(self) -> int:
        """Get total count of plugins.

        Returns:
            Total number of plugins in repository.

        """
        try:
            count = len(self._storage)
            logger.debug("Plugin count: %d", count)
            return count
        except Exception:
            logger.exception("Failed to count plugins")
            return 0

    async def find_by_name(self, name: str) -> Plugin | None:
        """Find plugin by name.

        Args:
            name: Plugin name to search for.

        Returns:
            Plugin entity if found, None otherwise.

        """
        try:
            for plugin in self._storage.values():
                if plugin.name == name:
                    logger.debug("Plugin found by name: %s", name)
                    return plugin
            logger.debug("Plugin not found by name: %s", name)
            return None
        except Exception:
            logger.exception("Failed to find plugin by name: %s", name)
            return None


__all__ = [
    "PluginRepository",
]
