"""Pydantic models for the Monitoring API.

Defining data structures for health and statistics.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ComponentHealthAPI(BaseModel):
    """API model for component health status serialization."""

    healthy: bool = Field(..., description="Whether the component is healthy.")
    message: str = Field(..., description="A status message from the component.")
    metadata: dict[str, Any] = Field(
        ...,
        description="Additional metadata about the component's status.",
    )


class HealthResponse(BaseModel):
    """Represents the overall health of the system, including all its components."""

    healthy: bool = Field(..., description="The overall health status of the system.")
    components: dict[str, ComponentHealthAPI] = Field(
        ...,
        description="A dictionary of health statuses for individual components.",
    )
    timestamp: datetime = Field(
        ...,
        description="The timestamp when the health check was performed.",
    )


class SystemStatsResponse(BaseModel):
    """Represents key performance and usage statistics for the system."""

    active_pipelines: int = Field(
        ...,
        description="The number of currently active pipelines.",
    )
    total_executions: int = Field(
        ...,
        description="The total number of pipeline executions since startup.",
    )
    success_rate: float = Field(
        ...,
        description="The success rate of pipeline executions as a percentage.",
    )
    uptime_seconds: int = Field(..., description="The system uptime in seconds.")
    cpu_usage: float = Field(..., description="The current CPU usage as a percentage.")
    memory_usage: float = Field(
        ...,
        description="The current memory usage in megabytes.",
    )
    active_connections: int = Field(
        ...,
        description="The number of active client connections.",
    )
