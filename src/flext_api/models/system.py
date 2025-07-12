"""System API Models - Enterprise System Management.

REFACTORED:
    Uses flext-core APIRequest/APIResponse with types and StrEnum.
Zero tolerance for duplication.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from pydantic import Field
from pydantic import field_validator

from flext_core.domain.pydantic_base import APIRequest
from flext_core.domain.pydantic_base import APIResponse
from flext_core.domain.types import StrEnum

if TYPE_CHECKING:
    from datetime import datetime
    from uuid import UUID


class SystemStatus(StrEnum):
    """System status enumeration."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    STARTING = "starting"
    STOPPING = "stopping"


class MaintenanceMode(StrEnum):
    """Maintenance mode enumeration."""

    NONE = "none"
    PLANNED = "planned"
    EMERGENCY = "emergency"
    ROLLING = "rolling"


class ServiceType(StrEnum):
    """Service type enumeration."""

    API = "api"
    GRPC = "grpc"
    DATABASE = "database"
    REDIS = "redis"
    PLUGIN_SYSTEM = "plugin_system"
    AUTHENTICATION = "authentication"
    MONITORING = "monitoring"
    PIPELINE_ENGINE = "pipeline_engine"


class AlertSeverity(StrEnum):
    """Alert severity enumeration."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# --- Request Models ---


class MaintenanceRequest(APIRequest):
    """Request model for system maintenance operations."""

    mode: MaintenanceMode = Field(
        description="Type of maintenance mode",
    )
    reason: str = Field(
        max_length=500,
        description="Reason for maintenance",
    )
    estimated_duration_minutes: int | None = Field(
        default=None,
        ge=1,
        le=1440,  # Max 24 hours
        description="Estimated maintenance duration in minutes",
    )
    affected_services: list[ServiceType] = Field(
        default_factory=list,
        description="Services affected by maintenance",
    )
    notify_users: bool = Field(
        default=True,
        description="Whether to notify users about maintenance",
    )
    notification_message: str | None = Field(
        default=None,
        max_length=1000,
        description="Custom notification message for users",
    )
    scheduled_start: datetime | None = Field(
        default=None,
        description="Scheduled maintenance start time",
    )
    force_immediate: bool = Field(
        default=False,
        description="Force immediate maintenance without graceful shutdown",
    )
    backup_before_maintenance: bool = Field(
        default=True,
        description="Create system backup before maintenance",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional maintenance metadata",
    )


class SystemConfigurationRequest(APIRequest):
    """Request model for system configuration updates."""

    configuration_updates: dict[str, Any] = Field(
        description="Configuration updates to apply",
    )
    environment: str | None = Field(
        default=None,
        description="Target environment for configuration",
    )
    validate_before_apply: bool = Field(
        default=True,
        description="Validate configuration before applying",
    )
    backup_current_config: bool = Field(
        default=True,
        description="Backup current configuration before update",
    )
    restart_required_services: bool = Field(
        default=True,
        description="Restart services that require restart after config change",
    )
    rollback_on_failure: bool = Field(
        default=True,
        description="Rollback to previous configuration on failure",
    )
    notification_settings: dict[str, Any] = Field(
        default_factory=dict,
        description="Notification settings for configuration changes",
    )


class SystemBackupRequest(APIRequest):
    """Request model for system backup operations."""

    backup_type: str = Field(
        description="Type of backup (full, incremental, configuration)",
    )
    include_database: bool = Field(
        default=True,
        description="Include database in backup",
    )
    include_configuration: bool = Field(
        default=True,
        description="Include configuration files in backup",
    )
    include_logs: bool = Field(
        default=False,
        description="Include log files in backup",
    )
    include_plugins: bool = Field(
        default=True,
        description="Include plugin data in backup",
    )
    compression: bool = Field(
        default=True,
        description="Compress backup files",
    )
    encryption: bool = Field(
        default=True,
        description="Encrypt backup files",
    )
    retention_days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Backup retention period in days",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Backup description",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional backup metadata",
    )

    @field_validator("backup_type")
    @classmethod
    def validate_backup_type(cls, v: str) -> str:
        """Validate backup type value.

        Args:
            v: Backup type value to validate.

        Returns:
            Validated backup type.

        Raises:
            ValueError: If backup type is not allowed.

        """
        allowed_types = ["full", "incremental", "configuration", "database", "plugins"]
        if v not in allowed_types:
            msg = f"Backup type must be one of: {', '.join(allowed_types)}"
            raise ValueError(msg)
        return v


# --- Response Models ---


class SystemStatusResponse(APIResponse):
    """Response model for system status information."""

    status: SystemStatus = Field(description="Overall system status")
    version: str = Field(description="System version")
    uptime_seconds: int = Field(description="System uptime in seconds")
    maintenance_mode: MaintenanceMode = Field(description="Current maintenance mode")
    maintenance_message: str | None = Field(
        default=None,
        description="Maintenance message if applicable",
    )
    maintenance_estimated_end: datetime | None = Field(
        default=None,
        description="Estimated maintenance end time",
    )
    services: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Individual service status",
    )
    resource_usage: dict[str, Any] = Field(
        default_factory=dict,
        description="System resource usage",
    )
    performance_metrics: dict[str, Any] = Field(
        default_factory=dict,
        description="Performance metrics",
    )
    active_alerts: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Active system alerts",
    )
    last_backup: datetime | None = Field(
        default=None,
        description="Last backup timestamp",
    )
    configuration_version: str | None = Field(
        default=None,
        description="Current configuration version",
    )
    plugin_count: int = Field(default=0, description="Number of installed plugins")
    active_pipelines: int = Field(default=0, description="Number of active pipelines")
    system_load: dict[str, float] = Field(
        default_factory=dict,
        description="System load averages",
    )
    disk_usage: dict[str, Any] = Field(
        default_factory=dict,
        description="Disk usage information",
    )
    memory_usage: dict[str, Any] = Field(
        default_factory=dict,
        description="Memory usage information",
    )
    network_status: dict[str, Any] = Field(
        default_factory=dict,
        description="Network connectivity status",
    )
    security_status: dict[str, Any] = Field(
        default_factory=dict,
        description="Security status information",
    )
    feature_flags: dict[str, bool] = Field(
        default_factory=dict,
        description="Enabled feature flags",
    )
    environment: str = Field(description="Current environment")
    deployment_id: str | None = Field(
        default=None,
        description="Current deployment identifier",
    )
    build_info: dict[str, Any] = Field(
        default_factory=dict,
        description="Build and deployment information",
    )


class SystemServiceResponse(APIResponse):
    """Response model for individual service information."""

    service_name: str = Field(description="Service name")
    service_type: ServiceType = Field(description="Service type")
    status: SystemStatus = Field(description="Service status")
    version: str | None = Field(description="Service version")
    uptime_seconds: int = Field(description="Service uptime in seconds")
    health_checks: list[dict[str, Any]] = Field(
        description="Service health check results",
    )
    metrics: dict[str, Any] = Field(description="Service metrics")
    configuration: dict[str, Any] = Field(description="Service configuration")
    dependencies: list[str] = Field(description="Service dependencies")
    resource_usage: dict[str, Any] = Field(description="Service resource usage")
    last_restart: datetime | None = Field(description="Last restart timestamp")
    restart_count: int = Field(description="Number of restarts since start")
    error_count: int = Field(description="Error count in current session")
    warning_count: int = Field(description="Warning count in current session")
    performance_score: float = Field(
        ge=0.0,
        le=100.0,
        description="Service performance score",
    )


class MaintenanceResponse(APIResponse):
    """Response model for maintenance operations."""

    maintenance_id: UUID = Field(description="Unique maintenance identifier")
    mode: MaintenanceMode = Field(description="Maintenance mode")
    status: str = Field(description="Maintenance status")
    reason: str = Field(description="Maintenance reason")
    started_at: datetime = Field(description="Maintenance start timestamp")
    estimated_end: datetime | None = Field(description="Estimated completion time")
    actual_end: datetime | None = Field(description="Actual completion time")
    duration_minutes: int | None = Field(description="Actual duration in minutes")
    affected_services: list[ServiceType] = Field(description="Affected services")
    progress_percentage: float = Field(
        ge=0.0,
        le=100.0,
        description="Maintenance progress percentage",
    )
    current_step: str | None = Field(description="Current maintenance step")
    completed_steps: list[str] = Field(description="Completed maintenance steps")
    remaining_steps: list[str] = Field(description="Remaining maintenance steps")
    logs: list[dict[str, Any]] = Field(description="Maintenance operation logs")
    notifications_sent: int = Field(description="Number of notifications sent")
    rollback_available: bool = Field(description="Whether rollback is available")
    backup_created: bool = Field(description="Whether backup was created")
    initiated_by: str = Field(description="User who initiated maintenance")
    metadata: dict[str, Any] = Field(description="Additional maintenance metadata")


class SystemBackupResponse(APIResponse):
    """Response model for backup operations."""

    backup_id: UUID = Field(description="Unique backup identifier")
    backup_type: str = Field(description="Type of backup")
    status: str = Field(description="Backup status")
    created_at: datetime = Field(description="Backup creation timestamp")
    completed_at: datetime | None = Field(description="Backup completion timestamp")
    duration_seconds: int | None = Field(description="Backup duration in seconds")
    size_bytes: int | None = Field(description="Backup size in bytes")
    compression_ratio: float | None = Field(description="Compression ratio achieved")
    encrypted: bool = Field(description="Whether backup is encrypted")
    description: str | None = Field(description="Backup description")
    included_components: list[str] = Field(description="Components included in backup")
    file_count: int | None = Field(description="Number of files in backup")
    checksum: str | None = Field(description="Backup integrity checksum")
    storage_location: str | None = Field(description="Backup storage location")
    retention_until: datetime = Field(description="Backup retention expiry date")
    restore_count: int = Field(
        description="Number of times this backup was used for restore",
    )
    metadata: dict[str, Any] = Field(description="Additional backup metadata")
    created_by: str = Field(description="User who created the backup")
    system_version: str = Field(description="System version when backup was created")
    configuration_version: str | None = Field(
        description="Configuration version in backup",
    )


class SystemAlertResponse(APIResponse):
    """Response model for system alerts."""

    alert_id: UUID = Field(description="Unique alert identifier")
    severity: AlertSeverity = Field(description="Alert severity level")
    title: str = Field(max_length=200, description="Alert title")
    message: str = Field(max_length=1000, description="Alert message")
    service_name: str | None = Field(default=None, description="Affected service name")
    service_type: ServiceType | None = Field(default=None, description="Affected service type")
    created_at: datetime = Field(description="Alert creation timestamp")
    updated_at: datetime | None = Field(default=None, description="Alert last update timestamp")
    acknowledged: bool = Field(default=False, description="Whether alert is acknowledged")
    acknowledged_by: str | None = Field(default=None, description="User who acknowledged alert")
    acknowledged_at: datetime | None = Field(default=None, description="Alert acknowledgment timestamp")
    resolved: bool = Field(default=False, description="Whether alert is resolved")
    resolved_by: str | None = Field(default=None, description="User who resolved alert")
    resolved_at: datetime | None = Field(default=None, description="Alert resolution timestamp")
    alert_count: int = Field(default=1, ge=1, description="Number of similar alerts")
    first_occurrence: datetime = Field(description="First occurrence of this alert")
    last_occurrence: datetime = Field(description="Last occurrence of this alert")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional alert metadata",
    )
    tags: list[str] = Field(default_factory=list, description="Alert tags")
    source: str | None = Field(default=None, description="Alert source system")
    correlation_id: str | None = Field(default=None, description="Alert correlation identifier")
    escalation_level: int = Field(
        default=0,
        ge=0,
        le=5,
        description="Alert escalation level",
    )
    auto_resolve_after_minutes: int | None = Field(
        default=None,
        description="Auto-resolve after specified minutes",
    )


class SystemMetricsResponse(APIResponse):
    """Response model for system metrics."""

    metric_name: str = Field(description="Metric name")
    metric_type: str = Field(description="Metric type (gauge, counter, histogram)")
    value: float = Field(description="Current metric value")
    unit: str | None = Field(default=None, description="Metric unit")
    timestamp: datetime = Field(description="Metric collection timestamp")
    service_name: str | None = Field(default=None, description="Source service name")
    service_type: ServiceType | None = Field(default=None, description="Source service type")
    labels: dict[str, str] = Field(
        default_factory=dict,
        description="Metric labels",
    )
    description: str | None = Field(default=None, description="Metric description")
    historical_data: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Historical metric data points",
    )
    thresholds: dict[str, float] = Field(
        default_factory=dict,
        description="Metric threshold values",
    )
    status: str = Field(default="normal", description="Metric status")
    alert_rules: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Associated alert rules",
    )
    aggregation_period: str | None = Field(default=None, description="Aggregation period")
    collection_interval_seconds: int = Field(
        default=60,
        ge=1,
        description="Collection interval in seconds",
    )
    retention_days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Data retention period in days",
    )
    tags: list[str] = Field(default_factory=list, description="Metric tags")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metric metadata",
    )
