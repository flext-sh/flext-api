"""Domain entities for FLEXT-API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the domain entities for the FLEXT API.
"""

from __future__ import annotations

from datetime import UTC
from datetime import datetime
from typing import TYPE_CHECKING
from typing import Any

from flext_core.domain.constants import ConfigDefaults

# TimestampMixin functionality already included in DomainEntity
from flext_core.domain.pydantic_base import DomainEntity
from flext_core.domain.pydantic_base import DomainEvent
from flext_core.domain.pydantic_base import Field
from flext_core.domain.types import StrEnum

if TYPE_CHECKING:
    from flext_core.domain.types import EntityId
    from flext_core.domain.types import PipelineId
    from flext_core.domain.types import PluginId
    from flext_core.domain.types import UserId


class PipelineStatus(StrEnum):
    """Pipeline execution status using StrEnum for type safety."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    RUNNING = "running"
    FAILED = "failed"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PluginType(StrEnum):
    """Plugin type enumeration using StrEnum for type safety."""

    TAP = "tap"
    TARGET = "target"
    TRANSFORM = "transform"
    UTILITY = "utility"
    CUSTOM = "custom"


class HttpMethod(StrEnum):
    """HTTP method enumeration using StrEnum for type safety."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class Pipeline(DomainEntity):
    """API Pipeline domain entity using enhanced mixins for code reduction."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=ConfigDefaults.MAX_ENTITY_NAME_LENGTH,
    )
    description: str | None = Field(
        None,
        max_length=ConfigDefaults.MAX_ERROR_MESSAGE_LENGTH,
    )
    pipeline_status: PipelineStatus = Field(
        default=PipelineStatus.ACTIVE,
        description="Pipeline status (renamed to avoid conflict with StatusMixin)",
    )
    config: dict[str, Any] = Field(default_factory=dict)

    # Relationships - using typed IDs
    owner_id: UserId | None = Field(None, description="Pipeline owner")
    project_id: EntityId | None = Field(None, description="Associated project")

    # Metrics
    last_run_at: datetime | None = None
    run_count: int = Field(default=0, ge=0)
    success_count: int = Field(default=0, ge=0)
    failure_count: int = Field(default=0, ge=0)

    # API-specific fields
    endpoint: str | None = Field(
        None,
        description="API endpoint path",
        max_length=500,
    )
    method: HttpMethod = Field(
        default=HttpMethod.GET,
        description="HTTP method",
    )
    auth_required: bool = Field(default=True, description="Authentication required")
    rate_limit: int = Field(
        default=100,
        description="Rate limit per minute",
        ge=1,
        le=10000,
    )

    @property
    def success_rate(self) -> float:
        """Calculate the success rate of the pipeline."""
        if self.run_count == 0:
            return 0.0
        return (self.success_count / self.run_count) * 100

    @property
    def is_pipeline_active(self) -> bool:
        """Check if the pipeline is active."""
        return self.pipeline_status == PipelineStatus.ACTIVE

    def record_execution(self, success: bool = True) -> None:
        """Record the execution of the pipeline."""
        self.run_count += 1
        self.last_run_at = datetime.now(UTC)
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1


class Plugin(DomainEntity):
    """API Plugin domain entity using enhanced mixins for code reduction."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=ConfigDefaults.MAX_ENTITY_NAME_LENGTH,
    )
    plugin_type: PluginType = Field(
        default=PluginType.UTILITY,
        description="Plugin type (renamed to avoid confusion)",
    )
    version: str = Field(
        default="0.7.0",
        pattern=r"^\d+\.\d+\.\d+$",
    )
    description: str | None = Field(
        None,
        max_length=ConfigDefaults.MAX_ERROR_MESSAGE_LENGTH,
    )
    plugin_config: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = Field(default=True)

    # Metadata
    author: str | None = Field(
        None,
        max_length=ConfigDefaults.MAX_ENTITY_NAME_LENGTH,
    )
    repository_url: str | None = Field(None, max_length=500)
    documentation_url: str | None = Field(None, max_length=500)

    # Validation
    validation_schema: dict[str, Any] | None = Field(default=None)
    capabilities: list[str] = Field(default_factory=list)

    # API-specific fields
    api_version: str = Field(
        default="0",
        description="API version",
    )
    endpoints: list[str] = Field(
        default_factory=list,
        description="Available endpoints",
    )
    permissions: list[str] = Field(
        default_factory=list,
        description="Required permissions",
    )

    @property
    def is_tap(self) -> bool:
        """Check if the plugin is a tap."""
        return self.plugin_type == PluginType.TAP

    @property
    def is_target(self) -> bool:
        """Check if the plugin is a target."""
        return self.plugin_type == PluginType.TARGET

    @property
    def is_transform(self) -> bool:
        """Check if the plugin is a transform."""
        return self.plugin_type == PluginType.TRANSFORM


class RequestLog(DomainEntity):
    """API Request log domain entity using enhanced mixins for code reduction."""

    method: HttpMethod = Field(..., description="HTTP method")
    path: str = Field(
        ...,
        description="Request path",
        max_length=500,
    )
    query_params: dict[str, Any] = Field(default_factory=dict)
    headers: dict[str, str] = Field(default_factory=dict)
    body: dict[str, Any] | None = None

    # Request metadata - using typed IDs
    user_id: UserId | None = Field(None, description="User making the request")
    ip_address: str | None = Field(None, max_length=45)  # IPv6 max length
    user_agent: str | None = Field(None, max_length=500)
    request_id: str | None = Field(
        None,
        max_length=ConfigDefaults.MAX_ENTITY_NAME_LENGTH,
    )

    # Response data
    status_code: int | None = Field(None, ge=100, le=599)
    response_time_ms: int | None = Field(None, ge=0)
    response_size: int | None = Field(None, ge=0)

    @property
    def was_successful(self) -> bool:
        """Check if the pipeline execution was successful.

        Returns:
            True if status code indicates success (200-299).

        """
        return self.status_code is not None and 200 <= self.status_code < 300

    @property
    def was_client_error(self) -> bool:
        """Check if the pipeline execution had a client error.

        Returns:
            True if status code indicates client error (400-499).

        """
        return self.status_code is not None and 400 <= self.status_code < 500

    @property
    def was_server_error(self) -> bool:
        """Check if the pipeline execution had a server error.

        Returns:
            True if status code indicates server error (500+).

        """
        return self.status_code is not None and self.status_code >= 500


class ResponseLog(DomainEntity):
    """API Response log domain entity using enhanced mixins for code reduction."""

    request_id: EntityId = Field(..., description="Related request ID")
    status_code: int = Field(
        ...,
        description="HTTP status code",
        ge=100,
        le=599,
    )
    headers: dict[str, str] = Field(default_factory=dict)
    body: dict[str, Any] | None = None

    # Response metadata
    response_time_ms: int = Field(
        default=0,
        description="Response time in milliseconds",
        ge=0,
    )
    content_type: str | None = Field(None, max_length=255)
    content_length: int | None = Field(None, ge=0)

    # Error information
    error_message: str | None = Field(
        None,
        max_length=ConfigDefaults.MAX_ERROR_MESSAGE_LENGTH,
    )
    error_code: str | None = Field(
        None,
        max_length=ConfigDefaults.MAX_ENTITY_NAME_LENGTH,
    )

    @property
    def is_success(self) -> bool:
        """Check if the API response indicates success.

        Returns:
            True if status code indicates success (200-299).

        """
        return 200 <= self.status_code < 300

    @property
    def is_client_error(self) -> bool:
        """Check if the API response indicates client error.

        Returns:
            True if status code indicates client error (400-499).

        """
        return 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:
        """Check if the API response indicates server error.

        Returns:
            True if status code indicates server error (500+).

        """
        return self.status_code >= 500

    @property
    def is_fast_response(self) -> bool:
        """Check if the API response was fast.

        Returns:
            True if response time was under 100ms.

        """
        return self.response_time_ms < 100


# Domain Events for API
class PipelineCreatedEvent(DomainEvent):
    """Event raised when pipeline is created."""

    pipeline_id: PipelineId
    pipeline_name: str | None = Field(default=None, description="Pipeline name")


class PipelineExecutedEvent(DomainEvent):
    """Event raised when pipeline is executed."""

    pipeline_id: PipelineId
    execution_id: EntityId
    success: bool
    duration_ms: int


class PluginRegisteredEvent(DomainEvent):
    """Event raised when plugin is registered."""

    plugin_id: PluginId
    plugin_name: str
    plugin_type: PluginType
    version: str


class ApiRequestReceivedEvent(DomainEvent):
    """Event raised when API request is received."""

    request_id: EntityId
    method: HttpMethod | None = Field(default=None, description="HTTP method")
