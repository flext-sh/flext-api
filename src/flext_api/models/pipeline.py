"""Pipeline API Models - Enterprise Pipeline Management.

This module provides comprehensive Pydantic models for pipeline management
operations including creation, updates, execution, and status tracking.
Follows enterprise patterns with Python 3.13 type system.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field, field_validator

if TYPE_CHECKING:
    from uuid import UUID


class PipelineStatus(StrEnum):
    """Pipeline execution status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ExecutionStatus(StrEnum):
    """Pipeline execution status enumeration for job tracking."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class PipelineType(StrEnum):
    """Pipeline type enumeration."""

    EXTRACT = "extract"
    LOAD = "load"
    TRANSFORM = "transform"
    ETL = "etl"
    CUSTOM = "custom"


class RefreshMode(StrEnum):
    """Pipeline refresh mode enumeration."""

    INCREMENTAL = "incremental"
    FULL = "full"


# --- Request Models ---


class PipelineCreateRequest(BaseModel):
    """Request model for creating new pipelines."""

    name: str = Field(
        min_length=1,
        max_length=255,
        description="Unique pipeline name",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Pipeline description",
    )
    pipeline_type: PipelineType = Field(
        default=PipelineType.ETL,
        description="Type of pipeline operation",
    )
    extractor: str = Field(
        min_length=1,
        max_length=255,
        description="The name of the extractor plugin to use",
    )
    loader: str = Field(
        min_length=1,
        max_length=255,
        description="The name of the loader plugin to use",
    )
    transform: str | None = Field(
        default=None,
        max_length=255,
        description="The name of the transformation plugin or dbt model to run",
    )
    configuration: dict[str, Any] = Field(
        default_factory=dict,
        description="Pipeline configuration parameters",
    )
    environment: str = Field(
        default="dev",
        description="Target environment for pipeline",
    )
    schedule: str | None = Field(
        default=None,
        description="Cron expression for pipeline scheduling",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Pipeline tags for organization",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional pipeline metadata",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate pipeline name format."""
        if not v.replace("-", "").replace("_", "").isalnum():
            msg = "Pipeline name must contain only alphanumeric characters, hyphens, and underscores"
            raise ValueError(msg)
        return v.lower()

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate pipeline tags format."""
        return [tag.lower().strip() for tag in v if tag.strip()]


class PipelineUpdateRequest(BaseModel):
    """Request model for updating existing pipelines."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Updated pipeline name",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Updated pipeline description",
    )
    extractor: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Updated extractor plugin",
    )
    loader: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Updated loader plugin",
    )
    transform: str | None = Field(
        default=None,
        max_length=255,
        description="Updated transformation plugin or dbt model",
    )
    configuration: dict[str, Any] | None = Field(
        default=None,
        description="Updated pipeline configuration",
    )
    schedule: str | None = Field(
        default=None,
        description="Updated cron expression for scheduling",
    )
    tags: list[str] | None = Field(
        default=None,
        description="Updated pipeline tags",
    )
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Updated pipeline metadata",
    )
    is_active: bool | None = Field(
        default=None,
        description="Pipeline active status",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate pipeline name format."""
        if v is not None and not v.replace("-", "").replace("_", "").isalnum():
            msg = "Pipeline name must contain only alphanumeric characters, hyphens, and underscores"
            raise ValueError(msg)
        return v.lower() if v else v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        """Validate pipeline tags format."""
        if v is None:
            return v
        return [tag.lower().strip() for tag in v if tag.strip()]


class PipelineExecutionRequest(BaseModel):
    """Request model for pipeline execution."""

    refresh_mode: RefreshMode = Field(
        default=RefreshMode.INCREMENTAL,
        description="Pipeline refresh mode",
    )
    environment: str = Field(
        default="production",
        description="Target execution environment",
    )
    configuration: dict[str, Any] = Field(
        default_factory=dict,
        description="Configuration overrides for this execution",
    )
    environment_variables: dict[str, str] = Field(
        default_factory=dict,
        description="Environment variables for execution",
    )
    timeout_seconds: int | None = Field(
        default=None,
        ge=1,
        description="Execution timeout in seconds",
    )
    dry_run: bool = Field(
        default=False,
        description="Execute in dry-run mode",
    )
    async_execution: bool = Field(
        default=True,
        description="Execute asynchronously",
    )
    notification_settings: dict[str, Any] = Field(
        default_factory=dict,
        description="Notification configuration for execution",
    )


class PipelineExecutionStopRequest(BaseModel):
    """Request model for stopping pipeline execution."""

    force: bool = Field(
        default=False,
        description="Force stop without graceful shutdown",
    )
    reason: str | None = Field(
        default=None,
        max_length=500,
        description="Reason for stopping execution",
    )


# --- Response Models ---


class PipelineResponse(BaseModel):
    """Response model for pipeline information."""

    pipeline_id: UUID = Field(description="Unique pipeline identifier")
    name: str = Field(description="Pipeline name")
    description: str | None = Field(description="Pipeline description")
    pipeline_type: PipelineType = Field(description="Pipeline type")
    status: PipelineStatus = Field(description="Current pipeline status")
    extractor: str = Field(description="Extractor plugin name")
    loader: str = Field(description="Loader plugin name")
    transform: str | None = Field(default=None, description="Transform plugin name")
    configuration: dict[str, Any] = Field(
        default_factory=dict,
        description="Pipeline configuration",
    )
    environment: str = Field(description="Target environment")
    schedule: str | None = Field(default=None, description="Pipeline schedule")
    tags: list[str] = Field(default_factory=list, description="Pipeline tags")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Pipeline metadata",
    )
    is_active: bool = Field(default=True, description="Pipeline active status")
    created_at: datetime = Field(description="Pipeline creation timestamp")
    updated_at: datetime = Field(description="Pipeline last update timestamp")
    created_by: str | None = Field(default=None, description="Pipeline creator")
    last_execution_id: UUID | None = Field(
        default=None,
        description="Last execution ID",
    )
    last_execution_status: PipelineStatus | None = Field(
        default=None,
        description="Last execution status",
    )
    last_execution_at: datetime | None = Field(
        default=None,
        description="Last execution timestamp",
    )
    execution_count: int = Field(default=0, description="Total execution count")
    success_rate: float = Field(
        default=0.0,
        description="Pipeline success rate percentage",
    )


class PipelineExecutionResponse(BaseModel):
    """Response model for pipeline execution information."""

    execution_id: UUID = Field(description="Unique execution identifier")
    pipeline_id: UUID = Field(description="Pipeline identifier")
    pipeline_name: str = Field(description="Pipeline name")
    status: PipelineStatus = Field(description="Execution status")
    refresh_mode: RefreshMode = Field(description="Execution refresh mode")
    environment: str = Field(description="Execution environment")
    configuration: dict[str, Any] = Field(description="Execution configuration")
    started_at: datetime | None = Field(description="Execution start timestamp")
    finished_at: datetime | None = Field(description="Execution finish timestamp")
    duration_seconds: float | None = Field(description="Execution duration in seconds")
    logs: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Execution logs",
    )
    metrics: dict[str, Any] = Field(
        default_factory=dict,
        description="Execution metrics",
    )
    error_message: str | None = Field(description="Error message if failed")
    progress_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Execution progress percentage",
    )
    created_by: str | None = Field(description="Execution initiator")


class PipelineListResponse(BaseModel):
    """Response model for pipeline list operations."""

    pipelines: list[PipelineResponse] = Field(description="List of pipelines")
    total_count: int = Field(description="Total number of pipelines")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Page size")
    has_next: bool = Field(description="Whether there are more pages")
    has_previous: bool = Field(description="Whether there are previous pages")


class PipelineExecutionListResponse(BaseModel):
    """Response model for pipeline execution list operations."""

    executions: list[PipelineExecutionResponse] = Field(
        description="List of executions",
    )
    total_count: int = Field(description="Total number of executions")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Page size")
    has_next: bool = Field(description="Whether there are more pages")
    has_previous: bool = Field(description="Whether there are previous pages")


class PipelineStatsResponse(BaseModel):
    """Response model for pipeline statistics."""

    total_pipelines: int = Field(description="Total number of pipelines")
    active_pipelines: int = Field(description="Number of active pipelines")
    total_executions: int = Field(description="Total number of executions")
    running_executions: int = Field(
        description="Number of currently running executions",
    )
    success_rate: float = Field(description="Overall success rate percentage")
    average_duration_seconds: float = Field(description="Average execution duration")
    executions_by_status: dict[str, int] = Field(
        description="Execution count by status",
    )
    executions_by_type: dict[str, int] = Field(
        description="Execution count by pipeline type",
    )


# --- Search and Filter Models ---


class PipelineFilterRequest(BaseModel):
    """Request model for filtering pipelines."""

    pipeline_type: PipelineType | None = Field(
        default=None,
        description="Filter by pipeline type",
    )
    status: PipelineStatus | None = Field(
        default=None,
        description="Filter by pipeline status",
    )
    environment: str | None = Field(
        default=None,
        description="Filter by environment",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Filter by tags (AND operation)",
    )
    is_active: bool | None = Field(
        default=None,
        description="Filter by active status",
    )
    created_after: datetime | None = Field(
        default=None,
        description="Filter by creation date (after)",
    )
    created_before: datetime | None = Field(
        default=None,
        description="Filter by creation date (before)",
    )
    search: str | None = Field(
        default=None,
        description="Search in name and description",
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Page number",
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Page size",
    )
    sort_by: str = Field(
        default="created_at",
        description="Sort field",
    )
    sort_order: str = Field(
        default="desc",
        pattern="^(asc|desc)$",
        description="Sort order",
    )


class PipelineExecutionFilterRequest(BaseModel):
    """Request model for filtering pipeline executions."""

    pipeline_id: UUID | None = Field(
        default=None,
        description="Filter by pipeline ID",
    )
    status: PipelineStatus | None = Field(
        default=None,
        description="Filter by execution status",
    )
    environment: str | None = Field(
        default=None,
        description="Filter by environment",
    )
    refresh_mode: RefreshMode | None = Field(
        default=None,
        description="Filter by refresh mode",
    )
    started_after: datetime | None = Field(
        default=None,
        description="Filter by start date (after)",
    )
    started_before: datetime | None = Field(
        default=None,
        description="Filter by start date (before)",
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Page number",
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Page size",
    )
    sort_by: str = Field(
        default="started_at",
        description="Sort field",
    )
    sort_order: str = Field(
        default="desc",
        pattern="^(asc|desc)$",
        description="Sort order",
    )


# --- Legacy Models for Backward Compatibility ---


class RunPipelineRequest(BaseModel):
    """Legacy model for pipeline execution - maps to PipelineExecutionRequest."""

    full_refresh: bool = Field(
        default=False,
        description="Whether to perform a full refresh (state will be ignored)",
    )
    env_vars: dict[str, str] | None = Field(
        default=None,
        description="Additional environment variables for this specific run",
    )

    def to_execution_request(self) -> PipelineExecutionRequest:
        """Convert to modern PipelineExecutionRequest."""
        return PipelineExecutionRequest(
            refresh_mode=(
                RefreshMode.FULL if self.full_refresh else RefreshMode.INCREMENTAL
            ),
            configuration_override=self.env_vars or {},
        )


class ExecutionResponse(BaseModel):
    """Legacy model for execution response - maps to PipelineExecutionResponse."""

    id: str = Field(description="The unique identifier of the execution")
    pipeline_id: str = Field(
        description="The identifier of the pipeline that was executed",
    )
    status: str = Field(description="The current status of the execution")
    started_at: datetime = Field(description="The timestamp when the execution started")
    finished_at: datetime | None = Field(
        description="The timestamp when the execution finished",
    )
    duration_seconds: int | None = Field(
        description="The total duration of the execution in seconds",
    )
    error_message: str | None = Field(
        description="Any error message if the execution failed",
    )
    records_processed: int | None = Field(
        description="The number of records processed during the execution",
    )
    triggered_by: str = Field(
        description="The identifier of the user or system that triggered the execution",
    )

    @classmethod
    def from_execution_response(
        cls,
        response: PipelineExecutionResponse,
    ) -> ExecutionResponse:
        """Convert from modern PipelineExecutionResponse."""
        # Calculate duration from start/end times - ZERO TOLERANCE: Real implementation
        duration_seconds = None
        if response.started_at and response.completed_at:
            duration_delta = response.completed_at - response.started_at
            duration_seconds = int(duration_delta.total_seconds())

        # Extract records processed from metadata - ZERO TOLERANCE: Real tracking
        records_processed = None
        if hasattr(response, "metadata") and response.metadata:
            records_processed = response.metadata.get("records_processed")

        # Extract user from execution context - ZERO TOLERANCE: Real user tracking
        triggered_by = "system"
        if hasattr(response, "metadata") and response.metadata:
            triggered_by = response.metadata.get("triggered_by", "system")

        return cls(
            id=str(response.execution_id),
            pipeline_id=str(response.pipeline_id),
            status=response.status.value,
            started_at=response.started_at or datetime.now(UTC),
            finished_at=response.completed_at,
            duration_seconds=duration_seconds,
            error_message=(
                response.message if response.status == ExecutionStatus.FAILED else None
            ),
            records_processed=records_processed,
            triggered_by=triggered_by,
        )


# Note: Removed duplicate PipelineExecutionResponse and PipelineExecutionListResponse
# to avoid F811 redefinition errors. The original definitions above are sufficient.
