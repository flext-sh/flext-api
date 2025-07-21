"""Query objects for FLEXT API implementing CQRS pattern.

SINGLE RESPONSIBILITY PRINCIPLE: Each query has one clear responsibility.
Queries represent read operations that retrieve system state without modification.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from uuid import UUID

    from flext_core.domain.types import ServiceResult


# ==============================================================================
# SINGLE RESPONSIBILITY PRINCIPLE: Query Base Class
# ==============================================================================


class Query(ABC):
    """Base class for all queries (SRP compliance)."""

    @abstractmethod
    def validate_query(self) -> bool:
        """Validate query query parameters."""

    @abstractmethod
    def get_query_type(self) -> str:
        """Get query type identifier."""


# ==============================================================================
# SINGLE RESPONSIBILITY PRINCIPLE: Pipeline Queries
# ==============================================================================


class GetPipelineQuery(BaseModel, Query):
    """Query to retrieve a specific pipeline by ID (SRP compliance)."""

    pipeline_id: UUID
    include_executions: bool = False
    include_config: bool = True

    def validate_query(self) -> bool:
        """Validate query get pipeline query."""
        return True  # pipeline_id is required by Pydantic

    def get_query_type(self) -> str:
        """Get query type."""
        return "get_pipeline"


class ListPipelinesQuery(BaseModel, Query):
    """Query to list pipelines with filtering and pagination (SRP compliance)."""

    owner_id: UUID | None = None
    project_id: UUID | None = None
    status: str | None = None
    name_filter: str | None = Field(None, max_length=100)
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")

    def validate_query(self) -> bool:
        """Validate query list pipelines query."""
        return (
            1 <= self.limit <= 100
            and self.offset >= 0
            and self.sort_order in {"asc", "desc"}
        )

    def get_query_type(self) -> str:
        """Get query type."""
        return "list_pipelines"


class CountPipelinesQuery(BaseModel, Query):
    """Query to count pipelines matching criteria (SRP compliance)."""

    owner_id: UUID | None = None
    project_id: UUID | None = None
    status: str | None = None
    name_filter: str | None = Field(None, max_length=100)

    def validate_query(self) -> bool:
        """Validate query count pipelines query."""
        return True  # All filters are optional

    def get_query_type(self) -> str:
        """Get query type."""
        return "count_pipelines"


class GetPipelineExecutionsQuery(BaseModel, Query):
    """Query to retrieve executions for a pipeline (SRP compliance)."""

    pipeline_id: UUID
    status: str | None = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    include_logs: bool = False

    def validate_query(self) -> bool:
        """Validate query get pipeline executions query."""
        return 1 <= self.limit <= 100 and self.offset >= 0

    def get_query_type(self) -> str:
        """Get query type."""
        return "get_pipeline_executions"


# ==============================================================================
# SINGLE RESPONSIBILITY PRINCIPLE: Plugin Queries
# ==============================================================================


class GetPluginQuery(BaseModel, Query):
    """Query to retrieve a specific plugin by ID (SRP compliance)."""

    plugin_id: UUID
    include_config_schema: bool = True
    include_metadata: bool = True

    def validate_query(self) -> bool:
        """Validate query get plugin query."""
        return True  # plugin_id is required by Pydantic

    def get_query_type(self) -> str:
        """Get query type."""
        return "get_plugin"


class ListPluginsQuery(BaseModel, Query):
    """Query to list plugins with filtering and pagination (SRP compliance)."""

    plugin_type: str | None = None
    name_filter: str | None = Field(None, max_length=100)
    enabled_only: bool = False
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="name")
    sort_order: str = Field(default="asc", pattern="^(asc|desc)$")

    def validate_query(self) -> bool:
        """Validate query list plugins query."""
        return (
            1 <= self.limit <= 100
            and self.offset >= 0
            and self.sort_order in {"asc", "desc"}
        )

    def get_query_type(self) -> str:
        """Get query type."""
        return "list_plugins"


class SearchPluginsQuery(BaseModel, Query):
    """Query to search plugins by various criteria (SRP compliance)."""

    search_term: str = Field(..., min_length=1, max_length=100)
    search_fields: list[str] = Field(default=["name", "description"])
    plugin_type: str | None = None
    limit: int = Field(default=20, ge=1, le=50)

    def validate_query(self) -> bool:
        """Validate query search plugins query."""
        valid_fields = {"name", "description", "version", "entry_point"}
        return (
            len(self.search_term.strip()) >= 1
            and 1 <= self.limit <= 50
            and all(field in valid_fields for field in self.search_fields)
        )

    def get_query_type(self) -> str:
        """Get query type."""
        return "search_plugins"


# ==============================================================================
# SINGLE RESPONSIBILITY PRINCIPLE: System Queries
# ==============================================================================


class GetSystemStatusQuery(BaseModel, Query):
    """Query to retrieve system status information (SRP compliance)."""

    include_metrics: bool = True
    include_health_checks: bool = True
    include_alerts: bool = False

    def validate_query(self) -> bool:
        """Validate query system status query."""
        return True  # All parameters are optional booleans

    def get_query_type(self) -> str:
        """Get query type."""
        return "get_system_status"


class GetSystemMetricsQuery(BaseModel, Query):
    """Query to retrieve system metrics (SRP compliance)."""

    metric_name: str | None = None
    start_time: str | None = None  # ISO datetime string
    end_time: str | None = None  # ISO datetime string
    aggregation: str = Field(default="avg", pattern="^(avg|sum|min|max|count)$")

    def validate_query(self) -> bool:
        """Validate query system metrics query."""
        return self.aggregation in {"avg", "sum", "min", "max", "count"}

    def get_query_type(self) -> str:
        """Get query type."""
        return "get_system_metrics"


# ==============================================================================
# DEPENDENCY INVERSION PRINCIPLE: Query Handler Interface
# ==============================================================================


class QueryHandler(ABC):
    """Interface for query handlers (DIP compliance)."""

    @abstractmethod
    async def handle(self, query: Query) -> ServiceResult[Any]:
        """Handle a query and return result."""

    @abstractmethod
    def can_handle(self, query: Query) -> bool:
        """Check if this handler can process the query."""


# ==============================================================================
# SINGLE RESPONSIBILITY PRINCIPLE: Query Result Objects
# ==============================================================================


class QueryResult(BaseModel):
    """Base class for query results (SRP compliance)."""

    query_type: str
    execution_time_ms: float | None = None
    total_count: int | None = None


class PipelineQueryResult(QueryResult):
    """Result for pipeline queries (SRP compliance)."""

    pipelines: list[dict[str, Any]] = Field(default_factory=list)


class PluginQueryResult(QueryResult):
    """Result for plugin queries (SRP compliance)."""

    plugins: list[dict[str, Any]] = Field(default_factory=list)


class SystemQueryResult(QueryResult):
    """Result for system queries (SRP compliance)."""

    status: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)


# Export all queries and results for use in application layer
__all__ = [
    "CountPipelinesQuery",
    "GetPipelineExecutionsQuery",
    # Pipeline queries
    "GetPipelineQuery",
    # Plugin queries
    "GetPluginQuery",
    "GetSystemMetricsQuery",
    # System queries
    "GetSystemStatusQuery",
    "ListPipelinesQuery",
    "ListPluginsQuery",
    # Result objects
    "PipelineQueryResult",
    "PluginQueryResult",
    "Query",
    "QueryHandler",
    "QueryResult",
    "SearchPluginsQuery",
    "SystemQueryResult",
]
