"""Domain events for FLEXT-API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the domain events for the FLEXT API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.domain.pydantic_base import DomainEvent, Field

# Runtime imports for model_rebuild to work - needed for Pydantic validation

if TYPE_CHECKING:
    from flext_core.domain.shared_types import (
        EntityId,
        PipelineId,
        PluginId,
        PluginType,
        UserId,
    )


# Pipeline Events
class PipelineCreatedEvent(DomainEvent):
    """Event raised when pipeline is created."""

    pipeline_id: PipelineId
    pipeline_name: str = Field(..., min_length=1)
    owner_id: UserId | None = None
    project_id: EntityId | None = None


class PipelineUpdatedEvent(DomainEvent):
    """Event raised when pipeline is updated."""

    pipeline_id: PipelineId
    changes: dict[str, object] = Field(default_factory=dict)
    updated_by: UserId | None = None


class PipelineDeletedEvent(DomainEvent):
    """Event raised when pipeline is deleted."""

    pipeline_id: PipelineId
    deleted_by: UserId | None = None


class PipelineExecutedEvent(DomainEvent):
    """Event raised when pipeline is executed."""

    pipeline_id: PipelineId
    execution_id: int = Field(ge=0)
    error_message: str | None = None


# Plugin Events
class PluginRegisteredEvent(DomainEvent):
    """Event raised when plugin is registered."""

    plugin_id: PluginId
    plugin_name: str = Field(..., min_length=1)
    plugin_type: PluginType
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")


class PluginUpdatedEvent(DomainEvent):
    """Event raised when plugin is updated."""

    plugin_id: PluginId
    changes: dict[str, object] = Field(default_factory=dict)
    updated_by: UserId | None = None


class PluginDisabledEvent(DomainEvent):
    """Event raised when plugin is disabled."""

    plugin_id: PluginId
    disabled_by: UserId | None = None
    reason: str | None = None


class PluginEnabledEvent(DomainEvent):
    """Event raised when plugin is enabled."""

    plugin_id: PluginId
    enabled_by: UserId | None = None


# API Request Events
class ApiRequestReceivedEvent(DomainEvent):
    """Event raised when API request is received."""

    request_id: EntityId
    method: str | None = None
    ip_address: str | None = None


class ApiRequestCompletedEvent(DomainEvent):
    """Event raised when API request is completed."""

    request_id: EntityId
    status_code: int = Field(ge=100, le=599)
    response_time_ms: int = Field(ge=0)
    success: bool


class ApiRateLimitExceededEvent(DomainEvent):
    """Event raised when rate limit is exceeded."""

    user_id: UserId | None = None
    ip_address: str
    limit: int = Field(default=1, ge=1)


# Authentication Events
class ApiAuthenticationFailedEvent(DomainEvent):
    """Event raised when authentication fails."""

    request_id: EntityId
    reason: str | None = None
    attempted_token: str | None = None  # Partial token for debugging


class ApiAuthorizationFailedEvent(DomainEvent):
    """Event raised when authorization fails."""

    request_id: EntityId
    user_id: UserId
    required_permission: str
    endpoint: str


# NOTE: model_rebuild() calls removed to prevent import circular dependency issues
# Pydantic will resolve forward references automatically when needed
