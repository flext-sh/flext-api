"""Pipeline management routes for FLEXT API using clean architecture.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides REST endpoints for pipeline management using
the application services and clean architecture patterns.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from flext_api.application.services.pipeline_service import PipelineService
from flext_api.dependencies import get_current_user
from flext_api.dependencies import get_pipeline_service
from flext_api.models.pipeline import PipelineCreateRequest
from flext_api.models.pipeline import PipelineExecutionRequest
from flext_api.models.pipeline import PipelineResponse
from flext_api.models.pipeline import PipelineUpdateRequest

# Use centralized logger from flext-observability - ELIMINATE DUPLICATION
from flext_observability.logging import get_logger

# from flext_observability import get_logger


router = APIRouter(prefix="/pipelines", tags=["pipelines"])
logger = get_logger(__name__)


@router.post("/")
async def create_pipeline(
    request: PipelineCreateRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    pipeline_service: Annotated[PipelineService, Depends(get_pipeline_service)],
) -> PipelineResponse:
    """Create a new pipeline.

    Args:
        request: The pipeline creation request.
        current_user: The current user.
        pipeline_service: The pipeline service.

    Raises:
        HTTPException: If the pipeline creation fails.

    Returns:
        The created pipeline.

    """
    try:
        result = await pipeline_service.create_pipeline(
            name=request.name,
            description=request.description,
            config=request.config or {},
            owner_id=UUID(current_user["id"]) if current_user["id"] else None,
            project_id=UUID(request.project_id) if request.project_id else None,
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error,
            )

        pipeline = result.unwrap()

        return PipelineResponse(
            id=str(pipeline.id),
            name=pipeline.name,
            description=pipeline.description,
            status=pipeline.status.value,
            created_at=pipeline.created_at.isoformat(),
            updated_at=pipeline.updated_at.isoformat() if pipeline.updated_at else None,
            config=pipeline.config,
            owner_id=str(pipeline.owner_id) if pipeline.owner_id else None,
            project_id=str(pipeline.project_id) if pipeline.project_id else None,
            metrics={
                "run_count": pipeline.run_count,
                "success_count": pipeline.success_count,
                "failure_count": pipeline.failure_count,
                "success_rate": pipeline.success_rate,
            },
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e),
        ) from e


@router.get("/")
async def list_pipelines(
    current_user: Annotated[dict, Depends(get_current_user)],
    pipeline_service: Annotated[PipelineService, Depends(get_pipeline_service)],
    project_id: str | None = None,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[PipelineResponse]:
    """List pipelines.

    Args:
        current_user: The current user.
        pipeline_service: The pipeline service.
        project_id: The project ID.
        status: The status of the pipelines.
        limit: The limit of pipelines to return.
        offset: The offset of pipelines to return.

    Returns:
        The list of pipelines.

    """
    try:
        result = await pipeline_service.list_pipelines(
            owner_id=UUID(current_user["id"]) if current_user["id"] else None,
            project_id=UUID(project_id) if project_id else None,
            status=status,
            limit=limit,
            offset=offset,
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.error,
            )

        pipelines = result.unwrap()

        return [
            PipelineResponse(
                id=str(pipeline.id),
                name=pipeline.name,
                description=pipeline.description,
                status=pipeline.status.value,
                created_at=pipeline.created_at.isoformat(),
                updated_at=(
                    pipeline.updated_at.isoformat() if pipeline.updated_at else None
                ),
                config=pipeline.config,
                owner_id=str(pipeline.owner_id) if pipeline.owner_id else None,
                project_id=str(pipeline.project_id) if pipeline.project_id else None,
                metrics={
                    "run_count": pipeline.run_count,
                    "success_count": pipeline.success_count,
                    "failure_count": pipeline.failure_count,
                    "success_rate": pipeline.success_rate,
                },
            )
            for pipeline in pipelines
        ]

    except Exception as e:
        logger.exception("Failed to list pipelines", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list pipelines",
        ) from e


@router.get("/{pipeline_id}")
async def get_pipeline(
    pipeline_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    pipeline_service: Annotated[PipelineService, Depends(get_pipeline_service)],
) -> PipelineResponse:
    try:
        result = await pipeline_service.get_pipeline(UUID(pipeline_id))

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.error,
            )

        pipeline = result.unwrap()

        return PipelineResponse(
            id=str(pipeline.id),
            name=pipeline.name,
            description=pipeline.description,
            status=pipeline.status.value,
            created_at=pipeline.created_at.isoformat(),
            updated_at=pipeline.updated_at.isoformat() if pipeline.updated_at else None,
            config=pipeline.config,
            owner_id=str(pipeline.owner_id) if pipeline.owner_id else None,
            project_id=str(pipeline.project_id) if pipeline.project_id else None,
            metrics={
                "run_count": pipeline.run_count,
                "success_count": pipeline.success_count,
                "failure_count": pipeline.failure_count,
                "success_rate": pipeline.success_rate,
            },
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid pipeline ID",
        ) from e


@router.put("/{pipeline_id}")
async def update_pipeline(
    pipeline_id: str,
    request: PipelineUpdateRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    pipeline_service: Annotated[PipelineService, Depends(get_pipeline_service)],
) -> PipelineResponse:
    try:
        result = await pipeline_service.update_pipeline(
            pipeline_id=UUID(pipeline_id),
            name=request.name,
            description=request.description,
            config=request.config,
            status=request.status,
        )

        if not result.success:
            if "not found" in result.error.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result.error,
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error,
            )

        pipeline = result.unwrap()

        return PipelineResponse(
            id=str(pipeline.id),
            name=pipeline.name,
            description=pipeline.description,
            status=pipeline.status.value,
            created_at=pipeline.created_at.isoformat(),
            updated_at=pipeline.updated_at.isoformat() if pipeline.updated_at else None,
            config=pipeline.config,
            owner_id=str(pipeline.owner_id) if pipeline.owner_id else None,
            project_id=str(pipeline.project_id) if pipeline.project_id else None,
            metrics={
                "run_count": pipeline.run_count,
                "success_count": pipeline.success_count,
                "failure_count": pipeline.failure_count,
                "success_rate": pipeline.success_rate,
            },
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid pipeline ID",
        ) from e


@router.delete("/{pipeline_id}")
async def delete_pipeline(
    pipeline_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    pipeline_service: Annotated[PipelineService, Depends(get_pipeline_service)],
) -> dict[str, str]:
    try:
        result = await pipeline_service.delete_pipeline(UUID(pipeline_id))

        if not result.success:
            if "not found" in result.error.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result.error,
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error,
            )

        return {
            "message": "Pipeline deleted successfully",
            "pipeline_id": pipeline_id,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid pipeline ID",
        ) from e


@router.post("/{pipeline_id}/execute")
async def execute_pipeline(
    pipeline_id: str,
    request: PipelineExecutionRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    pipeline_service: Annotated[PipelineService, Depends(get_pipeline_service)],
) -> dict[str, str]:
    try:
        # First, verify pipeline exists
        pipeline_result = await pipeline_service.get_pipeline(UUID(pipeline_id))

        if not pipeline_result.success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=pipeline_result.error,
            )

        # TODO: Implement actual pipeline execution
        # This would integrate with flext-meltano or execution engine

        # For now, return mock execution response
        execution_id = f"exec_{pipeline_id}_{hash(current_user['id'])}"

        logger.info(
            "Pipeline execution started",
            pipeline_id=pipeline_id,
            execution_id=execution_id,
            user_id=current_user["id"],
        )

        return {
            "message": "Pipeline execution started",
            "execution_id": execution_id,
            "status": "queued",
            "pipeline_id": pipeline_id,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid pipeline ID",
        ) from e
    except Exception as e:
        logger.exception(
            "Pipeline execution failed",
            pipeline_id=pipeline_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Pipeline execution failed",
        ) from e


@router.get("/{pipeline_id}/status")
async def get_pipeline_status(
    pipeline_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
    pipeline_service: Annotated[PipelineService, Depends(get_pipeline_service)],
) -> dict[str, str]:
    try:
        # Verify pipeline exists
        pipeline_result = await pipeline_service.get_pipeline(UUID(pipeline_id))

        if not pipeline_result.success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=pipeline_result.error,
            )

        pipeline = pipeline_result.unwrap()

        # TODO: Implement actual status checking
        # This would query execution history and current status

        return {
            "pipeline_id": pipeline_id,
            "status": pipeline.status.value,
            "last_run_at": (
                pipeline.last_run_at.isoformat() if pipeline.last_run_at else None
            ),
            "run_count": str(pipeline.run_count),
            "success_count": str(pipeline.success_count),
            "failure_count": str(pipeline.failure_count),
            "success_rate": str(pipeline.success_rate),
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid pipeline ID",
        ) from e
