"""Pipeline management endpoints for FLEXT API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the pipeline management endpoints for the FLEXT API.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request
from flext_core import DomainBaseModel as APIBaseModel, EntityStatus, Field

from flext_api.dependencies import get_pipeline_service
from flext_api.models.pipeline import (
    PipelineCreateRequest,
    PipelineListResponse,
    PipelineResponse,
    PipelineType,
)

pipelines_router = APIRouter(prefix="/pipelines", tags=["pipelines"])


class PipelineListParams(APIBaseModel):
    """Parameters for listing pipelines."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    status: str | None = None
    search: str | None = None


@pipelines_router.post("")
async def create_pipeline(
    pipeline_data: PipelineCreateRequest,
    _request: Request,
) -> PipelineResponse:
    """Create pipeline endpoint."""
    try:
        pipeline_service = get_pipeline_service()

        # Create pipeline using the service to ensure it's stored
        config = pipeline_data.configuration or {}
        config.update(
            {
                "extractor": pipeline_data.extractor,
                "loader": pipeline_data.loader,
                "transform": pipeline_data.transform,
                "environment": pipeline_data.environment,
                "pipeline_type": pipeline_data.pipeline_type,
                "schedule": pipeline_data.schedule,
                "tags": pipeline_data.tags or [],
            },
        )

        pipeline_result = await pipeline_service.create_pipeline(
            name=pipeline_data.name,
            description=pipeline_data.description,
            config=config,
            owner_id=None,
            project_id=None,
        )

        if not pipeline_result.success:
            raise HTTPException(status_code=400, detail=pipeline_result.error)

        pipeline = pipeline_result.data
        if pipeline is None:
            raise HTTPException(status_code=500, detail="Pipeline creation returned None")

        return PipelineResponse(
            pipeline_id=pipeline.id,
            name=pipeline.name,
            description=pipeline.description,
            extractor=config.get("extractor", ""),
            loader=config.get("loader", ""),
            transform=config.get("transform"),
            configuration=config,
            status=EntityStatus.ACTIVE
            if pipeline.is_pipeline_active
            else EntityStatus.INACTIVE,
            pipeline_type=PipelineType(config.get("pipeline_type", "etl")),
            environment=config.get("environment", "development"),
            schedule=config.get("schedule"),
            tags=config.get("tags", []),
            created_at=pipeline.created_at,
            updated_at=pipeline.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create pipeline: {e}",
        ) from e


@pipelines_router.get("/{pipeline_id}")
async def get_pipeline(pipeline_id: str, _request: Request) -> PipelineResponse:
    """Get pipeline by ID."""
    try:
        pipeline_service = get_pipeline_service()

        # Convert string ID to UUID for service call
        try:
            uuid_id = UUID(pipeline_id)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail="Invalid pipeline ID format",
            ) from e

        pipeline_result = await pipeline_service.get_pipeline(uuid_id)

        if not pipeline_result.success:
            raise HTTPException(status_code=404, detail="Pipeline not found")

        pipeline = pipeline_result.data
        if pipeline is None:
            raise HTTPException(status_code=500, detail="Pipeline fetch returned None")

        config = pipeline.config or {}

        return PipelineResponse(
            pipeline_id=pipeline.id,
            name=pipeline.name,
            description=pipeline.description,
            extractor=config.get("extractor", ""),
            loader=config.get("loader", ""),
            transform=config.get("transform"),
            configuration=config,
            status=EntityStatus.ACTIVE
            if pipeline.is_pipeline_active
            else EntityStatus.INACTIVE,
            pipeline_type=PipelineType(config.get("pipeline_type", "etl")),
            environment=config.get("environment", "development"),
            schedule=config.get("schedule"),
            tags=config.get("tags", []),
            created_at=pipeline.created_at,
            updated_at=pipeline.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pipeline: {e}",
        ) from e


@pipelines_router.get("")
async def list_pipelines(
    params: Annotated[PipelineListParams, Query()],
    _request: Request,
) -> PipelineListResponse:
    """List pipelines with pagination."""
    try:
        pipeline_service = get_pipeline_service()

        # Calculate offset from page and page_size
        offset = (params.page - 1) * params.page_size

        pipelines_result = await pipeline_service.list_pipelines(
            limit=params.page_size,
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
                    status=EntityStatus.ACTIVE
                    if pipeline.is_pipeline_active
                    else EntityStatus.INACTIVE,
                    pipeline_type=PipelineType(config.get("pipeline_type", "etl")),
                    environment=config.get("environment", "development"),
                    schedule=config.get("schedule"),
                    tags=config.get("tags", []),
                    created_at=pipeline.created_at,
                    updated_at=pipeline.updated_at,
                ),
            )

        return PipelineListResponse(
            pipelines=pipeline_responses,
            total_count=len(pipeline_responses),
            page=params.page,
            page_size=params.page_size,
            has_next=False,  # Simple implementation for now
            has_previous=params.page > 1,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list pipelines: {e}",
        ) from e
