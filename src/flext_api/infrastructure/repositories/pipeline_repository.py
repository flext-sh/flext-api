"""Pipeline repository implementation using flext-core patterns.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the repository implementation for pipeline persistence
using clean architecture and dependency injection patterns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.config.base import injectable
from flext_observability.logging import get_logger

if TYPE_CHECKING:
    from uuid import UUID

    from flext_api.domain.entities import Pipeline

logger = get_logger(__name__)


@injectable()
class PipelineRepository:
    """Repository for pipeline persistence.

    This repository handles pipeline data persistence using
    clean architecture patterns and dependency injection.
    """

    def __init__(self) -> None:
        self._storage: dict[UUID, Pipeline] = {}

    async def save(self, pipeline: Pipeline) -> Pipeline:
        """Save pipeline to repository.

        Args:
            pipeline: Pipeline entity to save.

        Returns:
            Saved pipeline entity.

        Raises:
            Exception: If save operation fails.

        """
        try:
            # In production, this would use actual database
            self._storage[pipeline.id] = pipeline

            logger.info(
                "Pipeline saved successfully",
                pipeline_id=str(pipeline.id),
                name=pipeline.name,
            )

            return pipeline

        except Exception as e:
            logger.exception(
                "Failed to save pipeline",
                pipeline_id=str(pipeline.id),
                error=str(e),
            )
            raise

    async def get_by_id(self, pipeline_id: UUID) -> Pipeline | None:
        """Get pipeline by ID.

        Args:
            pipeline_id: Unique identifier of the pipeline.

        Returns:
            Pipeline entity if found, None otherwise.

        Raises:
            Exception: If retrieval operation fails.

        """
        try:
            pipeline = self._storage.get(pipeline_id)

            if pipeline:
                logger.debug("Pipeline retrieved", pipeline_id=str(pipeline_id))
            else:
                logger.warning("Pipeline not found", pipeline_id=str(pipeline_id))

            return pipeline

        except Exception as e:
            logger.exception(
                "Failed to get pipeline",
                pipeline_id=str(pipeline_id),
                error=str(e),
            )
            raise

    async def list_pipelines(
        self,
        owner_id: UUID | None = None,
        project_id: UUID | None = None,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Pipeline]:
        """List pipelines with optional filters and pagination.

        Args:
            owner_id: Filter by pipeline owner ID.
            project_id: Filter by project ID.
            status: Filter by pipeline status.
            limit: Maximum number of pipelines to return.
            offset: Number of pipelines to skip.

        Returns:
            List of pipeline entities matching the criteria.

        Raises:
            Exception: If list operation fails.

        """
        try:
            pipelines = list(self._storage.values())

            # Apply filters
            if owner_id:
                pipelines = [p for p in pipelines if p.owner_id == owner_id]

            if project_id:
                pipelines = [p for p in pipelines if p.project_id == project_id]

            if status:
                pipelines = [p for p in pipelines if p.status == status]

            # Apply pagination
            total_count = len(pipelines)
            pipelines = pipelines[offset : offset + limit]

            logger.debug(
                "Pipelines listed",
                count=len(pipelines),
                total=total_count,
                owner_id=str(owner_id) if owner_id else None,
                project_id=str(project_id) if project_id else None,
                status=status,
            )

            return pipelines

        except Exception as e:
            logger.exception("Failed to list pipelines", error=str(e))
            raise

    async def delete(self, pipeline_id: UUID) -> bool:
        """Delete pipeline by ID.

        Args:
            pipeline_id: Unique identifier of the pipeline to delete.

        Returns:
            True if pipeline was deleted, False if not found.

        Raises:
            Exception: If delete operation fails.

        """
        try:
            if pipeline_id in self._storage:
                del self._storage[pipeline_id]
                logger.info("Pipeline deleted", pipeline_id=str(pipeline_id))
                return True

            logger.warning(
                "Pipeline not found for deletion",
                pipeline_id=str(pipeline_id),
            )
            return False

        except Exception as e:
            logger.exception(
                "Failed to delete pipeline",
                pipeline_id=str(pipeline_id),
                error=str(e),
            )
            raise

    async def get_by_name(
        self,
        name: str,
        owner_id: UUID | None = None,
    ) -> Pipeline | None:
        """Get pipeline by name and optional owner.

        Args:
            name: Name of the pipeline.
            owner_id: Optional owner ID to filter by.

        Returns:
            Pipeline entity if found, None otherwise.

        Raises:
            Exception: If retrieval operation fails.

        """
        try:
            pipelines = await self.list_pipelines(owner_id=owner_id)

            for pipeline in pipelines:
                if pipeline.name == name:
                    return pipeline

            return None

        except Exception as e:
            logger.exception("Failed to get pipeline by name", name=name, error=str(e))
            raise

    async def count_pipelines(
        self,
        owner_id: UUID | None = None,
        project_id: UUID | None = None,
        status: str | None = None,
    ) -> int:
        """Count pipelines with optional filters.

        Args:
            owner_id: Filter by pipeline owner ID.
            project_id: Filter by project ID.
            status: Filter by pipeline status.

        Returns:
            Number of pipelines matching the criteria.

        Raises:
            Exception: If count operation fails.

        """
        try:
            pipelines = await self.list_pipelines(
                owner_id=owner_id,
                project_id=project_id,
                status=status,
                limit=1000000,  # Large limit to get all
                offset=0,
            )

            return len(pipelines)

        except Exception as e:
            logger.exception("Failed to count pipelines", error=str(e))
            raise
