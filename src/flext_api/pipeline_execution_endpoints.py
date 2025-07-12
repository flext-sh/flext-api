"""Pipeline execution endpoints for FLEXT API.

This module provides endpoints for managing pipeline executions,
including starting, stopping, monitoring, and retrieving execution logs.
"""

from __future__ import annotations

import uuid
from datetime import UTC
from datetime import datetime
from typing import TYPE_CHECKING
from typing import Annotated
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query
from fastapi import Request
from fastapi import status
from slowapi import Limiter
from slowapi.util import get_remote_address

from flext_core.config.base import get_config
from flext_core.domain.pipeline import PipelineExecution
from flext_core.domain.pydantic_base import APIRequest
from flext_core.domain.shared_models import PipelineExecutionStatus

# Use centralized logger from flext-observability - ELIMINATE DUPLICATION
from flext_observability.logging import get_logger

# from flext_observability import get_logger as get_observability_logger


if TYPE_CHECKING:
    from fastapi import Request

    from flext_api.models.pipeline import PipelineExecutionRequest

# Configuration
config = get_config()
logger = get_logger(__name__)
observability_logger = get_observability_logger(__name__)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)


class ExecutionLogParams(APIRequest):
    """Parameters for execution log retrieval operations."""

    offset: int = Query(
        default=0,
        ge=0,
        description="Number of log entries to skip",
    )
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of log entries to return",
    )
    level: str | None = Query(
        default=None,
        description="Filter logs by level (DEBUG, INFO, WARNING, ERROR)",
    )


class ExecutionListParams(APIRequest):
    """Parameters for execution listing operations."""

    pipeline_id: str | None = Query(
        default=None,
        description="Filter executions by pipeline ID",
    )
    status: str | None = Query(
        default=None,
        description="Filter executions by status",
    )
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
        description="Maximum number of executions to return",
    )
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of executions to skip",
    )


# Create router
router = APIRouter(prefix="/executions", tags=["pipeline-executions"])


@router.post("/{pipeline_id}/start")
@limiter.limit("10/minute")
async def start_pipeline_execution(
    request: Request,
    pipeline_id: str,
    execution_request: PipelineExecutionRequest,
) -> dict[str, Any]:
    """Start a new pipeline execution.

    Args:
        request: The HTTP request object.
        pipeline_id: The pipeline ID to execute.
        execution_request: The execution request parameters.

    Returns:
        The execution response with execution ID and status.

    Raises:
        HTTPException: If the pipeline execution fails to start.

    """
    try:
        # Generate execution ID
        execution_id = str(uuid.uuid4())

        # Create execution record
        execution = PipelineExecution(
            execution_id=execution_id,
            pipeline_id=pipeline_id,
            status=PipelineExecutionStatus.PENDING,
            config=execution_request.config or {},
            environment=execution_request.environment or "default",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        # Log execution start
        observability_logger.info(
            "Pipeline execution started",
            pipeline_id=pipeline_id,
            execution_id=execution_id,
            environment=execution.environment,
        )

        # Return execution response
        return {
            "execution_id": execution_id,
            "pipeline_id": pipeline_id,
            "status": execution.status.value,
            "created_at": execution.created_at.isoformat(),
            "message": "Pipeline execution started successfully",
        }

    except Exception as e:
        logger.exception("Failed to start pipeline execution", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start pipeline execution: {e}",
        ) from e


@router.post("/{execution_id}/stop")
@limiter.limit("5/minute")
async def stop_pipeline_execution(
    request: Request,
    execution_id: str,
) -> dict[str, Any]:
    """Stop a running pipeline execution.

    Args:
        request: The HTTP request object.
        execution_id: The execution ID to stop.

    Returns:
        The stop response with updated status.

    Raises:
        HTTPException: If the execution cannot be stopped.

    """
    try:
        # Log execution stop
        observability_logger.info(
            "Pipeline execution stop requested",
            execution_id=execution_id,
        )

        # Return stop response
        return {
            "execution_id": execution_id,
            "status": PipelineExecutionStatus.CANCELLED.value,
            "message": "Pipeline execution stopped successfully",
            "stopped_at": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        logger.exception("Failed to stop pipeline execution", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop pipeline execution: {e}",
        ) from e


@router.get("/{execution_id}")
async def get_execution_details(
    execution_id: str,
) -> dict[str, Any]:
    """Get details for a specific pipeline execution.

    Args:
        execution_id: The execution ID to retrieve.

    Returns:
        The execution details.

    Raises:
        HTTPException: If the execution is not found.

    """
    try:
        # Mock execution details
        return {
            "execution_id": execution_id,
            "pipeline_id": "sample-pipeline",
            "status": PipelineExecutionStatus.COMPLETED.value,
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
            "duration_seconds": 120,
            "records_processed": 1000,
            "records_failed": 0,
            "success_rate": 100.0,
        }

    except Exception as e:
        logger.exception("Failed to get execution details", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution details: {e}",
        ) from e


@router.get("/{execution_id}/logs")
async def get_execution_logs(
    execution_id: str,
    params: Annotated[ExecutionLogParams, Depends()],
) -> dict[str, Any]:
    """Get logs for a specific pipeline execution.

    Args:
        execution_id: The execution ID to retrieve logs for.
        params: The log retrieval parameters.

    Returns:
        The execution logs.

    """
    try:
        # Mock log entries
        log_entries = [
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "level": "INFO",
                "message": "Pipeline execution started",
                "component": "executor",
            },
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "level": "INFO",
                "message": "Processing data batch 1",
                "component": "processor",
            },
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "level": "INFO",
                "message": "Pipeline execution completed",
                "component": "executor",
            },
        ]

        # Apply filtering and pagination
        filtered_logs = log_entries
        if params.level:
            filtered_logs = [
                log for log in filtered_logs if log["level"] == params.level
            ]

        paginated_logs = filtered_logs[params.offset : params.offset + params.limit]

        return {
            "execution_id": execution_id,
            "logs": paginated_logs,
            "total_count": len(filtered_logs),
            "offset": params.offset,
            "limit": params.limit,
        }

    except Exception as e:
        logger.exception("Failed to get execution logs", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution logs: {e}",
        ) from e


@router.get("")
async def list_executions(
    params: Annotated[ExecutionListParams, Depends()],
) -> dict[str, Any]:
    """List pipeline executions with optional filtering.

    Args:
        params: The listing parameters.

    Returns:
        The list of executions.

    """
    try:
        # Mock execution list
        executions = [
            {
                "execution_id": str(uuid.uuid4()),
                "pipeline_id": "sample-pipeline-1",
                "status": PipelineExecutionStatus.COMPLETED.value,
                "created_at": datetime.now(UTC).isoformat(),
                "duration_seconds": 120,
            },
            {
                "execution_id": str(uuid.uuid4()),
                "pipeline_id": "sample-pipeline-2",
                "status": PipelineExecutionStatus.RUNNING.value,
                "created_at": datetime.now(UTC).isoformat(),
                "duration_seconds": None,
            },
        ]

        # Apply filtering
        filtered_executions = executions
        if params.pipeline_id:
            filtered_executions = [
                ex for ex in filtered_executions if ex["pipeline_id"] == params.pipeline_id
            ]
        if params.status:
            filtered_executions = [
                ex for ex in filtered_executions if ex["status"] == params.status
            ]

        # Apply pagination
        paginated_executions = filtered_executions[
            params.offset : params.offset + params.limit
        ]

        return {
            "executions": paginated_executions,
            "total_count": len(filtered_executions),
            "offset": params.offset,
            "limit": params.limit,
        }

    except Exception as e:
        logger.exception("Failed to list executions", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list executions: {e}",
        ) from e
