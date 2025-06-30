"""Pipeline management routes for FLEXT API."""


from fastapi import APIRouter, HTTPException, status
from flext_core.domain.entities import Pipeline
from flext_core.domain.value_objects import PipelineName

from flext_api.models.pipeline import (
    PipelineCreateRequest,
    PipelineExecutionRequest,
    PipelineResponse,
    PipelineStatus,
    PipelineUpdateRequest,
)

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.post("/", response_model=PipelineResponse)
async def create_pipeline(request: PipelineCreateRequest) -> PipelineResponse:
    """Create a new pipeline."""
    try:
        pipeline = Pipeline(
            name=PipelineName(request.name),
            description=request.description or "",
            created_by=request.created_by or "api_user"
        )

        return PipelineResponse(
            id=str(pipeline.pipeline_id.value),
            name=pipeline.name.value,
            description=pipeline.description,
            status="created",
            created_by=pipeline.created_by,
            created_at=pipeline.created_at,
            is_active=pipeline.is_active
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=list[PipelineResponse])
async def list_pipelines() -> list[PipelineResponse]:
    """List all pipelines."""
    # In a real implementation, this would query the database
    # For now, return empty list as demonstration
    return []


@router.get("/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(pipeline_id: str) -> PipelineResponse:
    """Get pipeline by ID."""
    # In a real implementation, this would query the database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Pipeline not found"
    )


@router.put("/{pipeline_id}", response_model=PipelineResponse)
async def update_pipeline(
    pipeline_id: str,
    request: PipelineUpdateRequest
) -> PipelineResponse:
    """Update pipeline configuration."""
    # In a real implementation, this would update the database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Pipeline not found"
    )


@router.delete("/{pipeline_id}")
async def delete_pipeline(pipeline_id: str) -> dict[str, str]:
    """Delete a pipeline."""
    # In a real implementation, this would delete from database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Pipeline not found"
    )


@router.post("/{pipeline_id}/execute")
async def execute_pipeline(
    pipeline_id: str,
    request: PipelineExecutionRequest
) -> dict[str, str]:
    """Execute a pipeline."""
    try:
        # Create a pipeline execution
        # In real implementation, this would:
        # 1. Load pipeline from database
        # 2. Create execution record
        # 3. Queue for execution
        # 4. Return execution ID

        return {
            "message": "Pipeline execution started",
            "execution_id": "exec_" + pipeline_id,
            "status": "queued"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Execution failed: {str(e)}"
        )


@router.get("/{pipeline_id}/status", response_model=PipelineStatus)
async def get_pipeline_status(pipeline_id: str) -> PipelineStatus:
    """Get pipeline execution status."""
    # In a real implementation, this would query execution status
    return PipelineStatus(
        pipeline_id=pipeline_id,
        status="idle",
        last_execution=None,
        next_execution=None
    )
