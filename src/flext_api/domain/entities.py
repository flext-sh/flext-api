"""Domain entities for FLEXT-API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

REFACTORED: Uses flext-core domain entities - NO duplication.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

# Use flext-core domain entities - NO duplication
from flext_core import (
    APIResponse,
    ConfigDefaults,
    DomainEntity,
    EntityId,
    Field,
    Pipeline,
    PipelineExecution,
    PipelineId,
    PluginId,
    PluginMetadata,
    PluginType,
    UserId,
)
from pydantic import field_validator

from flext_api.domain.events import (
    PipelineCreatedEvent,
    PipelineExecutedEvent,
    PluginRegisteredEvent,
)

# Export flext-core entities for API usage - NO DUPLICATION
# Type aliases for backward compatibility
PipelineEntity = Pipeline  # Use flext-core Pipeline aggregate
ExecutionEntity = PipelineExecution  # Use flext-core PipelineExecution
PluginEntity = PluginMetadata  # Use flext-core PluginMetadata


# PluginType already imported from flext-core - NO duplication needed


class HttpMethod(StrEnum):
    """HTTP method enumeration using StrEnum for type safety."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class PipelineStatus(StrEnum):
    """Pipeline status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ARCHIVED = "archived"
    FAILED = "failed"
    RUNNING = "running"
    SCHEDULED = "scheduled"


# Pipeline and Plugin are imported from flext-core - NO duplication
# Only API-specific entities are defined here


class APIPipeline(DomainEntity):
    """API Pipeline domain entity using enhanced mixins for code reduction."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=ConfigDefaults.MAX_ENTITY_NAME_LENGTH,
    )
    description: str | None = Field(
        default=None,
        max_length=ConfigDefaults.MAX_ERROR_MESSAGE_LENGTH,
    )
    pipeline_status: PipelineStatus = Field(
        default=PipelineStatus.ACTIVE,
        description="Pipeline status (renamed to avoid conflict with StatusMixin)",
    )
    config: dict[str, Any] = Field(default_factory=dict)

    # Timestamps
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships - using typed IDs
    owner_id: UserId | None = Field(default=None, description="Pipeline owner")
    project_id: EntityId | None = Field(default=None, description="Associated project")

    # Metrics
    last_run_at: datetime | None = None
    run_count: int = Field(default=0, ge=0)
    success_count: int = Field(default=0, ge=0)
    failure_count: int = Field(default=0, ge=0)

    # API-specific fields
    endpoint: str | None = Field(
        default=None,
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

    def record_execution(self, *, success: bool = True) -> None:
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
        default=None,
        max_length=ConfigDefaults.MAX_ERROR_MESSAGE_LENGTH,
    )
    plugin_config: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = Field(default=True)

    @field_validator("plugin_config", mode="before")
    @classmethod
    def validate_plugin_config(cls, v: dict[str, object] | None) -> dict[str, object]:
        """Ensure plugin_config is never None."""
        return v if v is not None else {}

    # Metadata
    author: str | None = Field(
        default=None,
        max_length=ConfigDefaults.MAX_ENTITY_NAME_LENGTH,
    )
    repository_url: str | None = Field(default=None, max_length=500)
    documentation_url: str | None = Field(default=None, max_length=500)

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
    def is_extractor(self) -> bool:
        """Check if the plugin is an extractor (formerly tap)."""
        return self.plugin_type == PluginType.EXTRACTOR

    @property
    def is_loader(self) -> bool:
        """Check if the plugin is a loader (formerly target)."""
        return self.plugin_type == PluginType.LOADER

    @property
    def is_transformer(self) -> bool:
        """Check if the plugin is a transformer (formerly transform)."""
        return self.plugin_type == PluginType.TRANSFORMER

    # Backward compatibility aliases (deprecated)
    @property
    def is_tap(self) -> bool:
        """Check if the plugin is a tap (deprecated, use is_extractor)."""
        return self.plugin_type == PluginType.EXTRACTOR

    @property
    def is_target(self) -> bool:
        """Check if the plugin is a target (deprecated, use is_loader)."""
        return self.plugin_type == PluginType.LOADER

    @property
    def is_transform(self) -> bool:
        """Check if the plugin is a transform (deprecated, use is_transformer)."""
        return self.plugin_type == PluginType.TRANSFORMER


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
    user_id: UserId | None = Field(default=None, description="User making the request")
    ip_address: str | None = Field(default=None, max_length=45)  # IPv6 max length
    user_agent: str | None = Field(default=None, max_length=500)
    request_id: str | None = Field(
        default=None,
        max_length=ConfigDefaults.MAX_ENTITY_NAME_LENGTH,
    )

    # Response data
    status_code: int | None = Field(default=None, ge=100, le=599)
    response_time_ms: int | None = Field(default=None, ge=0)
    response_size: int | None = Field(default=None, ge=0)

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
    content_type: str | None = Field(default=None, max_length=255)
    content_length: int | None = Field(default=None, ge=0)

    # Error information
    error_message: str | None = Field(
        default=None,
        max_length=ConfigDefaults.MAX_ERROR_MESSAGE_LENGTH,
    )
    error_code: str | None = Field(
        default=None,
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


# Events imported at top to avoid E402


class APIRequest(DomainEntity):
    """API Request domain entity for tracking and auditing API requests."""

    # Request identification
    request_id: str = Field(..., description="Unique request identifier")
    endpoint: str = Field(..., description="API endpoint being accessed")
    method: str = Field(..., description="HTTP method (GET, POST, etc.)")

    # Request metadata
    headers: dict[str, str] = Field(default_factory=dict, description="Request headers")
    query_params: dict[str, str] = Field(
        default_factory=dict,
        description="Query parameters",
    )
    path_params: dict[str, str] = Field(
        default_factory=dict,
        description="Path parameters",
    )

    # Request payload
    body: dict[str, Any] | None = Field(default=None, description="Request body data")
    content_type: str | None = Field(
        default=None,
        description="Content type of request",
    )

    # Client information
    client_ip: str | None = Field(default=None, description="Client IP address")
    user_agent: str | None = Field(default=None, description="Client user agent")
    client_id: str | None = Field(
        default=None,
        description="Client identifier if authenticated",
    )

    # Authentication
    user_id: UserId | None = Field(default=None, description="Authenticated user ID")
    session_id: str | None = Field(default=None, description="Session identifier")

    # Timing and status
    request_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the request was received",
    )
    processing_started_at: datetime | None = Field(
        default=None,
        description="When processing started",
    )

    def start_processing(self) -> None:
        """Mark request as started processing."""
        self.processing_started_at = datetime.now(UTC)


# Add alias for backward compatibility
ApiRequest = APIRequest


# ApiRequestReceivedEvent removed - use from flext_api.domain.events instead


class APIResponseLog(DomainEntity):
    """API Response log domain entity for tracking and auditing API responses."""

    # Response identification
    request_id: str = Field(..., description="Corresponding request identifier")
    response_id: str = Field(..., description="Unique response identifier")

    # Response data
    status_code: int = Field(..., description="HTTP status code")
    headers: dict[str, str] = Field(
        default_factory=dict,
        description="Response headers",
    )
    body: dict[str, Any] | None = Field(default=None, description="Response body data")
    content_type: str = Field(
        default="application/json",
        description="Response content type",
    )

    # Timing information
    response_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the response was sent",
    )
    processing_duration_ms: int | None = Field(
        default=None,
        description="Processing time in milliseconds",
    )

    # Response metadata
    size_bytes: int | None = Field(default=None, description="Response size in bytes")
    cache_status: str | None = Field(
        default=None,
        description="Cache status (HIT, MISS, etc.)",
    )

    # Error information (if applicable)
    error_code: str | None = Field(
        default=None,
        description="Error code if response indicates an error",
    )
    error_message: str | None = Field(
        default=None,
        description="Error message if applicable",
    )

    # Performance metrics
    database_query_count: int = Field(
        default=0,
        description="Number of database queries",
    )
    cache_hit_count: int = Field(default=0, description="Number of cache hits")
    external_api_calls: int = Field(
        default=0,
        description="Number of external API calls",
    )

    def mark_as_error(self, error_code: str, error_message: str) -> None:
        """Mark response as an error."""
        self.error_code = error_code
        self.error_message = error_message

    def set_processing_duration(self, start_time: datetime) -> None:
        """Calculate and set processing duration."""
        if self.response_timestamp and start_time:
            duration = self.response_timestamp - start_time
            self.processing_duration_ms = int(duration.total_seconds() * 1000)

    @property
    def is_success(self) -> bool:
        """Check if the API response indicates success."""
        return 200 <= self.status_code < 300

    @property
    def is_client_error(self) -> bool:
        """Check if the API response indicates client error."""
        return 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:
        """Check if the API response indicates server error."""
        return self.status_code >= 500


# Export all public entities for MyPy
__all__ = [
    "APIPipeline",
    "APIRequest",
    "APIResponse",
    "APIResponseLog",
    "ConfigDefaults",
    "HttpMethod",
    "PipelineCreatedEvent",
    "PipelineExecutedEvent",
    "PipelineExecution",
    "PipelineId",
    "PipelineStatus",
    "Plugin",
    "PluginId",
    "PluginMetadata",
    "PluginRegisteredEvent",
    "PluginType",
    "RequestLog",
    "ResponseLog",
    "UserId",
]

# NOTE: model_rebuild() calls removed to prevent import circular dependency issues
# Pydantic will resolve forward references automatically when needed
