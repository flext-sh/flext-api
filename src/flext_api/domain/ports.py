"""Domain ports for FLEXT-API.

REFACTORED:
Uses flext-core patterns - Clean Architecture ports/adapters.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from uuid import UUID

    from flext_core.domain.entities import Pipeline as APIPipeline
    from flext_core.domain.entities import Plugin as APIPlugin
    from flext_core.domain.pydantic_base import APIRequest
    from flext_core.domain.pydantic_base import APIResponse
    from flext_core.domain.types import ServiceResult


# ==============================================================================
# REPOSITORY PORTS
# ==============================================================================


class PipelineRepository(ABC):
    """Pipeline repository port."""

    @abstractmethod
    async def save(self, pipeline: APIPipeline) -> APIPipeline:
        """Save pipeline to storage."""

    @abstractmethod
    async def get(self, pipeline_id: UUID) -> APIPipeline | None:
        """Get pipeline by ID."""

    @abstractmethod
    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
        status: str | None = None,
    ) -> list[APIPipeline]:
        """List pipelines with optional filtering."""

    @abstractmethod
    async def delete(self, pipeline_id: UUID) -> bool:
        """Delete pipeline by ID."""


class PluginRepository(ABC):
    """Plugin repository port."""

    @abstractmethod
    async def save(self, plugin: APIPlugin) -> APIPlugin:
        """Save plugin to storage."""

    @abstractmethod
    async def get(self, plugin_id: UUID) -> APIPlugin | None:
        """Get plugin by ID."""

    @abstractmethod
    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
        plugin_type: str | None = None,
        enabled: bool | None = None,
    ) -> list[APIPlugin]:
        """List plugins with optional filtering."""

    @abstractmethod
    async def delete(self, plugin_id: UUID) -> bool:
        """Delete plugin by ID."""


# ==============================================================================
# SERVICE PORTS
# ==============================================================================


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
        self, execution_id: str
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
    ) -> ServiceResult[APIPlugin]:
        """Install plugin from registry."""

    @abstractmethod
    async def uninstall_plugin(self, plugin_id: UUID) -> ServiceResult[bool]:
        """Uninstall plugin."""

    @abstractmethod
    async def update_plugin_config(
        self,
        plugin_id: UUID,
        config: dict[str, Any],
    ) -> ServiceResult[APIPlugin]:
        """Update plugin configuration."""


# ==============================================================================
# EXTERNAL SERVICE PORTS
# ==============================================================================


class NotificationService(ABC):
    """Notification service port."""

    @abstractmethod
    async def send_notification(
        self,
        recipient: str,
        message: str,
        notification_type: str = "info",
    ) -> ServiceResult[bool]:
        """Send notification to recipient."""


class AuditService(ABC):
    """Audit service port."""

    @abstractmethod
    async def log_action(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
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
        self, request: APIRequest
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
    ) -> APIResponse:
        """Build successful API response."""

    @abstractmethod
    def build_error_response(
        self,
        error: str,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> APIResponse:
        """Build error API response."""
