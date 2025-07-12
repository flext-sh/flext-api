"""In-memory repository implementations for FLEXT-API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the in-memory repository implementations for the FLEXT API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_api.domain.entities import Pipeline
from flext_api.domain.entities import PipelineStatus
from flext_api.domain.entities import Plugin
from flext_core.config.base import injectable

# Use centralized logger from flext-observability - ELIMINATE DUPLICATION
from flext_observability.logging import get_logger

if TYPE_CHECKING:
    from uuid import UUID

logger = get_logger(__name__)


@injectable
class InMemoryPipelineRepository:
    """In-memory implementation of pipeline repository."""

    def __init__(self) -> None:
        self._storage: dict[UUID, Pipeline] = {}

    async def save(self, pipeline: Pipeline) -> Pipeline:
        """Save pipeline to in-memory storage.

        Args:
            pipeline: Pipeline entity to save.

        Returns:
            The saved pipeline entity.

        """
        self._storage[pipeline.id] = pipeline
        pipeline.touch()  # Update timestamp

        logger.debug(
            "Pipeline saved to memory",
            pipeline_id=str(pipeline.id),
            name=pipeline.name,
        )

        return pipeline

    async def get_by_id(self, pipeline_id: UUID) -> Pipeline | None:
        """Get pipeline by ID from in-memory storage.

        Args:
            pipeline_id: Unique identifier of the pipeline.

        Returns:
            Pipeline entity if found, None otherwise.

        """
        return self._storage.get(pipeline_id)

    async def list_pipelines(
        self,
        owner_id: UUID | None = None,
        project_id: UUID | None = None,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Pipeline]:
        """List pipelines.

        Args:
            owner_id: The owner ID.
            project_id: The project ID.
            status: The status of the pipelines.
            limit: The limit of pipelines to return.
            offset: The offset of the pipelines to return.

        Returns:
            The list of pipelines.

        """
        pipelines = list(self._storage.values())

        # Apply filters
        if owner_id:
            pipelines = [p for p in pipelines if p.owner_id == owner_id]

        if project_id:
            pipelines = [p for p in pipelines if p.project_id == project_id]

        if status:
            try:
                status_enum = PipelineStatus(status)
                pipelines = [p for p in pipelines if p.pipeline_status == status_enum]
            except ValueError:
                logger.warning(f"Invalid status filter: {status}")

        # Sort by created_at descending
        pipelines.sort(key=lambda p: p.created_at, reverse=True)

        # Apply pagination
        return pipelines[offset : offset + limit]

    async def delete(self, pipeline_id: UUID) -> bool:
        """Delete pipeline from in-memory storage.

        Args:
            pipeline_id: Unique identifier of the pipeline to delete.

        Returns:
            True if pipeline was deleted, False if not found.

        """
        if pipeline_id in self._storage:
            del self._storage[pipeline_id]
            logger.debug(f"Pipeline deleted from memory: {pipeline_id}")
            return True
        return False

    async def count(self) -> int:
        """Count total number of pipelines in storage.

        Returns:
            Total number of pipelines.

        """
        return len(self._storage)


@injectable
class InMemoryPluginRepository:
    """In-memory implementation of plugin repository."""

    def __init__(self) -> None:
        self._storage: dict[UUID, Plugin] = {}

    async def save(self, plugin: Plugin) -> Plugin:
        """Save plugin to in-memory storage.

        Args:
            plugin: Plugin entity to save.

        Returns:
            The saved plugin entity.

        """
        self._storage[plugin.id] = plugin
        plugin.touch()  # Update timestamp

        logger.debug(
            "Plugin saved to memory",
            plugin_id=str(plugin.id),
            name=plugin.name,
            type=plugin.plugin_type,
        )

        return plugin

    async def get_by_id(self, plugin_id: UUID) -> Plugin | None:
        """Get plugin by ID from in-memory storage.

        Args:
            plugin_id: Unique identifier of the plugin.

        Returns:
            Plugin entity if found, None otherwise.

        """
        return self._storage.get(plugin_id)

    async def get_by_name(self, name: str) -> Plugin | None:
        """Get plugin by name from in-memory storage.

        Args:
            name: Name of the plugin.

        Returns:
            Plugin entity if found, None otherwise.

        """
        for plugin in self._storage.values():
            if plugin.name == name:
                return plugin
        return None

    async def list_plugins(
        self,
        plugin_type: str | None = None,
        enabled: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Plugin]:
        """List plugins with optional filtering.

        Args:
            plugin_type: Optional plugin type filter.
            enabled: Optional enabled status filter.
            limit: Maximum number of plugins to return.
            offset: Number of plugins to skip.

        Returns:
            List of plugin entities matching the criteria.

        """
        plugins = list(self._storage.values())

        # Apply filters
        if plugin_type:
            plugins = [p for p in plugins if p.plugin_type.value == plugin_type]

        if enabled is not None:
            plugins = [p for p in plugins if p.enabled == enabled]

        # Sort by name
        plugins.sort(key=lambda p: p.name)

        # Apply pagination
        return plugins[offset : offset + limit]

    async def delete(self, plugin_id: UUID) -> bool:
        """Delete plugin from in-memory storage.

        Args:
            plugin_id: Unique identifier of the plugin to delete.

        Returns:
            True if plugin was deleted, False if not found.

        """
        if plugin_id in self._storage:
            del self._storage[plugin_id]
            logger.debug(f"Plugin deleted from memory: {plugin_id}")
            return True
        return False

    async def count(self) -> int:
        """Count total number of plugins in storage.

        Returns:
            Total number of plugins.

        """
        return len(self._storage)
