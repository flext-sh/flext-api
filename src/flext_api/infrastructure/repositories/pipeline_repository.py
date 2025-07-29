"""Pipeline repository using flext-core patterns - NO LEGACY CODE."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from flext_core import FlextResult, get_logger

if TYPE_CHECKING:
    import builtins

    from flext_api.domain.entities import FlextAPIPipeline, PipelineExecution

from flext_api.domain.ports import PipelineRepository

# Create logger using flext-core get_logger function
logger = get_logger(__name__)


class FlextInMemoryPipelineRepository(PipelineRepository):
    """In-memory pipeline repository using flext-core patterns - NO FALLBACKS."""

    def __init__(self) -> None:
        """Initialize repository with thread-safe storage."""
        self._pipelines: dict[str, FlextAPIPipeline] = {}
        self._executions: dict[str, PipelineExecution] = {}
        logger.info("FlextInMemoryPipelineRepository initialized")

    async def create(self, pipeline: FlextAPIPipeline) -> FlextResult[FlextAPIPipeline]:
        """Create new pipeline - STRICT VALIDATION."""
        try:
            if not pipeline.id:
                return FlextResult.fail("Pipeline ID is required")

            if pipeline.id in self._pipelines:
                return FlextResult.fail(f"Pipeline {pipeline.id} already exists")

            # Validate required fields
            if not pipeline.name:
                return FlextResult.fail("Pipeline name is required")

            if not pipeline.config:
                return FlextResult.fail("Pipeline configuration is required")

            self._pipelines[pipeline.id] = pipeline
            logger.info(f"Created pipeline: {pipeline.id}")
            return FlextResult.ok(pipeline)

        except Exception as e:
            logger.exception("Failed to create pipeline")
            return FlextResult.fail(f"Pipeline creation failed: {e}")

    async def get(self, pipeline_id: str) -> FlextResult[FlextAPIPipeline | None]:
        """Get pipeline by ID - STRICT LOOKUP."""
        try:
            if not pipeline_id:
                return FlextResult.fail("Pipeline ID is required")

            pipeline = self._pipelines.get(pipeline_id)
            if pipeline:
                logger.debug(f"Retrieved pipeline: {pipeline_id}")
                return FlextResult.ok(pipeline)
            logger.debug(f"Pipeline not found: {pipeline_id}")
            return FlextResult.ok(None)

        except Exception as e:
            logger.exception(f"Failed to get pipeline: {pipeline_id}")
            return FlextResult.fail(f"Pipeline retrieval failed: {e}")

    async def update(self, pipeline: FlextAPIPipeline) -> FlextResult[FlextAPIPipeline]:
        """Update existing pipeline - STRICT VALIDATION."""
        try:
            if not pipeline.id:
                return FlextResult.fail("Pipeline ID is required")

            if pipeline.id not in self._pipelines:
                return FlextResult.fail(f"Pipeline {pipeline.id} not found")

            # Validate required fields
            if not pipeline.name:
                return FlextResult.fail("Pipeline name is required")

            if not pipeline.config:
                return FlextResult.fail("Pipeline configuration is required")

            # Update timestamp
            pipeline.updated_at = datetime.now(UTC)
            self._pipelines[pipeline.id] = pipeline

            logger.info(f"Updated pipeline: {pipeline.id}")
            return FlextResult.ok(pipeline)

        except Exception as e:
            logger.exception(f"Failed to update pipeline: {pipeline.id}")
            return FlextResult.fail(f"Pipeline update failed: {e}")

    async def delete(self, pipeline_id: str) -> FlextResult[bool]:
        """Delete pipeline - STRICT DELETION."""
        try:
            if not pipeline_id:
                return FlextResult.fail("Pipeline ID is required")

            if pipeline_id not in self._pipelines:
                return FlextResult.fail(f"Pipeline {pipeline_id} not found")

            # Delete associated executions first
            executions_to_delete = [
                exec_id
                for exec_id, execution in self._executions.items()
                if execution.pipeline_id == pipeline_id
            ]

            for exec_id in executions_to_delete:
                del self._executions[exec_id]

            del self._pipelines[pipeline_id]
            logger.info(
                f"Deleted pipeline: {pipeline_id} and {len(executions_to_delete)} executions",
            )
            return FlextResult.ok(True)

        except Exception as e:
            logger.exception(f"Failed to delete pipeline: {pipeline_id}")
            return FlextResult.fail(f"Pipeline deletion failed: {e}")

    async def list(
        self,
        limit: int = 100,
        offset: int = 0,
        owner_id: str | None = None,
        project_id: str | None = None,
        status: str | None = None,
    ) -> FlextResult[list[FlextAPIPipeline]]:
        """List pipelines with filters and pagination - EFFICIENT RETRIEVAL."""
        try:
            if limit <= 0:
                return FlextResult.fail("Limit must be positive")

            if offset < 0:
                return FlextResult.fail("Offset must be non-negative")

            pipelines = list(self._pipelines.values())

            # Apply filters
            if status:
                pipelines = [p for p in pipelines if p.pipeline_status == status]

            if owner_id:
                pipelines = [
                    p for p in pipelines if getattr(p, "owner_id", None) == owner_id
                ]

            if project_id:
                pipelines = [
                    p for p in pipelines if getattr(p, "project_id", None) == project_id
                ]

            # Sort by creation date (newest first)
            pipelines.sort(key=lambda p: p.created_at, reverse=True)

            # Apply pagination
            paginated_pipelines = pipelines[offset : offset + limit]

            logger.debug(
                f"Listed {len(paginated_pipelines)} pipelines (total: {len(pipelines)})",
            )
            return FlextResult.ok(paginated_pipelines)

        except Exception as e:
            logger.exception("Failed to list pipelines")
            return FlextResult.fail(f"Pipeline listing failed: {e}")

    async def count(
        self,
        owner_id: str | None = None,
        project_id: str | None = None,
        status: str | None = None,
    ) -> FlextResult[int]:
        """Count pipelines matching criteria - EFFICIENT COUNT."""
        try:
            # Get filtered list to count
            result = await self.list(
                limit=1000000,  # Large limit to get all
                offset=0,
                owner_id=owner_id,
                project_id=project_id,
                status=status,
            )

            if not result.success:
                return FlextResult.fail(result.error or "Count failed")

            count = len(result.data or [])
            logger.debug(f"Pipeline count: {count}")
            return FlextResult.ok(count)

        except Exception as e:
            logger.exception("Failed to count pipelines")
            return FlextResult.fail(f"Pipeline count failed: {e}")

    async def save(self, pipeline: FlextAPIPipeline) -> FlextResult[FlextAPIPipeline]:
        """Save pipeline (create or update) - SMART PERSISTENCE."""
        try:
            if pipeline.id in self._pipelines:
                return await self.update(pipeline)
            return await self.create(pipeline)

        except Exception as e:
            logger.exception("Failed to save pipeline")
            return FlextResult.fail(f"Pipeline save failed: {e}")

    # Execution methods
    async def create_execution(
        self, execution: PipelineExecution,
    ) -> FlextResult[PipelineExecution]:
        """Create pipeline execution - STRICT VALIDATION."""
        try:
            if not execution.id:
                execution.id = str(uuid4())

            if not execution.pipeline_id:
                return FlextResult.fail("Pipeline ID is required for execution")

            # Verify pipeline exists
            if execution.pipeline_id not in self._pipelines:
                return FlextResult.fail(f"Pipeline {execution.pipeline_id} not found")

            if execution.id in self._executions:
                return FlextResult.fail(f"Execution {execution.id} already exists")

            self._executions[execution.id] = execution
            logger.info(
                f"Created execution: {execution.id} for pipeline: {execution.pipeline_id}",
            )
            return FlextResult.ok(execution)

        except Exception as e:
            logger.exception("Failed to create execution")
            return FlextResult.fail(f"Execution creation failed: {e}")

    async def get_execution(
        self, execution_id: str,
    ) -> FlextResult[PipelineExecution | None]:
        """Get execution by ID - STRICT LOOKUP."""
        try:
            if not execution_id:
                return FlextResult.fail("Execution ID is required")

            execution = self._executions.get(execution_id)
            if execution:
                logger.debug(f"Retrieved execution: {execution_id}")
                return FlextResult.ok(execution)
            logger.debug(f"Execution not found: {execution_id}")
            return FlextResult.ok(None)

        except Exception as e:
            logger.exception(f"Failed to get execution: {execution_id}")
            return FlextResult.fail(f"Execution retrieval failed: {e}")

    async def update_execution(
        self, execution: PipelineExecution,
    ) -> FlextResult[PipelineExecution]:
        """Update execution status - STRICT VALIDATION."""
        try:
            if not execution.id:
                return FlextResult.fail("Execution ID is required")

            if execution.id not in self._executions:
                return FlextResult.fail(f"Execution {execution.id} not found")

            self._executions[execution.id] = execution
            logger.info(f"Updated execution: {execution.id} status: {execution.status}")
            return FlextResult.ok(execution)

        except Exception as e:
            logger.exception(f"Failed to update execution: {execution.id}")
            return FlextResult.fail(f"Execution update failed: {e}")

    async def list_executions(
        self,
        pipeline_id: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> FlextResult[builtins.list[PipelineExecution]]:
        """List executions with filters and pagination - EFFICIENT RETRIEVAL."""
        try:
            if limit <= 0:
                return FlextResult.fail("Limit must be positive")

            if offset < 0:
                return FlextResult.fail("Offset must be non-negative")

            executions = list(self._executions.values())

            # Apply filters
            if pipeline_id:
                executions = [e for e in executions if e.pipeline_id == pipeline_id]

            if status:
                executions = [e for e in executions if e.status == status]

            # Sort by creation time (newest first)
            executions.sort(key=lambda e: e.created_at, reverse=True)

            # Apply pagination
            paginated_executions = executions[offset : offset + limit]

            logger.debug(
                f"Listed {len(paginated_executions)} executions (total: {len(executions)})",
            )
            return FlextResult.ok(paginated_executions)

        except Exception as e:
            logger.exception("Failed to list executions")
            return FlextResult.fail(f"Execution listing failed: {e}")


# All code should use FlextInMemoryPipelineRepository directly
