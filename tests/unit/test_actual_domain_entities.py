"""Tests for actual domain entities with 100% coverage.

Tests only the classes and methods that actually exist in the domain entities.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from flext_api.domain.entities import (
    APIResponseLog,
    FlextApiEndpoint,
    FlextAPIPipeline,
    FlextAPIRequest,
    FlextApiRequest,
    FlextApiResponse,
    HttpMethod,
    Pipeline,
    PipelineExecution,
    PipelineStatus,
    Plugin,
    PluginMetadata,
    PluginType,
)


class TestPipeline:
    """Test basic Pipeline domain entity."""

    def test_pipeline_creation(self) -> None:
        """Test creating a pipeline with valid data."""
        pipeline = Pipeline(
            entity_id=str(uuid4()),
            name="test-pipeline",
            description="A test pipeline",
        )
        assert pipeline.name == "test-pipeline"
        assert pipeline.description == "A test pipeline"
        assert pipeline.entity_id is not None

    def test_pipeline_default_description(self) -> None:
        """Test pipeline with default description."""
        pipeline = Pipeline(
            entity_id=str(uuid4()),
            name="test-pipeline",
        )
        assert pipeline.name == "test-pipeline"
        assert pipeline.description == ""  # Default from entities.py

    def test_pipeline_name_validation(self) -> None:
        """Test pipeline name validation."""
        pipeline = Pipeline(
            entity_id=str(uuid4()),
            name="",  # Empty name
        )
        with pytest.raises(ValueError, match="Pipeline name cannot be empty"):
            pipeline.validate_domain_rules()

    def test_pipeline_name_max_length(self) -> None:
        """Test pipeline name maximum length validation."""
        long_name = "x" * 256  # Over the 255 character limit
        with pytest.raises(
            ValueError,
            match="String should have at most 255 characters",
        ):
            Pipeline(entity_id=str(uuid4()), name=long_name)


class TestPipelineExecution:
    """Test PipelineExecution domain entity."""

    def test_pipeline_execution_creation(self) -> None:
        """Test creating a pipeline execution."""
        execution = PipelineExecution(
            entity_id=str(uuid4()),
            pipeline_id=str(uuid4()),
        )
        assert execution.pipeline_id is not None
        assert execution.status == "pending"  # Default value

    def test_pipeline_execution_custom_status(self) -> None:
        """Test creating pipeline execution with custom status."""
        execution = PipelineExecution(
            entity_id=str(uuid4()),
            pipeline_id=str(uuid4()),
            status="running",
        )
        assert execution.status == "running"

    def test_pipeline_execution_validation_empty_pipeline_id(self) -> None:
        """Test validation fails with empty pipeline ID."""
        execution = PipelineExecution(
            entity_id=str(uuid4()),
            pipeline_id="",  # Empty
            status="running",
        )
        with pytest.raises(ValueError, match="Pipeline ID cannot be empty"):
            execution.validate_domain_rules()

    def test_pipeline_execution_validation_empty_status(self) -> None:
        """Test validation fails with empty status."""
        execution = PipelineExecution(
            entity_id=str(uuid4()),
            pipeline_id=str(uuid4()),
            status="",  # Empty
        )
        with pytest.raises(ValueError, match="Status cannot be empty"):
            execution.validate_domain_rules()


class TestPluginMetadata:
    """Test PluginMetadata value object."""

    def test_plugin_metadata_creation(self) -> None:
        """Test creating plugin metadata."""
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            description="Test description",
        )
        assert metadata.name == "test-plugin"
        assert metadata.version == "1.0.0"
        assert metadata.description == "Test description"

    def test_plugin_metadata_default_description(self) -> None:
        """Test plugin metadata with default description."""
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
        )
        assert metadata.name == "test-plugin"
        assert metadata.version == "1.0.0"
        assert metadata.description == ""  # Default value


class TestAPIPipeline:
    """Test FlextAPIPipeline domain entity."""

    def test_api_pipeline_creation(self) -> None:
        """Test creating an API pipeline."""
        pipeline = FlextAPIPipeline(
            entity_id=str(uuid4()),
            name="api-pipeline",
        )
        assert pipeline.name == "api-pipeline"
        assert pipeline.pipeline_status == PipelineStatus.ACTIVE  # Default
        assert pipeline.method == HttpMethod.GET  # Default
        assert pipeline.auth_required is True  # Default
        assert pipeline.rate_limit == 100  # Default

    def test_api_pipeline_custom_values(self) -> None:
        """Test creating API pipeline with custom values."""
        pipeline = FlextAPIPipeline(
            entity_id=str(uuid4()),
            name="custom-pipeline",
            description="Custom description",
            pipeline_status=PipelineStatus.INACTIVE,
            method=HttpMethod.POST,
            auth_required=False,
            rate_limit=50,
        )
        assert pipeline.name == "custom-pipeline"
        assert pipeline.description == "Custom description"
        assert pipeline.pipeline_status == PipelineStatus.INACTIVE
        assert pipeline.method == HttpMethod.POST
        assert pipeline.auth_required is False
        assert pipeline.rate_limit == 50

    def test_api_pipeline_success_rate_zero_runs(self) -> None:
        """Test success rate calculation with zero runs."""
        pipeline = FlextAPIPipeline(entity_id=str(uuid4()), name="test")
        assert pipeline.success_rate == 0.0

    def test_api_pipeline_success_rate_with_runs(self) -> None:
        """Test success rate calculation with runs."""
        pipeline = FlextAPIPipeline(
            entity_id=str(uuid4()),
            name="test",
            run_count=10,
            success_count=8,
        )
        assert pipeline.success_rate == 80.0

    def test_api_pipeline_is_active_property(self) -> None:
        """Test is_pipeline_active property."""
        active_pipeline = FlextAPIPipeline(
            entity_id=str(uuid4()),
            name="active",
            pipeline_status=PipelineStatus.ACTIVE,
        )
        inactive_pipeline = FlextAPIPipeline(
            entity_id=str(uuid4()),
            name="inactive",
            pipeline_status=PipelineStatus.INACTIVE,
        )
        assert active_pipeline.is_pipeline_active is True
        assert inactive_pipeline.is_pipeline_active is False

    def test_api_pipeline_record_successful_execution(self) -> None:
        """Test recording successful execution."""
        pipeline = FlextAPIPipeline(entity_id=str(uuid4()), name="test")

        updated = pipeline.record_execution(success=True)
        assert updated.run_count == 1
        assert updated.success_count == 1
        assert updated.failure_count == 0
        assert updated.last_run_at is not None

    def test_api_pipeline_record_failed_execution(self) -> None:
        """Test recording failed execution."""
        pipeline = FlextAPIPipeline(entity_id=str(uuid4()), name="test")

        updated = pipeline.record_execution(success=False)
        assert updated.run_count == 1
        assert updated.success_count == 0
        assert updated.failure_count == 1
        assert updated.last_run_at is not None

    def test_api_pipeline_validation_empty_name(self) -> None:
        """Test validation fails with empty name."""
        pipeline = FlextAPIPipeline(entity_id=str(uuid4()), name="")
        with pytest.raises(ValueError, match="Pipeline name cannot be empty"):
            pipeline.validate_domain_rules()

    def test_api_pipeline_validation_negative_counts(self) -> None:
        """Test validation fails with negative counts."""
        pipeline = FlextAPIPipeline(
            entity_id=str(uuid4()),
            name="test",
            run_count=-1,
        )
        with pytest.raises(ValueError, match="Run count cannot be negative"):
            pipeline.validate_domain_rules()

    def test_api_pipeline_validation_negative_success_count(self) -> None:
        """Test validation fails with negative success count."""
        pipeline = FlextAPIPipeline(
            entity_id=str(uuid4()),
            name="test",
            success_count=-1,
        )
        with pytest.raises(
            ValueError,
            match="Success/failure counts cannot be negative",
        ):
            pipeline.validate_domain_rules()

    def test_api_pipeline_validation_zero_rate_limit(self) -> None:
        """Test validation fails with zero rate limit."""
        pipeline = FlextAPIPipeline(
            entity_id=str(uuid4()),
            name="test",
            rate_limit=0,
        )
        with pytest.raises(ValueError, match="Rate limit must be positive"):
            pipeline.validate_domain_rules()


class TestPlugin:
    """Test Plugin domain entity."""

    def test_plugin_creation(self) -> None:
        """Test creating a plugin with valid data."""
        plugin = Plugin(
            name="test-plugin",
            plugin_type=PluginType.EXTRACTOR,
        )
        assert plugin.name == "test-plugin"
        assert plugin.plugin_type == PluginType.EXTRACTOR
        assert plugin.enabled is True  # Default

    def test_plugin_type_properties(self) -> None:
        """Test plugin type checking properties."""
        extractor = Plugin(
            entity_id=str(uuid4()),
            name="ext",
            plugin_type=PluginType.EXTRACTOR,
        )
        loader = Plugin(
            entity_id=str(uuid4()),
            name="load",
            plugin_type=PluginType.LOADER,
        )
        transformer = Plugin(
            entity_id=str(uuid4()),
            name="trans",
            plugin_type=PluginType.TRANSFORMER,
        )
        Plugin(entity_id=str(uuid4()), name="util", plugin_type=PluginType.UTILITY)

        assert extractor.is_extractor is True
        assert extractor.is_loader is False
        assert extractor.is_transformer is False

        assert loader.is_extractor is False
        assert loader.is_loader is True
        assert loader.is_transformer is False

        assert transformer.is_extractor is False
        assert transformer.is_loader is False
        assert transformer.is_transformer is True

    def test_plugin_config_validation(self) -> None:
        """Test plugin config validation handles None."""
        plugin = Plugin(
            entity_id=str(uuid4()),
            name="test",
            plugin_config=None,
        )
        assert plugin.plugin_config == {}

    def test_plugin_version_validation(self) -> None:
        """Test plugin version format validation."""
        plugin = Plugin(
            entity_id=str(uuid4()),
            name="test",
            plugin_version="invalid",
        )

        with pytest.raises(
            ValueError,
            match="Plugin version must follow semver format",
        ):
            plugin.validate_domain_rules()

    def test_plugin_name_validation(self) -> None:
        """Test plugin name validation."""
        plugin = Plugin(
            entity_id=str(uuid4()),
            name="",
        )

        with pytest.raises(ValueError, match="Plugin name cannot be empty"):
            plugin.validate_domain_rules()


class TestAPIRequest:
    """Test FlextAPIRequest domain entity."""

    def test_api_request_creation(self) -> None:
        """Test creating an API request."""
        request = FlextAPIRequest(
            entity_id=str(uuid4()),
            request_id="req-123",
            endpoint="/api/test",
            method="GET",
        )
        assert request.request_id == "req-123"
        assert request.endpoint == "/api/test"
        assert request.method == "GET"

    def test_api_request_start_processing(self) -> None:
        """Test starting request processing."""
        request = FlextAPIRequest(
            entity_id=str(uuid4()),
            request_id="req-123",
            endpoint="/api/test",
            method="GET",
        )

        processing = request.start_processing()
        assert processing.processing_started_at is not None
        assert processing.request_id == request.request_id

    def test_api_request_validation(self) -> None:
        """Test API request domain validation."""
        # Empty request ID
        request = FlextAPIRequest(
            entity_id=str(uuid4()),
            request_id="",
            endpoint="/api/test",
            method="GET",
        )
        with pytest.raises(ValueError, match="Request ID cannot be empty"):
            request.validate_domain_rules()

        # Empty endpoint
        request = FlextAPIRequest(
            entity_id=str(uuid4()),
            request_id="req-123",
            endpoint="",
            method="GET",
        )
        with pytest.raises(ValueError, match="Endpoint cannot be empty"):
            request.validate_domain_rules()


class TestAPIResponseLog:
    """Test APIResponseLog domain entity."""

    def test_api_response_creation(self) -> None:
        """Test creating an API response log."""
        response = APIResponseLog(
            entity_id=str(uuid4()),
            request_id="req-123",
            response_id="resp-456",
            status_code=200,
        )
        assert response.request_id == "req-123"
        assert response.response_id == "resp-456"
        assert response.status_code == 200

    def test_api_response_status_properties(self) -> None:
        """Test API response status checking properties."""
        success = APIResponseLog(
            entity_id=str(uuid4()),
            request_id="req-1",
            response_id="resp-1",
            status_code=200,
        )

        client_error = APIResponseLog(
            entity_id=str(uuid4()),
            request_id="req-2",
            response_id="resp-2",
            status_code=404,
        )

        server_error = APIResponseLog(
            entity_id=str(uuid4()),
            request_id="req-3",
            response_id="resp-3",
            status_code=500,
        )

        assert success.is_success is True
        assert success.is_client_error is False
        assert success.is_server_error is False

        assert client_error.is_success is False
        assert client_error.is_client_error is True
        assert client_error.is_server_error is False

        assert server_error.is_success is False
        assert server_error.is_client_error is False
        assert server_error.is_server_error is True

    def test_api_response_mark_as_error(self) -> None:
        """Test marking response as error."""
        response = APIResponseLog(
            entity_id=str(uuid4()),
            request_id="req-123",
            response_id="resp-456",
            status_code=200,
        )

        error_response = response.mark_as_error("ERR_001", "Test error")
        assert error_response.error_code == "ERR_001"
        assert error_response.error_message == "Test error"

    def test_api_response_set_processing_duration(self) -> None:
        """Test setting processing duration."""
        start_time = datetime.now(UTC)
        response = APIResponseLog(
            entity_id=str(uuid4()),
            request_id="req-123",
            response_id="resp-456",
            status_code=200,
            response_timestamp=start_time.replace(second=start_time.second + 2),
        )

        timed_response = response.set_processing_duration(start_time)
        assert timed_response.processing_duration_ms == 2000

    def test_api_response_validation(self) -> None:
        """Test API response domain validation."""
        # Invalid status code
        response = APIResponseLog(
            entity_id=str(uuid4()),
            request_id="req-123",
            response_id="resp-456",
            status_code=999,  # Invalid
        )
        with pytest.raises(ValueError, match="Status code must be between 100 and 599"):
            response.validate_domain_rules()


class TestFlextApiEndpoint:
    """Test FlextApiEndpoint domain entity."""

    def test_endpoint_creation(self) -> None:
        """Test creating an API endpoint."""
        endpoint = FlextApiEndpoint(
            entity_id=str(uuid4()),
            name="test-endpoint",
            path="/api/test",
            method=HttpMethod.GET,
        )
        assert endpoint.name == "test-endpoint"
        assert endpoint.path == "/api/test"
        assert endpoint.method == HttpMethod.GET
        assert endpoint.is_active is True

    def test_endpoint_activate_deactivate(self) -> None:
        """Test endpoint activation and deactivation."""
        endpoint = FlextApiEndpoint(
            entity_id=str(uuid4()),
            name="test",
            path="/test",
            method=HttpMethod.GET,
            is_active=False,
        )

        activated = endpoint.activate()
        assert activated.is_active is True

        deactivated = activated.deactivate()
        assert deactivated.is_active is False

    def test_endpoint_validation(self) -> None:
        """Test endpoint domain validation."""
        # Path must start with /
        endpoint = FlextApiEndpoint(
            entity_id=str(uuid4()),
            name="test",
            path="invalid",  # No leading slash
            method=HttpMethod.GET,
        )
        with pytest.raises(ValueError, match="Endpoint path must start with '/'"):
            endpoint.validate_domain_rules()


class TestFlextApiRequest:
    """Test FlextApiRequest domain entity."""

    def test_flext_api_request_creation(self) -> None:
        """Test creating a FlextApiRequest."""
        request = FlextApiRequest(
            entity_id=str(uuid4()),
            request_id="req-123",
            endpoint="/api/test",
            method=HttpMethod.GET,
        )
        assert request.endpoint == "/api/test"
        assert request.method == HttpMethod.GET

    def test_flext_api_request_business_validation(self) -> None:
        """Test business rule validation."""
        request = FlextApiRequest(
            entity_id=str(uuid4()),
            request_id="req-123",
            endpoint="invalid",  # No leading slash
            method=HttpMethod.GET,
        )

        result = request.validate_business_rules()
        assert not result.success
        assert "must start with '/'" in result.error


class TestFlextApiResponse:
    """Test FlextApiResponse domain entity."""

    def test_flext_api_response_creation(self) -> None:
        """Test creating a FlextApiResponse."""
        response = FlextApiResponse(
            success=True,
            data={"message": "test"},
        )
        assert response.success is True
        assert response.data == {"message": "test"}

    def test_add_api_metadata(self) -> None:
        """Test adding API metadata."""
        response = FlextApiResponse(success=True, data={})
        response.add_api_metadata("2.0")

        assert response.data["_api_version"] == "2.0"
        assert response.data["_response_type"] == "flext_api"

    def test_add_api_metadata_none_data(self) -> None:
        """Test adding API metadata when data is None."""
        response = FlextApiResponse(success=True, data=None)
        response.add_api_metadata()

        assert response.data is not None
        assert response.data["_api_version"] == "1.0"


class TestEnums:
    """Test enum classes."""

    def test_http_method_enum(self) -> None:
        """Test HttpMethod enum values."""
        assert HttpMethod.GET == "GET"
        assert HttpMethod.POST == "POST"
        assert HttpMethod.PUT == "PUT"
        assert HttpMethod.DELETE == "DELETE"
        assert HttpMethod.PATCH == "PATCH"
        assert HttpMethod.HEAD == "HEAD"
        assert HttpMethod.OPTIONS == "OPTIONS"

    def test_pipeline_status_enum(self) -> None:
        """Test PipelineStatus enum values."""
        assert PipelineStatus.ACTIVE == "active"
        assert PipelineStatus.INACTIVE == "inactive"
        assert PipelineStatus.DRAFT == "draft"
        assert PipelineStatus.ARCHIVED == "archived"
        assert PipelineStatus.FAILED == "failed"
        assert PipelineStatus.RUNNING == "running"
        assert PipelineStatus.SCHEDULED == "scheduled"

    def test_plugin_type_enum(self) -> None:
        """Test PluginType enum values."""
        assert PluginType.EXTRACTOR == "extractor"
        assert PluginType.LOADER == "loader"
        assert PluginType.TRANSFORMER == "transformer"
        assert PluginType.UTILITY == "utility"
