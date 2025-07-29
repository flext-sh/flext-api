"""Plugin repository implementation using flext-core patterns.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the repository implementation for plugin persistence
using clean architecture and dependency injection patterns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

# Import runtime dependencies
from flext_core import FlextResult, get_logger

from flext_api.domain.ports import PluginRepository

if TYPE_CHECKING:
    from flext_api.domain.entities import Plugin

# Create logger using flext-core get_logger function
logger = get_logger(__name__)


class FlextInMemoryPluginRepository(PluginRepository):
    """Repository for plugin persistence.

    This repository handles plugin data persistence using
    clean architecture patterns and dependency injection.
    """

    def __init__(self) -> None:
        """Initialize plugin repository."""
        self._storage: dict[str, Plugin] = {}

    async def create(self, plugin: Plugin) -> FlextResult[Any]:
        """Create a new plugin."""
        try:
            if plugin.id in self._storage:
                return FlextResult.fail(f"Plugin {plugin.id} already exists")

            self._storage[plugin.id] = plugin
            logger.info(f"Plugin created successfully: {plugin.name}")
            return FlextResult.ok(plugin)
        except Exception as e:
            logger.exception(f"Failed to create plugin: {plugin.name}")
            return FlextResult.fail(f"Failed to create plugin: {e}")

    async def get(self, plugin_id: str) -> FlextResult[Any]:
        """Get plugin by ID.

        Args:
            plugin_id: Plugin unique identifier.,

        Returns:
            Plugin entity if found, None otherwise.

        """
        try:
            plugin = self._storage.get(plugin_id)
            if plugin:
                logger.debug(f"Plugin found: {plugin.name}")
                return FlextResult.ok(plugin)
            logger.debug(f"Plugin not found: {plugin_id}")
            return FlextResult.fail(f"Plugin {plugin_id} not found")
        except Exception as e:
            logger.exception(f"Failed to get plugin: {plugin_id}")
            return FlextResult.fail(f"Failed to get plugin: {e}")

    async def list(
        self,
        limit: int = 2,
        offset: int = 0,
        plugin_type: str | None = None,
        status: str | None = None,
    ) -> FlextResult[Any]:
        """List plugins with filtering and pagination.

        Args:
            limit: Maximum number of plugins to return.,
            offset: Number of plugins to skip.,
            plugin_type: Filter by plugin type.,
            status: Filter by plugin status.,

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
                f"Listed {len(paginated)} plugins (limit={limit}, offset={offset})",
            )
            return FlextResult.ok(paginated)

        except Exception as e:
            logger.exception("Failed to list plugins")
            return FlextResult.fail(f"Failed to list plugins: {e}")

    async def update(self, plugin: Plugin) -> FlextResult[Any]:
        """Update existing plugin."""
        try:
            if plugin.id not in self._storage:
                return FlextResult.fail(f"Plugin {plugin.id} not found")

            self._storage[plugin.id] = plugin
            logger.info(f"Plugin updated successfully: {plugin.name}")
            return FlextResult.ok(plugin)
        except Exception as e:
            logger.exception(f"Failed to update plugin: {plugin.name}")
            return FlextResult.fail(f"Failed to update plugin: {e}")

    async def delete(self, plugin_id: str) -> FlextResult[Any]:
        """Delete plugin by ID.

        Args:
            plugin_id: Plugin unique identifier.,

        Returns:
            True if plugin was deleted, False if not found.

        """
        try:
            if plugin_id in self._storage:
                plugin = self._storage.pop(plugin_id)
                logger.info(f"Plugin deleted successfully: {plugin.name}")
                return FlextResult.ok(True)
            logger.warning(f"Plugin not found for deletion: {plugin_id}")
            return FlextResult.fail(f"Plugin {plugin_id} not found")
        except Exception as e:
            logger.exception(f"Failed to delete plugin: {plugin_id}")
            return FlextResult.fail(f"Failed to delete plugin: {e}")

    async def exists(self, plugin_id: str) -> bool:
        """Check if plugin exists.

        Args:
            plugin_id: Plugin unique identifier.,

        Returns:
            True if plugin exists, False otherwise.

        """
        try:
            exists = plugin_id in self._storage
            logger.debug(f"Plugin exists check: {plugin_id} = {exists}")
            return exists
        except Exception:
            logger.exception(f"Failed to check plugin existence: {plugin_id}")
            return False

    async def count(
        self,
        plugin_type: str | None = None,
        status: str | None = None,
    ) -> FlextResult[Any]:
        """Count plugins with optional filtering.

        Args:
            plugin_type: Filter by plugin type.,
            status: Filter by status.,

        Returns:
            FlextResult containing count of matching plugins.

        """
        try:
            # Use list method to get filtered plugins and count them
            result = await self.list(
                limit=1000000,  # Large limit to get all
                offset=0,
                plugin_type=plugin_type,
                status=status,
            )
            if not result.success:
                return FlextResult.fail(result.error or "Failed to count plugins")

            count = len(result.data or [])
            logger.debug(f"Plugin count: {count}")
            return FlextResult.ok(count)
        except Exception as e:
            logger.exception("Failed to count plugins")
            return FlextResult.fail(f"Failed to count plugins: {e}")

    async def find_by_name(self, name: str) -> Plugin | None:
        """Find plugin by name.

        Args:
            name: Plugin name to search for.,

        Returns:
            Plugin entity if found, None otherwise.

        """
        try:
            for plugin in self._storage.values():
                if plugin.name == name:
                    logger.debug(f"Plugin found by name: {name}")
                    return plugin
            logger.debug(f"Plugin not found by name: {name}")
            return None
        except Exception:
            logger.exception(f"Failed to find plugin by name: {name}")
            return None

    async def save(self, plugin: Plugin) -> FlextResult[Any]:
        """Save plugin (create or update based on existence).

        Args:
            plugin: Plugin entity to save.,

        Returns:
            FlextResult containing saved plugin or error.

        """
        try:
            # Check if plugin exists
            if plugin.id in self._storage:
                # Update existing plugin
                return await self.update(plugin)
            # Create new plugin
            return await self.create(plugin)

        except Exception as e:
            logger.exception("Failed to save plugin")
            return FlextResult.fail(f"Failed to save plugin: {e}")


__all__ = ["FlextInMemoryPluginRepository"]
