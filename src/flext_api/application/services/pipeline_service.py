"""Pipeline application service using flext-core patterns.

This module provides the application service for pipeline management
implementing business logic using domain entities and clean architecture.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core import FlextResult, get_logger

# Use centralized logger from flext-infrastructure.monitoring.flext-observability
from flext_api.application.services.base import (
    PipelineBaseService,
    PipelineExecutor,
    PipelineReader,
    PipelineValidator,
    PipelineWriter,
)
from flext_api.domain.entities import (
    EntityId,
    FlextAPIPipeline as Pipeline,
    PipelineStatus,
    UserId,
)

if TYPE_CHECKING:
    from uuid import UUID

    from flext_api.domain.ports import PipelineRepository

# Create logger using flext-core get_logger function
logger = get_logger(__name__)


class PipelineService(
    PipelineBaseService,
    PipelineReader,
    PipelineWriter,
    PipelineExecutor,
    PipelineValidator,
):
    """Application service for pipeline management implementing ISP.

    This service implements business logic for pipeline operations
    coordinating between domain entities and infrastructure.
    Implements segregated interfaces for focused responsibilities.
    """

    def __init__(self, pipeline_repo: PipelineRepository) -> None:
        super().__init__(pipeline_repo)
        # Use repository directly
        self.pipeline_repo = self.repository

    async def create_pipeline(
        self,
        name: str,
        description: str | None = None,
        config: dict[str, Any] | None = None,
        owner_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> FlextResult[Any]:
        """Create a new pipeline.

        Args:
            name: Pipeline name.,
            description: Optional pipeline description.,
            config: Optional pipeline configuration.,
            owner_id: Optional owner ID.,
            project_id: Optional project ID.,

        Returns:
            FlextResult containing created pipeline.

        """
        try:
            pipeline = Pipeline(
                name=name,
                description=description,
                config=config or {},
                owner_id=UserId(str(owner_id)) if owner_id else None,
                project_id=EntityId(str(project_id)) if project_id else None,
            )

            # Validate pipeline name (ISP compliance)
            name_validation = await self.validate_pipeline_name(pipeline.name, owner_id)
            if not name_validation.success:
                return FlextResult.fail(
                    name_validation.error or "Pipeline name validation failed",
                )

            # Validate pipeline configuration (ISP compliance)
            config_validation = await self.validate_pipeline_config(pipeline.config)
            if not config_validation.success:
                return FlextResult.fail(
                    config_validation.error
                    or "Pipeline configuration validation failed",
                )

            # Save to repository
            save_result = await self.pipeline_repo.create(pipeline)
            if not save_result.success:
                return save_result

            saved_pipeline = save_result.data
            if saved_pipeline is None:
                return FlextResult.fail("Pipeline creation returned None")

            logger.info(
                f"Pipeline created successfully - pipeline_id: {saved_pipeline.id}, name: {saved_pipeline.name}",
            )
            return FlextResult.ok(saved_pipeline)

        except Exception as e:
            logger.exception("Operation failed")
            return FlextResult.fail(f"Failed to create pipeline: {e}")

    async def get_pipeline(self, pipeline_id: UUID) -> FlextResult[Any]:
        """Get pipeline by ID.

        Args:
            pipeline_id: Pipeline unique identifier.,

        Returns:
            FlextResult containing requested pipeline.

        """
        try:
            pipeline_result = await self.pipeline_repo.get(str(pipeline_id))
            if not pipeline_result.success:
                return pipeline_result

            pipeline = pipeline_result.data
            return FlextResult.ok(pipeline)

        except Exception as e:
            logger.exception("Pipeline operation failed")
            return FlextResult.fail(f"Failed to get pipeline: {e}")

    async def list_pipelines(
        self,
        owner_id: UUID | None = None,
        project_id: UUID | None = None,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> FlextResult[Any]:
        """List pipelines with optional filtering.

        Args:
            owner_id: Optional owner ID filter.,
            project_id: Optional project ID filter.,
            status: Optional status filter.,
            limit: Maximum number of results.,
            offset: Results offset for pagination.,

        Returns:
            FlextResult containing list of pipelines.

        """
        try:
            pipelines_result = await self.pipeline_repo.list(
                limit=limit,
                offset=offset,
                owner_id=str(owner_id) if owner_id else None,
                project_id=str(project_id) if project_id else None,
                status=status,
            )
            if not pipelines_result.success:
                return pipelines_result

            pipelines = pipelines_result.data
            return FlextResult.ok(pipelines)

        except Exception as e:
            logger.exception("Operation failed")
            return FlextResult.fail(f"Failed to list pipelines: {e}")

    async def update_pipeline(
        self,
        pipeline_id: UUID,
        name: str | None = None,
        description: str | None = None,
        config: dict[str, Any] | None = None,
        status: str | None = None,
    ) -> FlextResult[Any]:
        """Update an existing pipeline.

        Args:
            pipeline_id: Pipeline unique identifier.,
            name: Optional new name.,
            description: Optional new description.,
            config: Optional new configuration.,
            status: Optional new status.,

        Returns:
            FlextResult containing updated pipeline.

        """
        try:
            # Get existing pipeline
            existing_result = await self.get_pipeline(pipeline_id)
            if not existing_result.success:
                return existing_result

            pipeline = existing_result.data
            if pipeline is None:
                return FlextResult.fail("Pipeline not found")

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
            if not update_result.success:
                return update_result

            updated_pipeline = update_result.data
            if updated_pipeline is None:
                return FlextResult.fail("Pipeline update returned None")

            logger.info(
                f"Pipeline updated successfully - pipeline_id: {pipeline_id}, name: {updated_pipeline.name}",
            )
            return FlextResult.ok(updated_pipeline)

        except Exception as e:
            logger.exception("Pipeline operation failed")
            return FlextResult.fail(f"Failed to update pipeline: {e}")

    async def delete_pipeline(self, pipeline_id: UUID) -> FlextResult[Any]:
        """Delete a pipeline.

        Args:
            pipeline_id: Pipeline unique identifier.,

        Returns:
            FlextResult indicating deletion success.

        """
        try:
            # Check if pipeline exists:
            existing_result = await self.get_pipeline(pipeline_id)
            if not existing_result.success:
                return FlextResult.fail("Pipeline not found")

            # Delete from repository
            await self.pipeline_repo.delete(str(pipeline_id))

            logger.info(
                "Pipeline deleted successfully", extra={"pipeline_id": str(pipeline_id)},
            )
            return FlextResult.ok(True)

        except Exception as e:
            logger.exception("Pipeline operation failed")
            return FlextResult.fail(f"Failed to delete pipeline: {e}")

    async def execute_pipeline(self, pipeline_id: UUID) -> FlextResult[Any]:
        """Execute a pipeline by updating its status to running.

        Args:
            pipeline_id: Pipeline unique identifier.,

        Returns:
            FlextResult containing the updated pipeline.

        """
        try:
            # Get existing pipeline
            existing_result = await self.get_pipeline(pipeline_id)
            if not existing_result.success:
                return existing_result

            pipeline = existing_result.data
            if pipeline is None:
                return FlextResult.fail("Pipeline not found")

            # Update status to running
            pipeline.pipeline_status = PipelineStatus.RUNNING

            # Save the updated pipeline
            update_result = await self.pipeline_repo.update(pipeline)
            if not update_result.success:
                return update_result

            updated_pipeline = update_result.data
            if updated_pipeline is None:
                return FlextResult.fail("Pipeline update returned None")

            logger.info(
                f"Pipeline execution started - pipeline_id: {pipeline_id}, name: {updated_pipeline.name}",
            )
            return FlextResult.ok(updated_pipeline)

        except Exception as e:
            logger.exception("Pipeline operation failed")
            return FlextResult.fail(f"Failed to execute pipeline: {e}")

    async def _is_duplicate_name(self, name: str, owner_id: UUID | None) -> bool:
        try:
            pipelines_result = await self.pipeline_repo.list(limit=1000, offset=0)
            if not pipelines_result.success:
                return False  # Assume no duplicates if we can't check

            existing_pipelines = pipelines_result.data
            if existing_pipelines is None:
                return False
            return any(p.name == name for p in existing_pipelines)
        except (OSError, ConnectionError, TimeoutError, ValueError, TypeError):
            # If we can't check, assume no duplicate to avoid blocking creation
            return False

    # ==============================================================================
    # INTERFACE SEGREGATION PRINCIPLE: Pipeline Validation Methods
    # ==============================================================================

    async def validate_pipeline_config(
        self, config: dict[str, Any] | None,
    ) -> FlextResult[Any]:
        """Validate pipeline configuration (ISP compliance).

        Args:
            config: Pipeline configuration to validate,

        Returns:
            FlextResult indicating validation success

        """
        try:
            # Basic validation rules
            if config is None or not isinstance(config, dict):
                return FlextResult.fail("Configuration must be a dictionary")

            # Check for required configuration keys (updated to new terminology)
            required_keys = ["extractor", "loader"]
            missing_keys = [key for key in required_keys if key not in config]
            if missing_keys:
                return FlextResult.fail(
                    f"Missing required configuration keys: {missing_keys}",
                )

            # Validate extractor configuration
            extractor_config = config.get("extractor")
            if extractor_config is not None and not isinstance(extractor_config, str):
                return FlextResult.fail("Extractor must be a string plugin name")

            # Validate loader configuration
            loader_config = config.get("loader")
            if loader_config is not None and not isinstance(loader_config, str):
                return FlextResult.fail("Loader must be a string plugin name")

            logger.info("Pipeline configuration validated successfully")
            return FlextResult.ok(True)

        except Exception as e:
            logger.exception("Operation failed")
            return FlextResult.fail(f"Configuration validation failed: {e}")

    async def validate_pipeline_name(
        self, name: str, owner_id: UUID | None,
    ) -> FlextResult[Any]:
        """Validate pipeline name uniqueness (ISP compliance).

        Args:
            name: Pipeline name to validate,
            owner_id: Owner ID for scoped validation,

        Returns:
            FlextResult indicating validation success

        """
        try:
            # Basic name validation
            if not name or not name.strip():
                return FlextResult.fail("Pipeline name cannot be empty")

            if len(name) < 3:
                return FlextResult.fail("Pipeline name must be at least 3 characters")

            if len(name) > 100:
                return FlextResult.fail("Pipeline name must be 100 characters or less")

            # Check for invalid characters
            invalid_chars = set(name) - set(
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_",
            )
            if invalid_chars:
                return FlextResult.fail(
                    f"Pipeline name contains invalid characters: {invalid_chars}",
                )

            # Check for uniqueness
            is_duplicate = await self._is_duplicate_name(name, owner_id)
            if is_duplicate:
                return FlextResult.fail(f"Pipeline name '{name}' already exists")

            logger.info("Pipeline name validated successfully")
            return FlextResult.ok(True)

        except Exception as e:
            logger.exception("Operation failed")
            return FlextResult.fail(f"Name validation failed: {e}")
