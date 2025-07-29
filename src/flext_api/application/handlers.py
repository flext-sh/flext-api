"""Application layer handlers for FLEXT API.

This module contains command handlers that implement the application layer
business logic for the FLEXT API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core import FlextResult, get_logger

from flext_api.base import FlextAPIRequest, FlextAPIResponse
from flext_api.domain.entities import FlextAPIPipeline as Pipeline

if TYPE_CHECKING:
    from uuid import UUID

    from flext_api.config import APISettings
    from flext_api.domain.ports import PipelineRepository
    from flext_api.infrastructure.ports import AuthService

# Create logger using flext-core get_logger function
logger = get_logger(__name__)

# ==============================================================================
# COMMAND CLASSES (Data Transfer Objects)
# ==============================================================================


class FlextApiAuthenticateCommand:
    """Command for authenticating a user."""

    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password


class FlextCreatePipelineCommand:
    """Command for creating a pipeline."""

    def __init__(self, pipeline_name: str, description: str | None = None) -> None:
        self.pipeline_name = pipeline_name
        self.description = description


class FlextGetPipelineCommand:
    """Command for getting a pipeline."""

    def __init__(self, pipeline_id: UUID) -> None:
        self.pipeline_id = pipeline_id


class FlextListPipelinesCommand:
    """Command for listing pipelines."""

    def __init__(self, limit: int = 20, offset: int = 0) -> None:
        self.limit = limit
        self.offset = offset


class FlextUpdatePipelineCommand:
    """Command for updating a pipeline."""

    def __init__(self, pipeline_id: UUID, updates: dict[str, Any]) -> None:
        self.pipeline_id = pipeline_id
        self.updates = updates


class FlextDeletePipelineCommand:
    """Command for deleting a pipeline."""

    def __init__(self, pipeline_id: UUID) -> None:
        self.pipeline_id = pipeline_id


class FlextCreatePluginCommand:
    """Command for creating a plugin."""

    def __init__(self, plugin_name: str, plugin_type: str) -> None:
        self.plugin_name = plugin_name
        self.plugin_type = plugin_type


class FlextGetPluginCommand:
    """Command for getting a plugin."""

    def __init__(self, plugin_id: UUID) -> None:
        self.plugin_id = plugin_id


class FlextListPluginsCommand:
    """Command for listing plugins."""

    def __init__(self, limit: int = 20, offset: int = 0) -> None:
        self.limit = limit
        self.offset = offset


class FlextUpdatePluginCommand:
    """Command for updating a plugin."""

    def __init__(self, plugin_id: UUID, updates: dict[str, Any]) -> None:
        self.plugin_id = plugin_id
        self.updates = updates


class FlextDeletePluginCommand:
    """Command for deleting a plugin."""

    def __init__(self, plugin_id: UUID) -> None:
        self.plugin_id = plugin_id


class FlextGetSystemInfoCommand:
    """Command for getting system information."""

    def __init__(self) -> None:
        pass


class FlextGetSystemHealthCommand:
    """Command for getting system health."""

    def __init__(self) -> None:
        pass


# ==============================================================================
# HANDLER CLASSES (Simplified Implementation)
# ==============================================================================


class FlextAuthenticationHandler:
    """Handler for authentication operations."""

    def __init__(self, auth_service: AuthService) -> None:
        self.auth_service = auth_service

    async def handle(self, _command: FlextApiAuthenticateCommand) -> FlextResult[Any]:
        """Handle authentication command."""
        # Simplified implementation
        return FlextResult.ok({"authenticated": True})


class FlextCreatePipelineHandler:
    """Handler for creating pipelines."""

    def __init__(self, repository: PipelineRepository) -> None:
        self.repository = repository

    async def handle(self, command: FlextCreatePipelineCommand) -> FlextResult[Any]:
        """Handle create pipeline command."""
        try:
            pipeline = Pipeline(
                name=command.pipeline_name,
                description=command.description,
            )
            saved_result = await self.repository.create(pipeline)
            if not saved_result.success:
                return saved_result
            saved_pipeline = saved_result.data
            return FlextResult.ok(saved_pipeline)
        except Exception as e:
            return FlextResult.fail(f"Failed to create pipeline: {e}")


class FlextGetSystemInfoHandler:
    """Handler for getting system information."""

    def __init__(self, config: APISettings) -> None:
        self.config = config

    async def handle(
        self,
        _command: FlextGetSystemInfoCommand,
    ) -> FlextResult[Any]:
        """Handle get system info command."""
        return FlextResult.ok(
            {
                "name": "FLEXT API",
                "status": "running",
                "environment": getattr(self.config, "environment", "development"),
            },
        )


class FlextGetSystemHealthHandler:
    """Handler for getting system health."""

    def __init__(self, service: AuthService | Any) -> None:
        self.service = service

    async def handle(
        self,
        _command: FlextGetSystemHealthCommand,
    ) -> FlextResult[Any]:
        """Handle get system health command."""
        return FlextResult.ok(
            {
                "status": "healthy",
                "timestamp": "2025-01-20T00:00:00Z",
                "components": {
                    "database": "healthy",
                    "auth": "healthy",
                },
            },
        )


# ==============================================================================
# FLEXT API HANDLERS - Real implementations using flext-core patterns
# ==============================================================================


class FlextApiHandler:
    """API handler for FlextApi patterns using proper inheritance."""

    def validate_request(self, request: FlextAPIRequest) -> FlextResult[None]:
        """Validate API request - override in subclasses for specific validation."""
        if not request:
            return FlextResult.fail("Request cannot be None")
        if not hasattr(request, "request_id") or not request.request_id:
            return FlextResult.fail("Request must have valid request_id")
        return FlextResult.ok(None)

    async def handle(
        self, request: FlextAPIRequest,
    ) -> FlextAPIResponse[dict[str, Any]]:
        """Handle API request with proper implementation."""
        # Validate request first
        validation_result = self.validate_request(request)
        if not validation_result.is_success:
            return FlextAPIResponse.error(
                message=validation_result.error or "Validation failed",
            )

        # Process request - subclasses should override this
        try:
            result = await self._process_request(request)
            return FlextAPIResponse.success(data=result)
        except Exception as e:
            return FlextAPIResponse.error(message=f"Request processing failed: {e!s}")

    async def _process_request(self, request: FlextAPIRequest) -> dict[str, Any]:
        """Process the request - override in subclasses."""
        return {"status": "processed", "request_id": request.request_id}


class FlextApiResponseHandler:
    """Response handler for FlextApi patterns with proper functionality."""

    def format_response(self, response: FlextAPIResponse[Any]) -> dict[str, Any]:
        """Format response for API output."""
        return response.model_dump()

    def add_headers(self, response_dict: dict[str, Any]) -> dict[str, Any]:
        """Add standard headers to response."""
        response_dict["headers"] = {
            "Content-Type": "application/json",
            "X-API-Version": "1.0",
        }
        return response_dict
