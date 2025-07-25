"""Pipeline API Models - Enterprise Pipeline Management.

REFACTORED:
    Uses flext-core patterns with FlextResult and StrEnum.
Zero tolerance for duplication.
"""

from __future__ import annotations

import typing
from enum import StrEnum
from typing import Any

from pydantic import Field, field_validator

from flext_api.base import FlextAPIResponse
from flext_api.common.models import FlextValidatedRequest

if typing.TYPE_CHECKING:
    from datetime import datetime
    from uuid import UUID


class PipelineType(StrEnum):
    """Pipeline type enumeration."""

    ETL = "etl"
    ELT = "elt"
    STREAMING = "streaming"
    BATCH = "batch"
    REALTIME = "realtime"
    TRANSFORMATION = "transformation"
    EXTRACTION = "extraction"
    LOADING = "loading"


class PipelineStatus(StrEnum):
    """Pipeline status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ARCHIVED = "archived"
    FAILED = "failed"
    RUNNING = "running"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EntityStatus(StrEnum):
    """Entity status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ARCHIVED = "archived"
    FAILED = "failed"
    RUNNING = "running"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PipelineCreateRequest(FlextValidatedRequest):
    """Request model for creating a new pipeline - MATCHES ROUTES EXACTLY."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Pipeline name"
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Pipeline description"
    )
    pipeline_type: PipelineType = Field(
        default=PipelineType.ETL,
        description="Type of pipeline"
    )

    # EXACT FIELDS EXPECTED BY ROUTES
    extractor: str = Field(
        ...,
        description="Extractor plugin name"
    )
    loader: str = Field(
        ...,
        description="Loader plugin name"
    )
    transform: str | None = Field(
        default=None,
        description="Transform plugin name"
    )
    configuration: dict[str, Any] = Field(
        default_factory=dict,
        description="Pipeline configuration"
    )
    environment: str = Field(
        default="development",
        description="Pipeline environment"
    )
    schedule: dict[str, Any] | None = Field(
        default=None,
        description="Pipeline schedule configuration"
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Pipeline tags"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Pipeline metadata"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate pipeline name."""
        if not v or not v.strip():
            raise ValueError("Pipeline name cannot be empty")
        return v.strip()

    @field_validator("configuration", mode="before")
    @classmethod
    def validate_configuration(cls, v: dict[str, Any] | None) -> dict[str, Any]:
        """Ensure configuration is never None."""
        return v if v is not None else {}

    @field_validator("metadata", mode="before")
    @classmethod
    def validate_metadata(cls, v: dict[str, Any] | None) -> dict[str, Any]:
        """Ensure metadata is never None."""
        return v if v is not None else {}

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str]:
        """Ensure tags is never None."""
        return v if v is not None else []


class PipelineUpdateRequest(FlextValidatedRequest):
    """Request model for updating an existing pipeline."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Pipeline name"
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Pipeline description"
    )
    pipeline_type: PipelineType | None = Field(
        default=None,
        description="Type of pipeline"
    )
    extractor: str | None = Field(
        default=None,
        description="Extractor plugin name"
    )
    loader: str | None = Field(
        default=None,
        description="Loader plugin name"
    )
    transform: str | None = Field(
        default=None,
        description="Transform plugin name"
    )
    configuration: dict[str, Any] | None = Field(
        default=None,
        description="Pipeline configuration"
    )
    environment: str | None = Field(
        default=None,
        description="Pipeline environment"
    )
    schedule: dict[str, Any] | None = Field(
        default=None,
        description="Pipeline schedule configuration"
    )
    tags: list[str] | None = Field(
        default=None,
        description="Pipeline tags"
    )
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Pipeline metadata"
    )
    status: PipelineStatus | None = Field(
        default=None,
        description="Pipeline status"
    )


class PipelineExecutionRequest(FlextValidatedRequest):
    """Request model for executing a pipeline."""

    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Execution parameters"
    )
    scheduled_time: datetime | None = Field(
        default=None,
        description="Scheduled execution time"
    )
    priority: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Execution priority (1-10)"
    )


class PipelineResponse(FlextAPIResponse[dict[str, Any]]):
    """Response model for pipeline operations - MATCHES ROUTES EXACTLY."""

    pipeline_id: UUID = Field(..., description="Pipeline unique identifier")
    name: str = Field(..., description="Pipeline name")
    description: str | None = Field(default=None, description="Pipeline description")
    pipeline_type: PipelineType = Field(..., description="Type of pipeline")

    # EXACT FIELDS EXPECTED BY ROUTES
    extractor: str = Field(..., description="Extractor plugin name")
    loader: str = Field(..., description="Loader plugin name")
    transform: str | None = Field(default=None, description="Transform plugin name")
    configuration: dict[str, Any] = Field(default_factory=dict, description="Pipeline configuration")
    environment: str = Field(..., description="Pipeline environment")
    schedule: dict[str, Any] | None = Field(default=None, description="Pipeline schedule configuration")
    tags: list[str] = Field(default_factory=list, description="Pipeline tags")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Pipeline metadata")

    pipeline_status: PipelineStatus = Field(..., description="Pipeline status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    # Optional execution info
    last_run_at: datetime | None = Field(default=None, description="Last execution timestamp")
    run_count: int = Field(default=0, description="Total execution count")
    success_count: int = Field(default=0, description="Successful execution count")
    failure_count: int = Field(default=0, description="Failed execution count")

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.run_count == 0:
            return 0.0
        return (self.success_count / self.run_count) * 100


class PipelineListResponse(FlextAPIResponse[list[PipelineResponse]]):
    """Response model for listing pipelines."""

    total: int = Field(..., description="Total number of pipelines")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")

    @field_validator("total_pages", mode="after")
    @classmethod
    def calculate_total_pages(cls, v: int, info: Any) -> int:
        """Calculate total pages based on total and page_size."""
        if hasattr(info.data, "total") and hasattr(info.data, "page_size"):
            total: int = info.data["total"]
            page_size: int = info.data["page_size"]
            if page_size > 0:
                return int((total + page_size - 1) // page_size)
        return v


class PipelineExecutionResponse(FlextAPIResponse[dict[str, Any]]):
    """Response model for pipeline execution."""

    execution_id: UUID = Field(..., description="Execution unique identifier")
    pipeline_id: UUID = Field(..., description="Pipeline unique identifier")
    status: PipelineStatus = Field(..., description="Execution status")
    started_at: datetime = Field(..., description="Execution start time")
    completed_at: datetime | None = Field(default=None, description="Execution completion time")
    duration_seconds: float | None = Field(default=None, description="Execution duration in seconds")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Execution parameters")
    result: dict[str, Any] | None = Field(default=None, description="Execution result")
    error_message: str | None = Field(default=None, description="Error message if failed")
    logs_url: str | None = Field(default=None, description="URL to execution logs")


class PipelineStatsResponse(FlextAPIResponse[dict[str, Any]]):
    """Response model for pipeline statistics."""

    pipeline_id: UUID = Field(..., description="Pipeline unique identifier")
    total_executions: int = Field(default=0, description="Total number of executions")
    successful_executions: int = Field(default=0, description="Number of successful executions")
    failed_executions: int = Field(default=0, description="Number of failed executions")
    success_rate: float = Field(default=0.0, description="Success rate percentage")
    average_duration_seconds: float = Field(default=0.0, description="Average execution duration")
    last_execution_at: datetime | None = Field(default=None, description="Last execution timestamp")
    last_success_at: datetime | None = Field(default=None, description="Last successful execution")
    last_failure_at: datetime | None = Field(default=None, description="Last failed execution")


__all__ = [
    "EntityStatus",
    "PipelineCreateRequest",
    "PipelineExecutionRequest",
    "PipelineExecutionResponse",
    "PipelineListResponse",
    "PipelineResponse",
    "PipelineStatsResponse",
    "PipelineStatus",
    "PipelineType",
    "PipelineUpdateRequest",
]
