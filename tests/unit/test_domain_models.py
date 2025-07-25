"""Tests for domain models - Maximum coverage with minimal dependencies."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from flext_api.models.auth import (
    LoginRequest,
    RegisterRequest,
    UserAPI,
)
from flext_api.models.pipeline import (
    PipelineCreateRequest,
    PipelineExecutionRequest,
    PipelineListResponse,
    PipelineResponse,
    PipelineStatus,
    PipelineUpdateRequest,
)
from flext_api.models.plugin import (
    PluginInstallRequest,
    PluginListResponse,
    PluginResponse,
    PluginSource,
    PluginStatus,
    PluginType,
    PluginUpdateRequest,
)
from flext_api.models.system import (
    MaintenanceMode,
    MaintenanceRequest,
    SystemBackupRequest,
    SystemMetricsResponse,
    SystemStatusResponse,
    SystemStatusType,
)


class TestPipelineModels:
    """Test pipeline domain models."""

    def test_pipeline_create_request_valid(self) -> None:
        """Test valid pipeline creation request."""
        request = PipelineCreateRequest(
            name="test-pipeline",
            description="Test pipeline",
            extractor="tap-postgres",
            loader="target-snowflake",
            configuration={"host": "localhost"},
        )

        assert request.name == "test-pipeline"
        assert request.extractor == "tap-postgres"
        assert request.loader == "target-snowflake"
        assert request.configuration == {"host": "localhost"}

    def test_pipeline_create_request_validation(self) -> None:
        """Test pipeline creation request validation."""
        # Test validation passes for valid data
        request = PipelineCreateRequest(
            name="valid-name",
            description="Test",
            extractor="tap-test",
            loader="target-test",
        )
        result = request.validate_business_rules()
        assert result.is_success

    def test_pipeline_update_request_partial(self) -> None:
        """Test pipeline update with partial data."""
        request = PipelineUpdateRequest(
            description="Updated description",
        )

        assert request.description == "Updated description"
        assert request.configuration is None

    def test_pipeline_execution_request(self) -> None:
        """Test pipeline execution request."""
        request = PipelineExecutionRequest(
            pipeline_id=str(uuid4()),
            parameters={"full_refresh": True},
        )

        assert request.parameters == {"full_refresh": True}

    def test_pipeline_response(self) -> None:
        """Test pipeline response model."""
        pipeline_id = str(uuid4())
        response = PipelineResponse(
            id=pipeline_id,
            name="test-pipeline",
            extractor="tap-postgres",
            loader="target-snowflake",
            status=PipelineStatus.ACTIVE,
            created_at=datetime.now(UTC),
            configuration={},
        )

        assert response.id == pipeline_id
        assert response.name == "test-pipeline"
        assert response.status == PipelineStatus.ACTIVE

    def test_pipeline_list_response(self) -> None:
        """Test pipeline list response."""
        pipelines = [
            PipelineResponse(
                id=str(uuid4()),
                name="pipeline1",
                extractor="tap-test",
                loader="target-test",
                status=PipelineStatus.ACTIVE,
                created_at=datetime.now(UTC),
                configuration={},
            ),
        ]

        response = PipelineListResponse(
            pipelines=pipelines,
            total_count=1,
            page=1,
            page_size=20,
        )

        assert len(response.pipelines) == 1
        assert response.total_count == 1


class TestPluginModels:
    """Test plugin domain models."""

    def test_plugin_install_request(self) -> None:
        """Test plugin installation request."""
        request = PluginInstallRequest(
            plugin_name="tap-test",
            plugin_version="1.0.0",
            source=PluginSource.HUB,
            configuration={"setting": "value"},
        )

        assert request.plugin_name == "tap-test"
        assert request.plugin_version == "1.0.0"
        assert request.source == PluginSource.HUB

    def test_plugin_install_request_validation(self) -> None:
        """Test plugin install request validation."""
        request = PluginInstallRequest(
            plugin_name="valid-plugin",
            plugin_version="1.0.0",
            source=PluginSource.HUB,
        )
        result = request.validate_business_rules()
        assert result.is_success

    def test_plugin_update_request(self) -> None:
        """Test plugin update request."""
        request = PluginUpdateRequest(
            version="2.0.0",
            force_update=True,
        )

        assert request.version == "2.0.0"
        assert request.force_update is True

    def test_plugin_response(self) -> None:
        """Test plugin response model."""
        response = PluginResponse(
            plugin_id=uuid4(),
            name="tap-test",
            plugin_type=PluginType.EXTRACTOR,
            version="1.0.0",
            description="Test plugin",
            plugin_status=PluginStatus.INSTALLED,
            source=PluginSource.HUB,
            configuration={},
            updated_at=datetime.now(UTC).isoformat(),
        )

        assert response.name == "tap-test"
        assert response.plugin_type == PluginType.TAP
        assert response.plugin_status == PluginStatus.INSTALLED

    def test_plugin_list_response(self) -> None:
        """Test plugin list response."""
        plugins = [
            PluginResponse(
                plugin_id=uuid4(),
                name="tap-test",
                plugin_type=PluginType.EXTRACTOR,
                version="1.0.0",
                description="Test plugin",
                plugin_status=PluginStatus.INSTALLED,
                source=PluginSource.HUB,
                configuration={},
                updated_at=datetime.now(UTC).isoformat(),
            ),
        ]

        response = PluginListResponse(
            items=plugins,
            total_count=1,
            installed_count=1,
            page=1,
            page_size=20,
            has_next=False,
            has_previous=False,
        )

        assert len(response.items) == 1
        assert response.installed_count == 1


class TestAuthModels:
    """Test authentication domain models."""

    def test_login_request(self) -> None:
        """Test login request model."""
        request = LoginRequest(
            username="testuser",
            password="testpass",
        )

        assert request.username == "testuser"
        assert request.password == "testpass"

    def test_login_request_validation(self) -> None:
        """Test login request validation."""
        request = LoginRequest(
            username="validuser",
            password="validpass123",
        )
        result = request.validate_business_rules()
        assert result.is_success

    def test_register_request(self) -> None:
        """Test user registration request."""
        request = RegisterRequest(
            username="newuser",
            email="newuser@example.com",
            password="newpass123",
        )

        assert request.username == "newuser"
        assert request.email == "newuser@example.com"
        assert request.password == "newpass123"

    def test_register_request_validation(self) -> None:
        """Test register request validation."""
        request = RegisterRequest(
            username="validuser",
            email="valid@example.com",
            password="validpass123",
        )
        result = request.validate_business_rules()
        assert result.is_success

    def test_user_api_model(self) -> None:
        """Test UserAPI model."""
        user = UserAPI(
            username="testuser",
            roles=["user", "admin"],
            is_active=True,
            is_admin=True,
            data={},
        )

        assert user.username == "testuser"
        assert "admin" in user.roles
        assert user.is_admin is True

    def test_user_has_role(self) -> None:
        """Test user role checking."""
        user = UserAPI(
            username="testuser",
            roles=["user", "moderator"],
            is_active=True,
            is_admin=False,
            data={},
        )

        assert user.has_role("user") is True
        assert user.has_role("admin") is False

    def test_user_is_authorized(self) -> None:
        """Test user authorization checking."""
        user = UserAPI(
            username="testuser",
            roles=["user", "moderator"],
            is_active=True,
            is_admin=False,
            data={},
        )

        assert user.is_authorized(["user"]) is True
        assert user.is_authorized(["admin"]) is False
        assert user.is_authorized(["user", "moderator"]) is True


class TestSystemModels:
    """Test system domain models."""

    def test_system_status_response(self) -> None:
        """Test system status response."""
        response = SystemStatusResponse(
            system_status=SystemStatusType.HEALTHY,
            version="1.0.0",
            uptime_seconds=3600,
            maintenance_mode=MaintenanceMode.NONE,
            services=[],
            resource_usage={},
            performance_metrics={},
            active_alerts=[],
            plugin_count=5,
            active_pipelines=2,
            data={},
        )

        assert response.system_status == SystemStatusType.HEALTHY
        assert response.version == "1.0.0"
        assert response.uptime_seconds == 3600

    def test_maintenance_request(self) -> None:
        """Test maintenance request."""
        request = MaintenanceRequest(
            mode=MaintenanceMode.PLANNED,
            reason="System update",
            estimated_duration_minutes=30,
            affected_services=["api", "grpc"],
            notification_message="System maintenance in progress",
        )

        assert request.mode == MaintenanceMode.PLANNED
        assert request.reason == "System update"
        assert "api" in request.affected_services

    def test_maintenance_request_validation(self) -> None:
        """Test maintenance request validation."""
        request = MaintenanceRequest(
            mode=MaintenanceMode.EMERGENCY,
            reason="Critical security update",
            estimated_duration_minutes=60,
            affected_services=["api"],
            notification_message="Emergency maintenance",
        )
        result = request.validate_business_rules()
        assert result.is_success

    def test_backup_request(self) -> None:
        """Test system backup request."""
        request = SystemBackupRequest(
            backup_type="full",
            include_data=True,
            include_configuration=True,
            retention_days=30,
            description="Weekly full backup",
        )

        assert request.backup_type == "full"
        assert request.include_data is True
        assert request.retention_days == 30

    def test_backup_request_validation(self) -> None:
        """Test backup request validation."""
        request = SystemBackupRequest(
            backup_type="incremental",
            include_data=True,
            include_configuration=False,
            retention_days=7,
        )
        result = request.validate_business_rules()
        assert result.is_success

    def test_metrics_response(self) -> None:
        """Test system metrics response."""
        response = SystemMetricsResponse(
            metric_name="cpu_usage",
            metric_value=45.2,
            metric_unit="%",
            timestamp=datetime.now(UTC),
            tags={"host": "api-server-1"},
            data={},
        )

        assert response.metric_name == "cpu_usage"
        assert response.metric_value == 45.2
        assert response.metric_unit == "%"

    def test_enum_values(self) -> None:
        """Test enum value consistency."""
        # Test SystemStatusType enum
        assert SystemStatusType.HEALTHY == "healthy"
        assert SystemStatusType.DEGRADED == "degraded"
        assert SystemStatusType.UNHEALTHY == "unhealthy"

        # Test MaintenanceMode enum
        assert MaintenanceMode.NONE == "none"
        assert MaintenanceMode.PLANNED == "planned"
        assert MaintenanceMode.EMERGENCY == "emergency"

        # Test PipelineStatus enum (alias for EntityStatus)
        assert PipelineStatus.ACTIVE == "active"
        assert PipelineStatus.INACTIVE == "inactive"
        assert PipelineStatus.PENDING == "pending"

        # Test PluginStatus enum
        assert PluginStatus.AVAILABLE == "available"
        assert PluginStatus.INSTALLED == "installed"
        assert PluginStatus.RUNNING == "running"
