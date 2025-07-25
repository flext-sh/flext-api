"""Pipeline management endpoints for FLEXT API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the pipeline management endpoints for the FLEXT API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import Field

from flext_api import get_logger
from flext_api.base import FlextApiBaseRequest
from flext_api.common import (
    ensure_service_available,
    handle_api_exceptions,
    validate_uuid,
)
from flext_api.dependencies import get_flext_pipeline_service
from flext_api.models.pipeline import (
    EntityStatus,
    PipelineCreateRequest,
    PipelineListResponse,
    PipelineResponse,
    PipelineStatus,
    PipelineType,
)

if TYPE_CHECKING:
    from flext_core import FlextResult

# Create logger using flext-core get_logger function
logger = get_logger(__name__)

pipelines_router = APIRouter(prefix="/api/v1/pipelines", tags=["pipelines"])


class FlextPipelineListParams(FlextApiBaseRequest):
    """Parameters for listing pipelines."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    status: str | None = None
    search: str | None = None


@pipelines_router.post("")
async def create_pipeline(request: PipelineCreateRequest) -> FlextResult[Any]:
    """Create pipeline endpoint."""
    try:
        pipeline_service = get_flext_pipeline_service()
        ensure_service_available(pipeline_service, "Pipeline service")

        # Create pipeline using the service to ensure it's stored
        config = request.configuration or {}
        config.update(
            {
                "extractor": request.extractor,
                "loader": request.loader,
                "transform": request.transform,
                "environment": request.environment,
                "pipeline_type": request.pipeline_type,
                "schedule": request.schedule,
                "tags": request.tags or [],
            },
        )

        pipeline_result = await pipeline_service.create_pipeline(
            name=request.name,
            description=request.description,
            config=config,
            owner_id=None,
            project_id=None,
        )

        if not pipeline_result.success:
            raise HTTPException(status_code=400, detail=pipeline_result.error)

        pipeline = pipeline_result.data
        if pipeline is None:
            raise HTTPException(
                status_code=500,
                detail="Pipeline creation returned None",
            )

        response = PipelineResponse(
            pipeline_id=pipeline.id,
            name=pipeline.name,
            description=pipeline.description,
            extractor=config.get("extractor", ""),
            loader=config.get("loader", ""),
            transform=config.get("transform"),
            configuration=config,
            pipeline_status=PipelineStatus.ACTIVE
            if pipeline.is_pipeline_active
            else PipelineStatus.INACTIVE,
            pipeline_type=PipelineType(config.get("pipeline_type", "etl")),
            environment=config.get("environment", "development"),
            schedule=config.get("schedule"),
            tags=config.get("tags", []),
            created_at=pipeline.created_at,
            updated_at=pipeline.updated_at,
        )

        from flext_core import FlextResult
        return FlextResult.ok(response)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to create pipeline")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create pipeline: {e}",
        ) from e


@pipelines_router.get("/{pipeline_id}")
@handle_api_exceptions("get pipeline")
async def get_pipeline(pipeline_id: str, _request: Request) -> FlextResult[PipelineResponse]:
    """Get pipeline by ID."""
    pipeline_service = get_flext_pipeline_service()
    ensure_service_available(pipeline_service, "Pipeline service")

    # Convert string ID to UUID for service call
    uuid_id = validate_uuid(pipeline_id, "pipeline ID")

    pipeline_result = await pipeline_service.get_pipeline(uuid_id)

    if not pipeline_result.success:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    pipeline = pipeline_result.data
    if pipeline is None:
        raise HTTPException(status_code=500, detail="Pipeline fetch returned None")

    config = pipeline.config or {}

    response = PipelineResponse(
        pipeline_id=pipeline.id,
        name=pipeline.name,
        description=pipeline.description,
        extractor=config.get("extractor", ""),
        loader=config.get("loader", ""),
        transform=config.get("transform"),
        configuration=config,
        pipeline_status=PipelineStatus.ACTIVE
        if pipeline.is_pipeline_active
        else PipelineStatus.INACTIVE,
        pipeline_type=PipelineType(config.get("pipeline_type", "etl")),
        environment=config.get("environment", "development"),
        schedule=config.get("schedule"),
        tags=config.get("tags", []),
        created_at=pipeline.created_at,
        updated_at=pipeline.updated_at,
    )

    from flext_core import FlextResult
    return FlextResult.ok(response)

    # Exception handling now done by @handle_api_exceptions decorator


@pipelines_router.get("")
@handle_api_exceptions("list pipelines")
async def list_pipelines(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    status: Annotated[str | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
) -> FlextResult[dict[str, Any]]:
    """List pipelines with pagination."""
    pipeline_service = get_flext_pipeline_service()
    ensure_service_available(pipeline_service, "Pipeline service")

    # Calculate offset from page and page_size
    offset = (page - 1) * page_size

    pipelines_result = await pipeline_service.list_pipelines(
        limit=page_size,
        offset=offset,
    )

    if not pipelines_result.success:
        raise HTTPException(status_code=500, detail=pipelines_result.error)

    pipelines = pipelines_result.data
    if pipelines is None:
        raise HTTPException(status_code=500, detail="Pipeline list returned None")

    # Convert pipelines to response format
    pipeline_responses = []
    for pipeline in pipelines:
        config = pipeline.config or {}
        pipeline_responses.append(
            PipelineResponse(
                pipeline_id=pipeline.id,
                name=pipeline.name,
                description=pipeline.description,
                extractor=config.get("extractor", ""),
                loader=config.get("loader", ""),
                transform=config.get("transform"),
                configuration=config,
                pipeline_status=PipelineStatus.ACTIVE
                if pipeline.is_pipeline_active
                else PipelineStatus.INACTIVE,
                pipeline_type=PipelineType(config.get("pipeline_type", "etl")),
                environment=config.get("environment", "development"),
                schedule=config.get("schedule"),
                tags=config.get("tags", []),
                created_at=pipeline.created_at,
                updated_at=pipeline.updated_at,
            )
        )

    response = {
        "pipelines": pipeline_responses,
        "total_count": len(pipeline_responses),
        "page": page,
        "page_size": page_size,
        "has_next": False,  # Simple implementation for now
        "has_previous": page > 1,
    }

    from flext_core import FlextResult
    return FlextResult.ok(response)

    # Exception handling now done by @handle_api_exceptions decorator


# Rebuild models to resolve forward references
PipelineListResponse.model_rebuild()
PipelineResponse.model_rebuild()
