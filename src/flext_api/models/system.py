"""System API Models - Enterprise System Management.

This module provides comprehensive Pydantic models for system management
operations including status monitoring, maintenance, configuration, and health checks.
Follows enterprise patterns with Python 3.13 type system.
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Any

from flext_core.domain.pydantic_base import DomainBaseModel
from pydantic import Field, field_validator

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


class APIResponse(DomainBaseModel):
    """Standard API response model."""

    success: bool = Field(description="Whether the operation was successful")
    message: str = Field(description="Human-readable response message")
    data: Any = Field(default=None, description="Response data payload")
    errors: list[str] = Field(default_factory=list, description="List of error messages")
    timestamp: str = Field(description="Response timestamp")

    @classmethod
    def success_response(cls, data: Any = None, message: str = "Operation successful") -> APIResponse:
        """Create a successful API response."""
        from datetime import datetime
        return cls(
            success=True,
            message=message,
            data=data,
            timestamp=datetime.now().isoformat()
        )

    @classmethod
    def error_response(cls, errors: list[str], message: str = "Operation failed") -> APIResponse:
        """Create an error API response."""
        from datetime import datetime
        return cls(
            success=False,
            message=message,
            errors=errors,
            timestamp=datetime.now().isoformat()
        )


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


class MaintenanceRequest(DomainBaseModel):
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


class SystemConfigurationRequest(DomainBaseModel):
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


class SystemBackupRequest(DomainBaseModel):
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
        """Validate backup type."""
        allowed_types = ["full", "incremental", "configuration", "database", "plugins"]
        if v not in allowed_types:
            msg = f"Backup type must be one of: {', '.join(allowed_types)}"
            raise ValueError(msg)
        return v


class SystemRestoreRequest(DomainBaseModel):
    """Request model for system restore operations."""

    backup_id: UUID = Field(
        description="ID of the backup to restore from",
    )
    restore_database: bool = Field(
        default=True,
        description="Restore database from backup",
    )
    restore_configuration: bool = Field(
        default=True,
        description="Restore configuration from backup",
    )
    restore_plugins: bool = Field(
        default=True,
        description="Restore plugins from backup",
    )
    force_restore: bool = Field(
        default=False,
        description="Force restore even if current system is newer",
    )
    verify_backup_integrity: bool = Field(
        default=True,
        description="Verify backup integrity before restore",
    )
    create_pre_restore_backup: bool = Field(
        default=True,
        description="Create backup of current system before restore",
    )
    restart_after_restore: bool = Field(
        default=True,
        description="Restart system after restore completion",
    )


class SystemHealthCheckRequest(DomainBaseModel):
    """Request model for system health checks."""

    check_types: list[str] = Field(
        default_factory=lambda: ["all"],
        description="Types of health checks to perform",
    )
    include_external_dependencies: bool = Field(
        default=True,
        description="Include external dependency checks",
    )
    deep_check: bool = Field(
        default=False,
        description="Perform deep health checks (may take longer)",
    )
    timeout_seconds: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Timeout for health checks in seconds",
    )

    @field_validator("check_types")
    @classmethod
    def validate_check_types(cls, v: list[str]) -> list[str]:
        """Validate health check types."""
        allowed_types = [
            "all",
            "database",
            "redis",
            "api",
            "grpc",
            "plugins",
            "authentication",
            "monitoring",
            "pipelines",
            "external",
        ]
        for check_type in v:
            if check_type not in allowed_types:
                msg = f"Invalid check type: {check_type}. Must be one of: {', '.join(allowed_types)}"
                raise ValueError(msg)
        return v


# --- Response Models ---


class SystemStatusResponse(DomainBaseModel):
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


class SystemServiceResponse(DomainBaseModel):
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


class MaintenanceResponse(DomainBaseModel):
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


class SystemBackupResponse(DomainBaseModel):
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


class SystemHealthResponse(DomainBaseModel):
    """Response model for system health information."""

    overall_health: SystemStatus = Field(description="Overall system health status")
    health_score: float = Field(
        ge=0.0,
        le=100.0,
        description="Overall health score",
    )
    checks_performed: int = Field(description="Number of health checks performed")
    checks_passed: int = Field(description="Number of health checks passed")
    checks_failed: int = Field(description="Number of health checks failed")
    check_results: list[dict[str, Any]] = Field(description="Individual check results")
    system_metrics: dict[str, Any] = Field(description="System performance metrics")
    resource_alerts: list[dict[str, Any]] = Field(description="Resource usage alerts")
    service_health: list[SystemServiceResponse] = Field(
        description="Individual service health",
    )
    external_dependencies: list[dict[str, Any]] = Field(
        description="External dependency status",
    )
    recommendations: list[str] = Field(description="Health improvement recommendations")
    critical_issues: list[str] = Field(
        description="Critical issues requiring attention",
    )
    warnings: list[str] = Field(description="Warnings that should be addressed")
    last_check_time: datetime = Field(description="Last health check timestamp")
    next_scheduled_check: datetime | None = Field(
        description="Next scheduled health check",
    )
    check_duration_seconds: float = Field(description="Health check duration")


class SystemAlertResponse(DomainBaseModel):
    """Response model for system alerts."""

    alert_id: UUID = Field(description="Unique alert identifier")
    severity: AlertSeverity = Field(description="Alert severity level")
    title: str = Field(description="Alert title")
    description: str = Field(description="Alert description")
    source: str = Field(description="Alert source component")
    triggered_at: datetime = Field(description="Alert trigger timestamp")
    acknowledged_at: datetime | None = Field(
        description="Alert acknowledgment timestamp",
    )
    resolved_at: datetime | None = Field(description="Alert resolution timestamp")
    acknowledged_by: str | None = Field(description="User who acknowledged the alert")
    resolved_by: str | None = Field(description="User who resolved the alert")
    tags: list[str] = Field(description="Alert tags")
    affected_services: list[ServiceType] = Field(
        description="Services affected by this alert",
    )
    metrics: dict[str, Any] = Field(description="Metrics associated with the alert")
    recommended_actions: list[str] = Field(
        description="Recommended actions to resolve alert",
    )
    escalation_level: int = Field(description="Current escalation level")
    notification_count: int = Field(description="Number of notifications sent")
    metadata: dict[str, Any] = Field(description="Additional alert metadata")


class SystemMetricsResponse(DomainBaseModel):
    """Response model for system metrics."""

    timestamp: datetime = Field(description="Metrics collection timestamp")
    system_metrics: dict[str, Any] = Field(description="System-level metrics")
    service_metrics: dict[str, dict[str, Any]] = Field(
        description="Per-service metrics",
    )
    resource_metrics: dict[str, Any] = Field(description="Resource utilization metrics")
    performance_metrics: dict[str, Any] = Field(description="Performance metrics")
    business_metrics: dict[str, Any] = Field(description="Business-related metrics")
    custom_metrics: dict[str, Any] = Field(description="Custom application metrics")
    historical_summary: dict[str, Any] = Field(description="Historical metrics summary")
    trends: dict[str, Any] = Field(description="Metric trends and analysis")
    anomalies: list[dict[str, Any]] = Field(description="Detected metric anomalies")
    collection_duration_ms: float = Field(description="Metrics collection duration")


# --- List and Filter Models ---


class SystemListResponse(DomainBaseModel):
    """Response model for system list operations."""

    systems: list[SystemStatusResponse] = Field(description="List of systems")
    total_count: int = Field(description="Total number of systems")
    healthy_count: int = Field(description="Number of healthy systems")
    degraded_count: int = Field(description="Number of degraded systems")
    unhealthy_count: int = Field(description="Number of unhealthy systems")
    maintenance_count: int = Field(description="Number of systems in maintenance")


class SystemFilterRequest(DomainBaseModel):
    """Request model for filtering system information."""

    status: SystemStatus | None = Field(
        default=None,
        description="Filter by system status",
    )
    maintenance_mode: MaintenanceMode | None = Field(
        default=None,
        description="Filter by maintenance mode",
    )
    service_type: ServiceType | None = Field(
        default=None,
        description="Filter by service type",
    )
    alert_severity: AlertSeverity | None = Field(
        default=None,
        description="Filter by alert severity",
    )
    environment: str | None = Field(
        default=None,
        description="Filter by environment",
    )
    has_alerts: bool | None = Field(
        default=None,
        description="Filter by presence of alerts",
    )
    uptime_min_hours: int | None = Field(
        default=None,
        ge=0,
        description="Filter by minimum uptime in hours",
    )
    last_backup_within_hours: int | None = Field(
        default=None,
        ge=0,
        description="Filter by last backup within hours",
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Page number",
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Page size",
    )
    sort_by: str = Field(
        default="status",
        description="Sort field",
    )
    sort_order: str = Field(
        default="asc",
        pattern="^(asc|desc)$",
        description="Sort order",
    )
