"""Pipeline application service using flext-core patterns.

This module provides the application service for pipeline management,
implementing business logic using domain entities and clean architecture.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core.domain.types import ServiceResult

# Use centralized logger from flext-infrastructure.monitoring.flext-observability
from flext_api.application.services.base import (
    PipelineBaseService,
    PipelineExecutor,
    PipelineReader,
    PipelineValidator,
    PipelineWriter,
)
from flext_api.domain.entities import APIPipeline as Pipeline, PipelineStatus

if TYPE_CHECKING:
    from uuid import UUID

    from flext_api.domain.ports import PipelineRepository


class PipelineService(
    PipelineBaseService,
    PipelineReader,
    PipelineWriter,
    PipelineExecutor,
    PipelineValidator,
):
    """Application service for pipeline management implementing ISP.

    This service implements business logic for pipeline operations,
    coordinating between domain entities and infrastructure.
    Implements segregated interfaces for focused responsibilities.
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

            # Validate pipeline name (ISP compliance)
            name_validation = await self.validate_pipeline_name(pipeline.name, owner_id)
            if not name_validation.is_success:
                return ServiceResult.fail(
                    name_validation.error or "Pipeline name validation failed",
                )

            # Validate pipeline configuration (ISP compliance)
            config_validation = await self.validate_pipeline_config(pipeline.config)
            if not config_validation.is_success:
                return ServiceResult.fail(
                    config_validation.error
                    or "Pipeline configuration validation failed",
                )

            # Save to repository
            save_result = await self.pipeline_repo.create(pipeline)
            if not save_result.is_success:
                return save_result

            saved_pipeline = save_result.unwrap()

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
            pipeline_result = await self.pipeline_repo.get(pipeline_id)
            if not pipeline_result.is_success:
                return pipeline_result

            pipeline = pipeline_result.unwrap()
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
            pipelines_result = await self.pipeline_repo.list(
                limit=limit,
                offset=offset,
                owner_id=owner_id,
                project_id=project_id,
                status=status,
            )
            if not pipelines_result.is_success:
                return pipelines_result

            pipelines = pipelines_result.unwrap()
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
            update_result = await self.pipeline_repo.update(pipeline)
            if not update_result.is_success:
                return update_result

            updated_pipeline = update_result.unwrap()

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
            update_result = await self.pipeline_repo.update(pipeline)
            if not update_result.is_success:
                return update_result

            updated_pipeline = update_result.unwrap()

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
            pipelines_result = await self.pipeline_repo.list(limit=1000, offset=0)
            if not pipelines_result.is_success:
                return False  # Assume no duplicates if we can't check

            existing_pipelines = pipelines_result.unwrap()
            return any(p.name == name for p in existing_pipelines)
        except (OSError, ConnectionError, TimeoutError, ValueError, TypeError):
            # If we can't check, assume no duplicate to avoid blocking creation
            return False

    # ==============================================================================
    # INTERFACE SEGREGATION PRINCIPLE: Pipeline Validation Methods
    # ==============================================================================

    async def validate_pipeline_config(
        self, config: dict[str, Any] | None,
    ) -> ServiceResult[bool]:
        """Validate pipeline configuration (ISP compliance).

        Args:
            config: Pipeline configuration to validate

        Returns:
            ServiceResult indicating validation success

        """
        try:
            # Basic validation rules
            if config is None or not isinstance(config, dict):
                return ServiceResult.fail("Configuration must be a dictionary")

            # Check for required configuration keys
            required_keys = ["source", "target"]
            missing_keys = [key for key in required_keys if key not in config]
            if missing_keys:
                return ServiceResult.fail(
                    f"Missing required configuration keys: {missing_keys}",
                )

            # Validate source configuration
            source_config = config.get("source", {})
            if not isinstance(source_config, dict):
                return ServiceResult.fail("Source configuration must be a dictionary")

            # Validate target configuration
            target_config = config.get("target", {})
            if not isinstance(target_config, dict):
                return ServiceResult.fail("Target configuration must be a dictionary")

            self.logger.info("Pipeline configuration validated successfully")
            return ServiceResult.ok(True)

        except Exception as e:
            self.logger.exception(
                "Failed to validate pipeline configuration", error=str(e),
            )
            return ServiceResult.fail(f"Configuration validation failed: {e}")

    async def validate_pipeline_name(
        self, name: str, owner_id: UUID | None,
    ) -> ServiceResult[bool]:
        """Validate pipeline name uniqueness (ISP compliance).

        Args:
            name: Pipeline name to validate
            owner_id: Owner ID for scoped validation

        Returns:
            ServiceResult indicating validation success

        """
        try:
            # Basic name validation
            if not name or not name.strip():
                return ServiceResult.fail("Pipeline name cannot be empty")

            if len(name) < 3:
                return ServiceResult.fail("Pipeline name must be at least 3 characters")

            if len(name) > 100:
                return ServiceResult.fail(
                    "Pipeline name must be 100 characters or less",
                )

            # Check for invalid characters
            invalid_chars = set(name) - set(
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_",
            )
            if invalid_chars:
                return ServiceResult.fail(
                    f"Pipeline name contains invalid characters: {invalid_chars}",
                )

            # Check for uniqueness
            is_duplicate = await self._is_duplicate_name(name, owner_id)
            if is_duplicate:
                return ServiceResult.fail(f"Pipeline name '{name}' already exists")

            self.logger.info("Pipeline name validated successfully", name=name)
            return ServiceResult.ok(True)

        except Exception as e:
            self.logger.exception(
                "Failed to validate pipeline name", name=name, error=str(e),
            )
            return ServiceResult.fail(f"Name validation failed: {e}")
