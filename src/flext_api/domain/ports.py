"""Domain ports for FLEXT-API.

REFACTORED:
Uses flext-core patterns - Clean Architecture ports/adapters.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from uuid import UUID

    from flext_core.domain.types import ServiceResult

    from flext_api.domain.entities import (
        APIPipeline,
        Plugin,
        RequestLog,
        ResponseLog,
    )

# ==============================================================================
# REPOSITORY PORTS
# ==============================================================================


class PipelineRepository(ABC):
    """Pipeline repository port."""

    @abstractmethod
    async def create(self, pipeline: APIPipeline) -> ServiceResult[APIPipeline]:
        """Create a new pipeline."""

    @abstractmethod
    async def get(self, pipeline_id: UUID) -> ServiceResult[APIPipeline]:
        """Get pipeline by ID."""

    @abstractmethod
    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
        owner_id: UUID | None = None,
        project_id: UUID | None = None,
        status: str | None = None,
    ) -> ServiceResult[list[APIPipeline]]:
        """List pipelines with optional filtering."""

    @abstractmethod
    async def update(self, pipeline: APIPipeline) -> ServiceResult[APIPipeline]:
        """Update existing pipeline."""

    @abstractmethod
    async def delete(self, pipeline_id: UUID) -> ServiceResult[bool]:
        """Delete pipeline by ID."""

    @abstractmethod
    async def count(
        self,
        owner_id: UUID | None = None,
        project_id: UUID | None = None,
        status: str | None = None,
    ) -> ServiceResult[int]:
        """Count pipelines with optional filtering."""

    @abstractmethod
    async def save(self, pipeline: APIPipeline) -> ServiceResult[APIPipeline]:
        """Save pipeline (create or update based on existence)."""


class PluginRepository(ABC):
    """Plugin repository port."""

    @abstractmethod
    async def create(self, plugin: Plugin) -> ServiceResult[Plugin]:
        """Create a new plugin."""

    @abstractmethod
    async def get(self, plugin_id: UUID) -> ServiceResult[Plugin]:
        """Get plugin by ID."""

    @abstractmethod
    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
        plugin_type: str | None = None,
        status: str | None = None,
    ) -> ServiceResult[list[Plugin]]:
        """List plugins with optional filtering."""

    @abstractmethod
    async def update(self, plugin: Plugin) -> ServiceResult[Plugin]:
        """Update existing plugin."""

    @abstractmethod
    async def delete(self, plugin_id: UUID) -> ServiceResult[bool]:
        """Delete plugin by ID."""

    @abstractmethod
    async def count(
        self,
        plugin_type: str | None = None,
        status: str | None = None,
    ) -> ServiceResult[int]:
        """Count plugins with optional filtering."""

    @abstractmethod
    async def save(self, plugin: Plugin) -> ServiceResult[Plugin]:
        """Save plugin (create or update based on existence)."""


class RequestRepository(ABC):
    """Request repository port."""

    @abstractmethod
    async def save(self, request: RequestLog) -> RequestLog:
        """Save request to storage."""

    @abstractmethod
    async def get(self, request_id: UUID) -> RequestLog | None:
        """Get request by ID."""

    @abstractmethod
    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
        user_id: UUID | None = None,
    ) -> list[RequestLog]:
        """List requests with optional filtering."""

    @abstractmethod
    async def delete(self, request_id: UUID) -> bool:
        """Delete request by ID."""


class ResponseRepository(ABC):
    """Response repository port."""

    @abstractmethod
    async def save(self, response: ResponseLog) -> ResponseLog:
        """Save response to storage."""

    @abstractmethod
    async def get(self, response_id: UUID) -> ResponseLog | None:
        """Get response by ID."""

    @abstractmethod
    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
        request_id: UUID | None = None,
    ) -> list[ResponseLog]:
        """List responses with optional filtering."""

    @abstractmethod
    async def delete(self, response_id: UUID) -> bool:
        """Delete response by ID."""


# ==============================================================================
# SERVICE PORTS
# ==============================================================================


class AuthService(ABC):
    """Authentication service port."""

    @abstractmethod
    async def authenticate(self, token: str) -> dict[str, Any] | None:
        """Authenticate a user with token."""

    @abstractmethod
    async def authorize(self, user_id: UUID, resource: str, action: str) -> bool:
        """Authorize user action on resource."""

    @abstractmethod
    async def generate_token(self, user_data: dict[str, Any]) -> str:
        """Generate authentication token."""

    @abstractmethod
    async def validate_token(self, token: str) -> dict[str, Any] | None:
        """Validate authentication token."""


class CacheService(ABC):
    """Cache service port."""

    @abstractmethod
    async def get(self, key: str) -> str | bytes | dict[str, object] | None:
        """Get value from cache."""

    @abstractmethod
    async def set(
        self,
        key: str,
        value: str | bytes | dict[str, object],
        ttl: int | None = None,
    ) -> bool:
        """Set value in cache."""

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache."""


class HealthCheckService(ABC):
    """Health check service port."""

    @abstractmethod
    async def check_health(self) -> dict[str, Any]:
        """Check overall system health."""

    @abstractmethod
    async def check_database(self) -> bool:
        """Check database health."""

    @abstractmethod
    async def check_cache(self) -> bool:
        """Check cache health."""

    @abstractmethod
    async def check_dependencies(self) -> dict[str, dict[str, Any]]:
        """Check all dependencies health."""


class MetricsService(ABC):
    """Metrics service port."""

    @abstractmethod
    async def record_request(self, request: RequestLog) -> None:
        """Record API request metrics."""

    @abstractmethod
    async def record_response(self, response: ResponseLog) -> None:
        """Record API response metrics."""

    @abstractmethod
    async def get_metrics(self) -> dict[str, Any]:
        """Get current metrics."""

    @abstractmethod
    async def reset_metrics(self) -> None:
        """Reset all metrics."""


class RateLimitService(ABC):
    """Rate limiting service port."""

    @abstractmethod
    async def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """Check if rate limit exceeded."""

    @abstractmethod
    async def increment_counter(self, key: str, window: int) -> int:
        """Increment rate limit counter."""

    @abstractmethod
    async def reset_counter(self, key: str) -> None:
        """Reset rate limit counter."""


class ServerService(ABC):
    """Server service port."""

    @abstractmethod
    async def start(self, app: Any) -> None:
        """Start the server."""

    @abstractmethod
    async def stop(self) -> None:
        """Stop the server."""

    @abstractmethod
    async def restart(self) -> None:
        """Restart the server."""

    @abstractmethod
    async def get_status(self) -> dict[str, Any]:
        """Get server status."""


class ValidationService(ABC):
    """Validation service port."""

    @abstractmethod
    async def validate_request(self, request: RequestLog) -> Any:
        """Validate API request."""

    @abstractmethod
    async def validate_pipeline(self, pipeline: APIPipeline) -> Any:
        """Validate pipeline configuration."""

    @abstractmethod
    async def validate_plugin(self, plugin: Plugin) -> Any:
        """Validate plugin configuration."""

    @abstractmethod
    async def validate_schema(
        self,
        data: dict[str, Any],
        schema: dict[str, Any],
    ) -> Any:
        """Validate data against schema."""


class WebFrameworkService(ABC):
    """Web framework service port."""

    @abstractmethod
    async def create_app(self) -> Any:
        """Create web application."""

    @abstractmethod
    async def add_middleware(self, app: Any, middleware: Any) -> None:
        """Add middleware to application."""

    @abstractmethod
    async def add_route(
        self,
        app: Any,
        path: str,
        handler: Any,
        methods: list[str],
    ) -> None:
        """Add route to application."""

    @abstractmethod
    async def configure_cors(self, app: Any, allowed_origins: list[str]) -> None:
        """Configure CORS for application."""


class PipelineExecutionService(ABC):
    """Pipeline execution service port."""

    @abstractmethod
    async def execute_pipeline(
        self,
        pipeline_id: UUID,
        config: dict[str, Any] | None = None,
    ) -> ServiceResult[str]:
        """Execute pipeline and return execution ID."""

    @abstractmethod
    async def get_execution_status(
        self,
        execution_id: str,
    ) -> ServiceResult[dict[str, Any]]:
        """Get pipeline execution status."""

    @abstractmethod
    async def cancel_execution(self, execution_id: str) -> ServiceResult[bool]:
        """Cancel pipeline execution."""


class PluginManagementService(ABC):
    """Plugin management service port."""

    @abstractmethod
    async def install_plugin(
        self,
        name: str,
        version: str,
        config: dict[str, Any] | None = None,
    ) -> ServiceResult[Plugin]:
        """Install plugin from registry."""

    @abstractmethod
    async def uninstall_plugin(self, plugin_id: UUID) -> ServiceResult[bool]:
        """Uninstall plugin."""

    @abstractmethod
    async def update_plugin_config(
        self,
        plugin_id: UUID,
        config: dict[str, Any],
    ) -> ServiceResult[Plugin]:
        """Update plugin configuration."""


# ==============================================================================
# EXTERNAL SERVICE PORTS
# ==============================================================================


class NotificationService(ABC):
    """Notification service port."""

    @abstractmethod
    async def send_notification(
        self,
        user_id: str,
        message: str,
        msg_type: str = "info",
    ) -> ServiceResult[bool]:
        """Send notification to recipient."""


class AuditService(ABC):
    """Audit service port."""

    @abstractmethod
    async def log_action(
        self,
        user_id: str,
        action: str,
        entity_type: str,
        entity_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> ServiceResult[bool]:
        """Log user action for audit trail."""


# ==============================================================================
# API PORTS
# ==============================================================================


class APIAuthenticationService(ABC):
    """API authentication service port."""

    @abstractmethod
    async def authenticate_request(
        self,
        request: RequestLog,
    ) -> ServiceResult[dict[str, Any]]:
        """Authenticate API request."""

    @abstractmethod
    async def authorize_action(
        self,
        user_id: str,
        action: str,
        resource: str,
    ) -> ServiceResult[bool]:
        """Authorize user action on resource."""


class APIResponseBuilder(ABC):
    """API response builder port."""

    @abstractmethod
    def build_success_response(
        self,
        data: Any,
        message: str | None = None,
    ) -> ResponseLog:
        """Build successful API response."""

    @abstractmethod
    def build_error_response(
        self,
        error: str,
        status_code: int = 400,
        extra_data: dict[str, Any] | None = None,
    ) -> ResponseLog:
        """Build error API response."""
