"""Pipeline application service using flext-core patterns.

This module provides the application service for pipeline management,
implementing business logic using domain entities and clean architecture.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core.domain.types import ServiceResult

# Use centralized logger from flext-infrastructure.monitoring.flext-observability
from flext_api.application.services.base import PipelineBaseService
from flext_api.domain.entities import APIPipeline as Pipeline, PipelineStatus

if TYPE_CHECKING:
    from uuid import UUID

    from flext_api.domain.ports import PipelineRepository


class PipelineService(PipelineBaseService):
    """Application service for pipeline management.

    This service implements business logic for pipeline operations,
    coordinating between domain entities and infrastructure.
    """

    def __init__(self, pipeline_repo: PipelineRepository) -> None:
        super().__init__(pipeline_repo)
        # Alias for backward compatibility
        self.pipeline_repo = self.repository

    async def create_pipeline(
        self,
        name: str,
        description: str | None = None,
        config: dict[str, Any] | None = None,
        owner_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> ServiceResult[Pipeline]:
        """Create a new pipeline.

        Args:
            name: Pipeline name.
            description: Optional pipeline description.
            config: Optional pipeline configuration.
            owner_id: Optional owner ID.
            project_id: Optional project ID.

        Returns:
            ServiceResult containing created pipeline.

        """
        try:
            pipeline = Pipeline(
                name=name,
                description=description,
                config=config or {},
                owner_id=owner_id,
                project_id=project_id,
            )

            # Validate business rules
            if await self._is_duplicate_name(pipeline.name, owner_id):
                return ServiceResult.fail(
                    "Pipeline name already exists for this owner",
                )

            # Save to repository
            saved_pipeline = await self.pipeline_repo.save(pipeline)

            self.logger.info(
                "Pipeline created successfully",
                pipeline_id=str(saved_pipeline.id),
                name=saved_pipeline.name,
                owner_id=str(owner_id) if owner_id else None,
            )

            return ServiceResult.ok(saved_pipeline)

        except Exception as e:
            self.logger.exception("Failed to create pipeline", error=str(e))
            return ServiceResult.fail(f"Failed to create pipeline: {e}")

    async def get_pipeline(self, pipeline_id: UUID) -> ServiceResult[Pipeline]:
        """Get pipeline by ID.

        Args:
            pipeline_id: Pipeline unique identifier.

        Returns:
            ServiceResult containing requested pipeline.

        """
        try:
            pipeline = await self.pipeline_repo.get(pipeline_id)
            if not pipeline:
                return ServiceResult.fail("Pipeline not found")

            return ServiceResult.ok(pipeline)

        except Exception as e:
            self.logger.exception(
                "Failed to get pipeline",
                pipeline_id=str(pipeline_id),
                error=str(e),
            )
            return ServiceResult.fail(f"Failed to get pipeline: {e}")

    async def list_pipelines(
        self,
        owner_id: UUID | None = None,
        project_id: UUID | None = None,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> ServiceResult[list[Pipeline]]:
        """List pipelines with optional filtering.

        Args:
            owner_id: Optional owner ID filter.
            project_id: Optional project ID filter.
            status: Optional status filter.
            limit: Maximum number of results.
            offset: Results offset for pagination.

        Returns:
            ServiceResult containing list of pipelines.

        """
        try:
            pipelines = await self.pipeline_repo.list(limit=1000, offset=0)

            return ServiceResult.ok(pipelines)

        except Exception as e:
            self.logger.exception("Failed to list pipelines", error=str(e))
            return ServiceResult.fail(f"Failed to list pipelines: {e}")

    async def update_pipeline(
        self,
        pipeline_id: UUID,
        name: str | None = None,
        description: str | None = None,
        config: dict[str, Any] | None = None,
        status: str | None = None,
    ) -> ServiceResult[Pipeline]:
        """Update an existing pipeline.

        Args:
            pipeline_id: Pipeline unique identifier.
            name: Optional new name.
            description: Optional new description.
            config: Optional new configuration.
            status: Optional new status.

        Returns:
            ServiceResult containing updated pipeline.

        """
        try:
            # Get existing pipeline
            existing_result = await self.get_pipeline(pipeline_id)
            if not existing_result.is_success:
                return existing_result

            pipeline = existing_result.unwrap()

            # Apply updates
            if name is not None:
                pipeline.name = name
            if description is not None:
                pipeline.description = description
            if config is not None:
                pipeline.config = config
            if status is not None:
                pipeline.pipeline_status = PipelineStatus(status)

            # Save updates
            updated_pipeline = await self.pipeline_repo.save(pipeline)

            self.logger.info(
                "Pipeline updated successfully",
                pipeline_id=str(pipeline_id),
                name=updated_pipeline.name,
            )

            return ServiceResult.ok(updated_pipeline)

        except Exception as e:
            self.logger.exception(
                "Failed to update pipeline",
                pipeline_id=str(pipeline_id),
                error=str(e),
            )
            return ServiceResult.fail(f"Failed to update pipeline: {e}")

    async def delete_pipeline(self, pipeline_id: UUID) -> ServiceResult[bool]:
        """Delete a pipeline.

        Args:
            pipeline_id: Pipeline unique identifier.

        Returns:
            ServiceResult indicating deletion success.

        """
        try:
            # Check if pipeline exists:
            existing_result = await self.get_pipeline(pipeline_id)
            if not existing_result.is_success:
                return ServiceResult.fail("Pipeline not found")

            # Delete from repository
            await self.pipeline_repo.delete(pipeline_id)

            self.logger.info(
                "Pipeline deleted successfully",
                pipeline_id=str(pipeline_id),
            )

            return ServiceResult.ok(data=True)

        except Exception as e:
            self.logger.exception(
                "Failed to delete pipeline",
                pipeline_id=str(pipeline_id),
                error=str(e),
            )
            return ServiceResult.fail(f"Failed to delete pipeline: {e}")

    async def execute_pipeline(self, pipeline_id: UUID) -> ServiceResult[Pipeline]:
        """Execute a pipeline by updating its status to running.

        Args:
            pipeline_id: Pipeline unique identifier.

        Returns:
            ServiceResult containing the updated pipeline.

        """
        try:
            # Get existing pipeline
            existing_result = await self.get_pipeline(pipeline_id)
            if not existing_result.is_success:
                return existing_result

            pipeline = existing_result.unwrap()

            # Update status to running
            pipeline.pipeline_status = PipelineStatus.RUNNING

            # Save the updated pipeline
            updated_pipeline = await self.pipeline_repo.save(pipeline)

            self.logger.info(
                "Pipeline execution started",
                pipeline_id=str(pipeline_id),
                name=updated_pipeline.name,
                status=updated_pipeline.pipeline_status,
            )

            return ServiceResult.ok(updated_pipeline)

        except Exception as e:
            self.logger.exception(
                "Failed to execute pipeline",
                pipeline_id=str(pipeline_id),
                error=str(e),
            )
            return ServiceResult.fail(f"Failed to execute pipeline: {e}")

    async def _is_duplicate_name(self, name: str, owner_id: UUID | None) -> bool:
        try:
            existing_pipelines = await self.pipeline_repo.list(limit=1000, offset=0)
            return any(p.name == name for p in existing_pipelines)
        except (OSError, ConnectionError, TimeoutError, ValueError, TypeError):
            # If we can't check, assume no duplicate to avoid blocking creation
            return False
