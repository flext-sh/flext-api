"""Repository interfaces for FLEXT-API domain layer.

This module defines the repository interfaces that will be implemented
by the infrastructure layer, following Clean Architecture principles.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flext_api.domain.entities import Pipeline, PipelineId, Plugin, PluginId


class PipelineRepository(ABC):
    """Repository interface for Pipeline entities."""

    @abstractmethod
    async def save(self, pipeline: Pipeline) -> Pipeline:
        """Save a pipeline entity.

        Args:
            pipeline: Pipeline entity to save,

        Returns:
            Saved pipeline entity

        """

    @abstractmethod
    async def find_by_id(self, pipeline_id: PipelineId) -> Pipeline | None:
        """Find pipeline by ID.

        Args:
            pipeline_id: Pipeline identifier,

        Returns:
            Pipeline entity if found, None otherwise

        """

    @abstractmethod
    async def list_all(self) -> list[Pipeline]:
        """List all pipelines.

        Returns:
            List of all pipeline entities

        """

    @abstractmethod
    async def delete(self, pipeline_id: PipelineId) -> bool:
        """Delete pipeline by ID.

        Args:
            pipeline_id: Pipeline identifier,

        Returns:
            True if deleted, False if not found

        """


class PluginRepository(ABC):
    """Repository interface for Plugin entities."""

    @abstractmethod
    async def save(self, plugin: Plugin) -> Plugin:
        """Save a plugin entity.

        Args:
            plugin: Plugin entity to save,

        Returns:
            Saved plugin entity

        """

    @abstractmethod
    async def find_by_id(self, plugin_id: PluginId) -> Plugin | None:
        """Find plugin by ID.

        Args:
            plugin_id: Plugin identifier,

        Returns:
            Plugin entity if found, None otherwise

        """

    @abstractmethod
    async def list_all(self) -> list[Plugin]:
        """List all plugins.

        Returns:
            List of all plugin entities

        """

    @abstractmethod
    async def delete(self, plugin_id: PluginId) -> bool:
        """Delete plugin by ID.

        Args:
            plugin_id: Plugin identifier,

        Returns:
            True if deleted, False if not found

        """
