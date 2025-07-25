"""Base service classes for FLEXT API application layer.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

REFACTORED: Uses DI for flext-auth integration - NO direct imports.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, TypeVar

from flext_core import get_logger

from flext_api.domain.ports import PipelineRepository, PluginRepository

if TYPE_CHECKING:
    from uuid import UUID

    from flext_core import FlextResult
    from flext_observability.metrics import MetricsCollector

    from flext_api.infrastructure.repositories import (
        APIRequestRepository,
        APIResponseRepository,
    )

# Note: Using HealthChecker instead of HealthMonitor
if TYPE_CHECKING:
    from flext_observability.health import HealthChecker
else:
    HealthChecker = Any

# Generic type for repository injection
TRepository = TypeVar("TRepository")


class BaseAPIService:
    """Base class for all API application services.

    Provides common initialization pattern and centralized logging
    to eliminate duplication across all service classes.
    """

    def __init__(self) -> None:
        """Initialize base service with centralized logger."""
        self.logger = get_logger(self.__class__.__module__)


class SingleRepositoryService[TRepository](BaseAPIService):
    """Base class for services that depend on a single repository.

    Eliminates duplication in services like PipelineService and PluginService
    that follow the pattern: __init__(self, repo: RepositoryType).
    """

    def __init__(self, repository: TRepository) -> None:
        """Initialize service with single repository dependency.

        Args:
            repository: The repository instance for this service,

        """
        super().__init__()
        self.repository = repository


class DualRepositoryService(BaseAPIService):
    """Base class for services that depend on two repositories.

    Eliminates duplication in services like FlextAPIService that manage
    multiple related repositories (request_repo, response_repo).
    """

    def __init__(
        self,
        primary_repo: APIRequestRepository | None = None,
        secondary_repo: APIResponseRepository | None = None,
    ) -> None:
        """Initialize service with dual repository dependencies.

        Args:
            primary_repo: Primary repository (optional),
            secondary_repo: Secondary repository (optional),

        """
        super().__init__()
        self.primary_repo = primary_repo
        self.secondary_repo = secondary_repo


class AuthenticationService(BaseAPIService):
    """Base class for authentication-related services.

    Eliminates duplication in AuthService initialization pattern.
    Uses DI for flext-auth integration - NO direct imports.
    """

    def __init__(
        self,
        auth_service: Any = None,  # Will be injected via DI
        session_service: Any = None,  # Will be injected via DI
    ) -> None:
        """Initialize authentication service with auth dependencies.

        Args:
            auth_service: Core authentication service (injected via DI),
            session_service: Session management service (injected via DI),

        """
        super().__init__()
        self.auth_service = auth_service
        self.session_service = session_service

    def _get_auth_service(self) -> Any:
        """Get auth service from DI container."""
        try:
            from flext_api.infrastructure.ports import FlextApiAuthPort

            return FlextApiAuthPort.get_instance()
        except Exception as e:
            self.logger.warning(f"Failed to get auth service from DI: {e}")
            return self.auth_service

    def _get_session_service(self) -> Any:
        """Get session service from DI container."""
        try:
            from flext_api.infrastructure.ports import FlextApiAuthPort

            auth_port = FlextApiAuthPort.get_instance()
            if auth_port and hasattr(auth_port, "session_service"):
                return auth_port.session_service
            return self.session_service
        except Exception as e:
            self.logger.warning(f"Failed to get session service from DI: {e}")
            return self.session_service


class MonitoringService(BaseAPIService):
    """Base class for monitoring-related services.

    Eliminates duplication in SystemService initialization pattern.
    """

    def __init__(
        self,
        health_monitor: HealthChecker | None = None,
        metrics_collector: MetricsCollector | None = None,
    ) -> None:
        """Initialize monitoring service with monitoring dependencies.

        Args:
            health_monitor: Health monitoring service,
            metrics_collector: Metrics collection service,

        """
        super().__init__()
        self.health_monitor = health_monitor
        self.metrics_collector = metrics_collector


# ==============================================================================
# PIPELINE SERVICE INTERFACES
# ==============================================================================


class PipelineReader(ABC):
    """Abstract interface for pipeline reading operations."""

    @abstractmethod
    async def get_pipeline(self, pipeline_id: UUID) -> FlextResult[Any]:
        """Get pipeline by ID."""

    @abstractmethod
    async def list_pipelines(
        self,
        owner_id: UUID | None = None,
        project_id: UUID | None = None,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> FlextResult[Any]:
        """List pipelines with optional filtering."""


class PipelineWriter(ABC):
    """Abstract interface for pipeline writing operations."""

    @abstractmethod
    async def create_pipeline(
        self,
        name: str,
        description: str | None = None,
        config: dict[str, Any] | None = None,
        owner_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> FlextResult[Any]:
        """Create new pipeline."""

    @abstractmethod
    async def update_pipeline(
        self,
        pipeline_id: UUID,
        name: str | None = None,
        description: str | None = None,
        config: dict[str, Any] | None = None,
        status: str | None = None,
    ) -> FlextResult[Any]:
        """Update existing pipeline."""

    @abstractmethod
    async def delete_pipeline(self, pipeline_id: UUID) -> FlextResult[Any]:
        """Delete pipeline."""


class PipelineExecutor(ABC):
    """Abstract interface for pipeline execution operations."""

    @abstractmethod
    async def execute_pipeline(self, pipeline_id: UUID) -> FlextResult[Any]:
        """Execute pipeline."""


class PipelineValidator(ABC):
    """Abstract interface for pipeline validation operations."""

    @abstractmethod
    async def validate_pipeline_config(
        self, config: dict[str, Any] | None
    ) -> FlextResult[Any]:
        """Validate pipeline configuration."""

    @abstractmethod
    async def validate_pipeline_name(
        self, name: str, owner_id: UUID | None
    ) -> FlextResult[Any]:
        """Validate pipeline name."""


# ==============================================================================
# CONCRETE SERVICE IMPLEMENTATIONS
# ==============================================================================


class PipelineBaseService(SingleRepositoryService[PipelineRepository]):
    """Base class for pipeline services."""


class PluginBaseService(SingleRepositoryService[PluginRepository]):
    """Base class for plugin services."""
