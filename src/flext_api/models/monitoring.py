"""Monitoring and health check API models using flext-core patterns.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides models for system health monitoring, statistics
and component status reporting.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import Field

from flext_api.base import FlextAPIResponse

# ComponentHealth now imported from flext-core as HealthStatus - no duplication
# Define our own ComponentHealth type
ComponentHealth = dict[str, Any]

if TYPE_CHECKING:
    from datetime import datetime

# ComponentHealthAPI removed - use ComponentHealth from flext_core instead


class HealthResponse(FlextAPIResponse[dict[str, Any]]):
    """Represents the overall health of the system, including all its components."""

    healthy: bool = Field(..., description="The overall health status of the system.")
    components: list[ComponentHealth] = Field(
        default_factory=list,
        description="A list of component health statuses.",
    )
    checks_performed: int = Field(
        default=0,
        description="The number of health checks performed.",
    )
    checks_passed: int = Field(
        default=0, description="The number of health checks that passed."
    )
    health_timestamp: datetime = Field(
        ..., description="The timestamp of the health check."
    )


class APIInfoResponse(FlextAPIResponse[dict[str, Any]]):
    """API service information response."""

    service: str = Field(..., description="Service name")
    service_status: str = Field(..., description="Service status")
    environment: str = Field(..., description="Environment name")
    version: str = Field(..., description="API version")


class SimpleHealthResponse(FlextAPIResponse[dict[str, Any]]):
    """Simple health check response."""

    health_status: str = Field(..., description="Health status")
    environment: str = Field(..., description="Environment name")
    debug: str = Field(..., description="Debug mode status")


class SystemStatsResponse(FlextAPIResponse[dict[str, Any]]):
    """Represents key performance and usage statistics for the system."""

    active_pipelines: int = Field(
        default=0, description="The number of currently active pipelines."
    )
    total_pipelines: int = Field(
        default=0, description="The total number of pipelines in the system."
    )
    successful_executions: int = Field(
        default=0, description="The number of successful pipeline executions."
    )
    failed_executions: int = Field(
        default=0, description="The number of failed pipeline executions."
    )
    total_executions: int = Field(
        default=0, description="The total number of pipeline executions."
    )
    active_connections: int = Field(
        default=0, description="The number of active client connections."
    )
