"""Base service classes to eliminate code duplication across FLEXT API services.

This module provides foundational base classes that encapsulate common patterns
used across all application services, following DRY principles and Clean Architecture.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

# Use centralized logger from flext-observability - ELIMINATE DUPLICATION
from flext_observability.logging import get_logger

from flext_api.domain.ports import PipelineRepository, PluginRepository

if TYPE_CHECKING:
    from uuid import UUID

    from flext_auth.application.services import (
        AuthService as FlextAuthService,
        SessionService,
    )
    from flext_core.domain.types import ServiceResult
    from flext_observability.monitoring.health import HealthMonitor
    from flext_observability.monitoring.metrics import MetricsCollector

    from flext_api.infrastructure.repositories import (
        APIRequestRepository,
        APIResponseRepository,
    )

# Runtime imports for ISP interfaces
from abc import ABC, abstractmethod
from typing import Any

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
            repository: The repository instance for this service

        """
        super().__init__()
        self.repository = repository


class DualRepositoryService(BaseAPIService):
    """Base class for services that depend on two repositories.

    Eliminates duplication in services like APIService that manage
    multiple related repositories (request_repo, response_repo).
    """

    def __init__(
        self,
        primary_repo: APIRequestRepository | None = None,
        secondary_repo: APIResponseRepository | None = None,
    ) -> None:
        """Initialize service with dual repository dependencies.

        Args:
            primary_repo: Primary repository (optional)
            secondary_repo: Secondary repository (optional)

        """
        super().__init__()
        self.primary_repo = primary_repo
        self.secondary_repo = secondary_repo


class AuthenticationService(BaseAPIService):
    """Base class for authentication-related services.

    Eliminates duplication in AuthService initialization pattern.
    """

    def __init__(
        self,
        auth_service: FlextAuthService,
        session_service: SessionService,
    ) -> None:
        """Initialize authentication service with auth dependencies.

        Args:
            auth_service: Core authentication service
            session_service: Session management service

        """
        super().__init__()
        self.auth_service = auth_service
        self.session_service = session_service


class MonitoringService(BaseAPIService):
    """Base class for system monitoring services.

    Eliminates duplication in SystemService initialization pattern.
    """

    def __init__(
        self,
        health_monitor: HealthMonitor | None = None,
        metrics_collector: MetricsCollector | None = None,
    ) -> None:
        """Initialize monitoring service with monitoring dependencies.

        Args:
            health_monitor: Health monitoring component (optional)
            metrics_collector: Metrics collection component (optional)

        """
        super().__init__()
        self.health_monitor = health_monitor
        self.metrics_collector = metrics_collector


# ==============================================================================
# INTERFACE SEGREGATION PRINCIPLE: Focused Service Interfaces
# ==============================================================================


class PipelineReader(ABC):
    """Interface for pipeline read operations (ISP compliance)."""

    @abstractmethod
    async def get_pipeline(self, pipeline_id: UUID) -> ServiceResult[Any]:
        """Get pipeline by ID."""

    @abstractmethod
    async def list_pipelines(
        self,
        owner_id: UUID | None = None,
        project_id: UUID | None = None,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> ServiceResult[list[Any]]:
        """List pipelines with filtering."""


class PipelineWriter(ABC):
    """Interface for pipeline write operations (ISP compliance)."""

    @abstractmethod
    async def create_pipeline(
        self,
        name: str,
        description: str | None = None,
        config: dict[str, Any] | None = None,
        owner_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> ServiceResult[Any]:
        """Create a new pipeline."""

    @abstractmethod
    async def update_pipeline(
        self,
        pipeline_id: UUID,
        name: str | None = None,
        description: str | None = None,
        config: dict[str, Any] | None = None,
        status: str | None = None,
    ) -> ServiceResult[Any]:
        """Update existing pipeline."""

    @abstractmethod
    async def delete_pipeline(self, pipeline_id: UUID) -> ServiceResult[bool]:
        """Delete pipeline."""


class PipelineExecutor(ABC):
    """Interface for pipeline execution operations (ISP compliance)."""

    @abstractmethod
    async def execute_pipeline(self, pipeline_id: UUID) -> ServiceResult[Any]:
        """Execute pipeline."""


class PipelineValidator(ABC):
    """Interface for pipeline validation operations (ISP compliance)."""

    @abstractmethod
    async def validate_pipeline_config(
        self, config: dict[str, Any] | None,
    ) -> ServiceResult[bool]:
        """Validate pipeline configuration."""

    @abstractmethod
    async def validate_pipeline_name(
        self, name: str, owner_id: UUID | None,
    ) -> ServiceResult[bool]:
        """Validate pipeline name uniqueness."""


# Convenience type aliases for specific service patterns


class PipelineBaseService(SingleRepositoryService[PipelineRepository]):
    """Specialized base class for pipeline-related services."""


class PluginBaseService(SingleRepositoryService[PluginRepository]):
    """Specialized base class for plugin-related services."""
