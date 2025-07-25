"""Comprehensive tests for all domain entities with 100% coverage.

Tests cover all classes, methods, properties, and edge cases for complete coverage.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

# Import PluginType separately since it's not in __all__
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
    """Test Pipeline domain entity."""

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

    def test_pipeline_name_validation(self) -> None:
        """Test pipeline name validation."""
        with pytest.raises(ValueError, match="String should have at least 1 character"):
            Pipeline(entity_id=str(uuid4()), name="")

    def test_pipeline_name_max_length(self) -> None:
        """Test pipeline name maximum length validation."""
        long_name = "x" * 256  # Over the 255 character limit
        with pytest.raises(
            ValueError,
            match="String should have at most 255 characters",
        ):
            Pipeline(entity_id=str(uuid4()), name=long_name)

    def test_pipeline_description_max_length(self) -> None:
        """Test pipeline description maximum length validation."""
        long_desc = "x" * 1001  # Over the 1000 character limit
        with pytest.raises(
            ValueError,
            match="String should have at most 1000 characters",
        ):
            Pipeline(
                entity_id=str(uuid4()),
                name="test",
                description=long_desc,
            )

    def test_pipeline_default_values(self) -> None:
        """Test pipeline default values."""
        pipeline = Pipeline(entity_id=str(uuid4()), name="test")
        assert pipeline.description is None
        assert pipeline.config == {}
        assert pipeline.tags == []
        assert pipeline.is_active is True

    def test_pipeline_activate_deactivate(self) -> None:
        """Test pipeline activation and deactivation."""
        pipeline = Pipeline(entity_id=str(uuid4()), name="test", is_active=False)

        activated = pipeline.activate()
        assert activated.is_active is True
        assert activated.entity_id == pipeline.entity_id

        deactivated = activated.deactivate()
        assert deactivated.is_active is False


class TestPipelineExecution:
    """Test PipelineExecution domain entity."""

    def test_pipeline_execution_creation(self) -> None:
        """Test creating a pipeline execution."""
        execution = PipelineExecution(
            entity_id=str(uuid4()),
            pipeline_id=str(uuid4()),
            status=PipelineStatus.RUNNING,
            started_at=datetime.now(UTC),
        )
        assert execution.pipeline_id is not None
        assert execution.status == PipelineStatus.RUNNING
        assert execution.started_at is not None

    def test_pipeline_execution_complete(self) -> None:
        """Test completing a pipeline execution."""
        execution = PipelineExecution(
            entity_id=str(uuid4()),
            pipeline_id=str(uuid4()),
            status=PipelineStatus.RUNNING,
            started_at=datetime.now(UTC),
        )

        completed = execution.complete()
        assert completed.status == PipelineStatus.SUCCESS
        assert completed.finished_at is not None

    def test_pipeline_execution_fail(self) -> None:
        """Test failing a pipeline execution."""
        execution = PipelineExecution(
            entity_id=str(uuid4()),
            pipeline_id=str(uuid4()),
            status=PipelineStatus.RUNNING,
            started_at=datetime.now(UTC),
        )

        failed = execution.fail("Test error")
        assert failed.status == PipelineStatus.FAILED
        assert failed.error_message == "Test error"
        assert failed.finished_at is not None

    def test_pipeline_execution_duration_property(self) -> None:
        """Test pipeline execution duration calculation."""
        start_time = datetime.now(UTC)
        execution = PipelineExecution(
            entity_id=str(uuid4()),
            pipeline_id=str(uuid4()),
            status=PipelineStatus.SUCCESS,
            started_at=start_time,
            finished_at=start_time.replace(second=start_time.second + 30),
        )

        duration = execution.duration
        assert duration is not None
        assert duration.total_seconds() == 30

    def test_pipeline_execution_duration_no_finish(self) -> None:
        """Test pipeline execution duration when not finished."""
        execution = PipelineExecution(
            entity_id=str(uuid4()),
            pipeline_id=str(uuid4()),
            status=PipelineStatus.RUNNING,
            started_at=datetime.now(UTC),
        )

        assert execution.duration is None

    def test_pipeline_execution_domain_validation(self) -> None:
        """Test pipeline execution domain rule validation."""
        execution = PipelineExecution(
            entity_id=str(uuid4()),
            pipeline_id=str(uuid4()),
            status=PipelineStatus.RUNNING,
            started_at=datetime.now(UTC),
            success_count=-1,
        )

        with pytest.raises(
            ValueError,
            match="Success/failure counts cannot be negative",
        ):
            execution.validate_domain_rules()


class TestPlugin:
    """Test Plugin domain entity."""

    def test_plugin_creation(self) -> None:
        """Test creating a plugin with valid data."""
        plugin = Plugin(
            entity_id=str(uuid4()),
            name="test-plugin",
            plugin_type=PluginType.EXTRACTOR,
        )
        assert plugin.name == "test-plugin"
        assert plugin.plugin_type == PluginType.EXTRACTOR
        assert plugin.enabled is True

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

    def test_plugin_metadata_defaults(self) -> None:
        """Test plugin metadata default values."""
        metadata = PluginMetadata(name="test", version="1.0.0")
        assert metadata.description is None
        assert metadata.author is None
        assert metadata.capabilities == []


class TestAPIPipeline:
    """Test FlextAPIPipeline domain entity."""

    def test_api_pipeline_creation(self) -> None:
        """Test creating an API pipeline."""
        pipeline = FlextAPIPipeline(
            entity_id=str(uuid4()),
            name="api-pipeline",
            pipeline_id=str(uuid4()),
        )
        assert pipeline.name == "api-pipeline"
        assert pipeline.pipeline_id is not None


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
        assert PipelineStatus.PENDING == "pending"
        assert PipelineStatus.RUNNING == "running"
        assert PipelineStatus.SUCCESS == "success"
        assert PipelineStatus.FAILED == "failed"
        assert PipelineStatus.CANCELLED == "cancelled"

    def test_plugin_type_enum(self) -> None:
        """Test PluginType enum values."""
        assert PluginType.EXTRACTOR == "extractor"
        assert PluginType.LOADER == "loader"
        assert PluginType.TRANSFORMER == "transformer"
        assert PluginType.UTILITY == "utility"
