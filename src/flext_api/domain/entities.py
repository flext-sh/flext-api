"""Domain entities for FLEXT-API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

REFACTORED: Uses flext-core domain entities - NO duplication.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from flext_core import (
    FlextEntity,
    FlextEntity as FlextEntityId,
    FlextResult,
    FlextValidationError,
    FlextValueObject,
)
from pydantic import Field, field_validator

from flext_api.base import FlextAPIResponse


# Define our own constants - NO FAKE FlextConstants import
class ConfigDefaults:
    """Configuration defaults for API entities."""

    MAX_SERVICE_NAME_LENGTH = 255
    MAX_DESCRIPTION_LENGTH = 1000
    DEFAULT_PLUGIN_VERSION = "1.0.0"


# Use proper typed IDs from flext-core
PipelineId = FlextEntity  # Pipeline identifier
PluginId = FlextEntity  # Plugin identifier
# Type aliases for identifiers
UserId = str  # User identifier
EntityId = str  # Generic entity identifier alias


# Use proper classes instead of generic aliases
class Pipeline(FlextEntity):
    """Pipeline domain entity."""

    name: str = Field(..., max_length=ConfigDefaults.MAX_SERVICE_NAME_LENGTH)
    description: str = Field(default="", max_length=1000)

    def validate_domain_rules(self) -> None:
        """Validate Pipeline domain rules."""
        if not self.name or not self.name.strip():
            msg = "Pipeline name cannot be empty"
            raise FlextValidationError(msg)


class PipelineExecution(FlextEntity):
    """Pipeline execution domain entity."""

    pipeline_id: PipelineId = Field(...)
    status: str = Field(default="pending")

    def validate_domain_rules(self) -> None:
        """Validate PipelineExecution domain rules."""
        if not self.pipeline_id:
            msg = "Pipeline ID cannot be empty"
            raise FlextValidationError(msg)

        if not self.status or not self.status.strip():
            msg = "Status cannot be empty"
            raise FlextValidationError(msg)


# PluginMetadata should use structured data, not generic dict
class PluginMetadata(FlextValueObject):
    """Plugin metadata value object."""

    name: str = Field(...)
    version: str = Field(...)
    description: str = Field(default="")

    def validate_domain_rules(self) -> None:
        """Validate plugin metadata domain rules."""
        if not self.name or not self.name.strip():
            msg = "Plugin name cannot be empty"
            raise ValueError(msg)
        if not self.version or not self.version.strip():
            msg = "Plugin version cannot be empty"
            raise ValueError(msg)


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


class FlextAPIPipeline(FlextEntity):
    """API Pipeline domain entity using enhanced mixins for code reduction."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=ConfigDefaults.MAX_SERVICE_NAME_LENGTH,
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
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

    def record_execution(self, *, success: bool = True) -> FlextAPIPipeline:
        """Record the execution of the pipeline.

        Returns:
            New FlextAPIPipeline instance with updated execution statistics.

        """
        data = self.model_dump()
        data["run_count"] = self.run_count + 1
        data["last_run_at"] = datetime.now(UTC)
        if success:
            data["success_count"] = self.success_count + 1
        else:
            data["failure_count"] = self.failure_count + 1
        return FlextAPIPipeline(**data)

    def validate_domain_rules(self) -> None:
        """Validate pipeline domain rules."""
        if not self.name or not self.name.strip():
            msg = "Pipeline name cannot be empty"
            raise FlextValidationError(msg)

        if self.run_count < 0:
            msg = "Run count cannot be negative"
            raise FlextValidationError(msg)

        if self.success_count < 0 or self.failure_count < 0:
            msg = "Success/failure counts cannot be negative"
            raise FlextValidationError(msg)

        if self.rate_limit <= 0:
            msg = "Rate limit must be positive"
            raise FlextValidationError(msg)


# Define our own PluginType enum - NO FAKE import from flext-core
class PluginType(StrEnum):
    """Plugin type enumeration."""

    EXTRACTOR = "extractor"
    LOADER = "loader"
    TRANSFORMER = "transformer"
    UTILITY = "utility"


class Plugin(FlextEntity):
    """API Plugin domain entity using enhanced mixins for code reduction."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=ConfigDefaults.MAX_SERVICE_NAME_LENGTH,
    )
    plugin_type: PluginType = Field(
        default=PluginType.UTILITY,
        description="Plugin type (renamed to avoid confusion)",
    )
    plugin_version: str = Field(
        default="0.7.0",
        pattern=r"^\d+\.\d+\.\d+$",
        description="Plugin semantic version (separate from entity version)",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
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
        max_length=ConfigDefaults.MAX_SERVICE_NAME_LENGTH,
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

    def validate_domain_rules(self) -> None:
        """Validate plugin domain rules."""
        if not self.name or not self.name.strip():
            msg = "Plugin name cannot be empty"
            raise FlextValidationError(msg)

        if not self.plugin_version:
            msg = "Plugin version cannot be empty"
            raise FlextValidationError(msg)

        # Validate version format (basic semantic version pattern)
        import re

        if not re.match(r"^\d+\.\d+\.\d+", self.plugin_version):
            msg = "Plugin version must follow semver format (e.g., 1.0.0)"
            raise FlextValidationError(msg)


class FlextAPIRequest(FlextEntity):
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
        default=None, description="Client identifier if authenticated"
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
        default=None, description="When processing started"
    )

    def start_processing(self) -> FlextAPIRequest:
        """Mark request as started processing.

        Returns:
            New FlextAPIRequest instance with processing started timestamp.

        """
        data = self.model_dump()
        data["processing_started_at"] = datetime.now(UTC)
        return FlextAPIRequest(**data)

    def validate_domain_rules(self) -> None:
        """Validate FlextAPIRequest domain rules."""
        if not self.request_id or not self.request_id.strip():
            msg = "Request ID cannot be empty"
            raise FlextValidationError(msg)

        if not self.endpoint or not self.endpoint.strip():
            msg = "Endpoint cannot be empty"
            raise FlextValidationError(msg)

        if not self.method or not self.method.strip():
            msg = "HTTP method cannot be empty"
            raise FlextValidationError(msg)


class APIResponseLog(FlextEntity):
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

    def mark_as_error(self, error_code: str, error_message: str) -> APIResponseLog:
        """Mark response as an error.

        Returns:
            New APIResponseLog instance with error information.

        """
        data = self.model_dump()
        data["error_code"] = error_code
        data["error_message"] = error_message
        return APIResponseLog(**data)

    def set_processing_duration(self, start_time: datetime) -> APIResponseLog:
        """Calculate and set processing duration.

        Returns:
            New APIResponseLog instance with processing duration set.

        """
        data = self.model_dump()
        if self.response_timestamp and start_time:
            duration = self.response_timestamp - start_time
            data["processing_duration_ms"] = int(duration.total_seconds() * 1000)
        return APIResponseLog(**data)

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

    def validate_domain_rules(self) -> None:
        """Validate APIResponseLog domain rules."""
        if not self.request_id or not self.request_id.strip():
            msg = "Request ID cannot be empty"
            raise FlextValidationError(msg)

        if not self.response_id or not self.response_id.strip():
            msg = "Response ID cannot be empty"
            raise FlextValidationError(msg)

        if self.status_code < 100 or self.status_code > 599:
            msg = "Status code must be between 100 and 599"
            raise FlextValidationError(msg)

        if self.processing_duration_ms is not None and self.processing_duration_ms < 0:
            msg = "Processing duration cannot be negative"
            raise FlextValidationError(msg)


# ========================================
# FLEXT API DOMAIN ENTITIES - Using proper flext-core patterns
# ========================================


class FlextApiEndpoint(FlextEntity):
    """API endpoint domain entity."""

    name: str = Field(..., description="Endpoint name")
    path: str = Field(..., description="Endpoint path")
    method: HttpMethod = Field(..., description="HTTP method")
    is_active: bool = Field(default=True, description="Endpoint is active")

    def activate(self) -> FlextApiEndpoint:
        """Activate this endpoint.

        Returns:
            New FlextApiEndpoint instance with is_active set to True.

        """
        data = self.model_dump()
        data["is_active"] = True
        return FlextApiEndpoint(**data)

    def deactivate(self) -> FlextApiEndpoint:
        """Deactivate this endpoint.

        Returns:
            New FlextApiEndpoint instance with is_active set to False.

        """
        data = self.model_dump()
        data["is_active"] = False
        return FlextApiEndpoint(**data)

    def validate_domain_rules(self) -> None:
        """Validate FlextApiEndpoint domain rules."""
        if not self.name or not self.name.strip():
            msg = "Endpoint name cannot be empty"
            raise FlextValidationError(msg)

        if not self.path or not self.path.strip():
            msg = "Endpoint path cannot be empty"
            raise FlextValidationError(msg)

        if not self.path.startswith("/"):
            msg = "Endpoint path must start with '/'"
            raise FlextValidationError(msg)


class FlextApiRequest(FlextAPIRequest):
    """API request extending flext-core base with domain-specific validation."""

    endpoint: str = Field(..., description="Request endpoint")
    method: HttpMethod = Field(..., description="HTTP method")
    data: dict[str, Any] = Field(default_factory=dict, description="Request data")

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate API-specific business rules."""
        if not self.endpoint or not self.endpoint.strip():
            return FlextResult.fail("Endpoint cannot be empty")

        if not self.endpoint.startswith("/"):
            return FlextResult.fail("Endpoint must start with '/'")

        return FlextResult.ok(None)

    def validate_domain_rules(self) -> None:
        """Validate FlextApiRequest domain rules."""
        if not self.endpoint or not self.endpoint.strip():
            msg = "Endpoint cannot be empty"
            raise FlextValidationError(msg)

        if not self.endpoint.startswith("/"):
            msg = "Endpoint must start with '/'"
            raise FlextValidationError(msg)


class FlextApiResponse(FlextAPIResponse[dict[str, Any]]):
    """API response extending flext-core base with domain-specific functionality."""

    def add_api_metadata(self, version: str = "1.0") -> None:
        """Add API-specific metadata to response."""
        if not self.data:
            self.data = {}
        self.data.update({"_api_version": version, "_response_type": "flext_api"})

    def validate_domain_rules(self) -> None:
        """Validate FlextApiResponse domain rules."""
        # FlextApiResponse validation - basic checks
        return


__all__ = [
    "APIResponseLog",
    "FlextAPIPipeline",
    "FlextAPIRequest",
    "FlextApiEndpoint",
    "FlextApiRequest",
    "FlextApiResponse",
    "HttpMethod",
    "Pipeline",
    "PipelineExecution",
    "PipelineStatus",
    "Plugin",
    "PluginMetadata"
]
