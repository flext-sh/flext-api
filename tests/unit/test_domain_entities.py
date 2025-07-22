"""Tests for domain entities."""

from __future__ import annotations

from uuid import uuid4

import pytest
from flext_core.domain.shared_types import PluginType

from flext_api.domain.entities import (
    APIPipeline,
    APIRequest,
    APIResponseLog,
    HttpMethod,
    PipelineCreatedEvent,
    PipelineExecutedEvent,
    PipelineStatus,
    Plugin,
    PluginRegisteredEvent,
    RequestLog,
    ResponseLog,
)


class TestPipelineStatus:
    """Test cases for PipelineStatus enum."""

    def test_pipeline_status_values(self) -> None:
        """Test pipeline status enum values."""
        assert PipelineStatus.ACTIVE.value == "active"
        assert PipelineStatus.INACTIVE.value == "inactive"
        assert PipelineStatus.RUNNING.value == "running"
        assert PipelineStatus.FAILED.value == "failed"

    def test_pipeline_status_iteration(self) -> None:
        """Test pipeline status enumeration."""
        statuses = list(PipelineStatus)
        assert len(statuses) == 7
        assert PipelineStatus.ACTIVE in statuses


class TestPluginType:
    """Test cases for PluginType enum."""

    def test_plugin_type_values(self) -> None:
        """Test plugin type enum values."""
        assert PluginType.EXTRACTOR.value == "extractor"
        assert PluginType.LOADER.value == "loader"
        assert PluginType.TRANSFORMER.value == "transformer"
        assert PluginType.UTILITY.value == "utility"
        assert PluginType.ORCHESTRATOR.value == "orchestrator"

    def test_plugin_type_iteration(self) -> None:
        """Test plugin type enumeration."""
        types = list(PluginType)
        assert len(types) == 5  # EXTRACTOR, LOADER, TRANSFORMER, ORCHESTRATOR, UTILITY
        assert PluginType.EXTRACTOR in types
        assert PluginType.LOADER in types
        assert PluginType.TRANSFORMER in types
        assert PluginType.UTILITY in types
        assert PluginType.ORCHESTRATOR in types


class TestHttpMethod:
    """Test cases for HttpMethod enum."""

    def test_http_method_values(self) -> None:
        """Test HTTP method enum values."""
        assert HttpMethod.GET == "GET"
        assert HttpMethod.POST == "POST"
        assert HttpMethod.PUT == "PUT"
        assert HttpMethod.PATCH == "PATCH"
        assert HttpMethod.DELETE == "DELETE"
        assert HttpMethod.HEAD == "HEAD"
        assert HttpMethod.OPTIONS == "OPTIONS"


class TestAPIPipeline:
    """Test cases for APIPipeline entity."""

    def test_pipeline_initialization(self) -> None:
        """Test pipeline initialization."""
        pipeline = APIPipeline(
            name="test-pipeline",
            description="Test pipeline",
            config={"input_file": "data.csv"},
            pipeline_status=PipelineStatus.ACTIVE,
            endpoint="/api/test",
            method=HttpMethod.POST,
            auth_required=True,
            rate_limit=50,
        )

        assert pipeline.name == "test-pipeline"
        assert pipeline.description == "Test pipeline"
        assert pipeline.config == {"input_file": "data.csv"}
        assert pipeline.pipeline_status == PipelineStatus.ACTIVE
        assert pipeline.endpoint == "/api/test"
        assert pipeline.method == HttpMethod.POST
        assert pipeline.auth_required is True
        assert pipeline.rate_limit == 50

    def test_pipeline_success_rate(self) -> None:
        """Test pipeline success rate calculation."""
        pipeline = APIPipeline(name="test-pipeline")

        # No runs yet
        assert pipeline.success_rate == 0.0

        # Record some executions
        pipeline.record_execution(success=True)
        pipeline.record_execution(success=True)
        pipeline.record_execution(success=False)

        assert pipeline.run_count == 3
        assert pipeline.success_count == 2
        assert pipeline.failure_count == 1
        assert pipeline.success_rate == 66.66666666666666

    def test_pipeline_is_active(self) -> None:
        """Test pipeline active status checking."""
        active_pipeline = APIPipeline(
            name="active-pipeline",
            pipeline_status=PipelineStatus.ACTIVE,
        )

        inactive_pipeline = APIPipeline(
            name="inactive-pipeline",
            pipeline_status=PipelineStatus.INACTIVE,
        )

        assert active_pipeline.is_pipeline_active is True
        assert inactive_pipeline.is_pipeline_active is False

    def test_pipeline_record_execution(self) -> None:
        """Test pipeline execution recording."""
        pipeline = APIPipeline(name="test-pipeline")

        # Initial state
        assert pipeline.run_count == 0
        assert pipeline.success_count == 0
        assert pipeline.failure_count == 0
        assert pipeline.last_run_at is None

        # Record successful execution
        pipeline.record_execution(success=True)

        assert pipeline.run_count == 1
        assert pipeline.success_count == 1
        assert pipeline.failure_count == 0
        assert pipeline.last_run_at is not None

    def test_pipeline_record_failed_execution(self) -> None:
        """Test pipeline failed execution recording."""
        pipeline = APIPipeline(name="test-pipeline")

        # Record successful execution first
        pipeline.record_execution(success=True)
        assert pipeline.run_count == 1

        # Record failed execution
        pipeline.record_execution(success=False)

        assert pipeline.run_count == 2
        assert pipeline.success_count == 1
        assert pipeline.failure_count == 1

    def test_pipeline_validation(self) -> None:
        """Test pipeline field validation."""
        # Valid pipeline
        pipeline = APIPipeline(name="valid-pipeline")
        assert pipeline.name == "valid-pipeline"

        # Test rate limit boundaries
        pipeline_low = APIPipeline(name="test", rate_limit=1)
        assert pipeline_low.rate_limit == 1

        pipeline_high = APIPipeline(name="test", rate_limit=10000)
        assert pipeline_high.rate_limit == 10000

        # Invalid rate limit should raise validation error
        with pytest.raises(
            ValueError,
            match="Input should be greater than or equal to 1",
        ):
            APIPipeline(name="test", rate_limit=0)

        with pytest.raises(
            ValueError,
            match="Input should be less than or equal to 10000",
        ):
            APIPipeline(name="test", rate_limit=10001)


class TestPlugin:
    """Test cases for Plugin entity."""

    def test_plugin_initialization(self) -> None:
        """Test plugin initialization."""
        plugin = Plugin(
            name="tap-csv",
            plugin_type=PluginType.EXTRACTOR,
            version="1.0.0",
            description="CSV tap plugin",
            plugin_config={"input_file": "data.csv"},
            enabled=True,
            author="Test Author",
            repository_url="https://github.com/test/tap-csv",
            api_version="1",
            endpoints=["/extract", "/schema"],
            permissions=["read:data"],
        )

        assert plugin.name == "tap-csv"
        assert plugin.plugin_type == PluginType.EXTRACTOR
        assert plugin.version == "1.0.0"
        assert plugin.description == "CSV tap plugin"
        assert plugin.plugin_config == {"input_file": "data.csv"}
        assert plugin.enabled is True
        assert plugin.author == "Test Author"
        assert plugin.repository_url == "https://github.com/test/tap-csv"
        assert plugin.api_version == "1"
        assert plugin.endpoints == ["/extract", "/schema"]
        assert plugin.permissions == ["read:data"]

    def test_plugin_type_properties(self) -> None:
        """Test plugin type checking properties."""
        tap_plugin = Plugin(name="tap-test", plugin_type=PluginType.EXTRACTOR)

        target_plugin = Plugin(name="target-test", plugin_type=PluginType.LOADER)

        transform_plugin = Plugin(
            name="transform-test",
            plugin_type=PluginType.TRANSFORMER,
        )

        assert tap_plugin.is_tap is True
        assert tap_plugin.is_target is False
        assert tap_plugin.is_transform is False

        assert target_plugin.is_tap is False
        assert target_plugin.is_target is True
        assert target_plugin.is_transform is False

        assert transform_plugin.is_tap is False
        assert transform_plugin.is_target is False
        assert transform_plugin.is_transform is True

    def test_plugin_version_validation(self) -> None:
        """Test plugin version validation."""
        # Valid versions
        valid_versions = ["1.0.0", "2.1.3", "0.1.0"]
        for version in valid_versions:
            plugin = Plugin(name="test-plugin", version=version)
            assert plugin.version == version

        # Invalid version format should raise validation error
        with pytest.raises(ValueError, match="String should match pattern"):
            Plugin(name="test-plugin", version="invalid-version")

        with pytest.raises(ValueError, match="String should match pattern"):
            Plugin(name="test-plugin", version="1.0")  # Missing patch version

    def test_plugin_defaults(self) -> None:
        """Test plugin default values."""
        plugin = Plugin(name="minimal-plugin")

        assert plugin.plugin_type == PluginType.UTILITY
        assert plugin.version == "0.7.0"
        assert plugin.plugin_config == {}
        assert plugin.enabled is True
        assert plugin.capabilities == []
        assert plugin.endpoints == []
        assert plugin.permissions == []
        assert plugin.api_version == "0"


class TestRequestLog:
    """Test cases for RequestLog entity."""

    def test_request_log_initialization(self) -> None:
        """Test request log initialization."""
        request_log = RequestLog(
            method=HttpMethod.POST,
            path="/api/v1/pipelines",
            query_params={"limit": "10"},
            headers={"Content-Type": "application/json"},
            body={"name": "test-pipeline"},
            ip_address="127.0.0.1",
            user_agent="TestClient/1.0",
            request_id="req-123",
            status_code=200,
            response_time_ms=150,
            response_size=1024,
        )

        assert request_log.method == HttpMethod.POST
        assert request_log.path == "/api/v1/pipelines"
        assert request_log.query_params == {"limit": "10"}
        assert request_log.headers == {"Content-Type": "application/json"}
        assert request_log.body == {"name": "test-pipeline"}
        assert request_log.ip_address == "127.0.0.1"
        assert request_log.user_agent == "TestClient/1.0"
        assert request_log.request_id == "req-123"
        assert request_log.status_code == 200
        assert request_log.response_time_ms == 150
        assert request_log.response_size == 1024

    def test_request_log_status_properties(self) -> None:
        """Test request log status checking properties."""
        successful_request = RequestLog(
            method=HttpMethod.GET,
            path="/api/v1/status",
            status_code=200,
        )

        client_error_request = RequestLog(
            method=HttpMethod.POST,
            path="/api/v1/invalid",
            status_code=404,
        )

        server_error_request = RequestLog(
            method=HttpMethod.GET,
            path="/api/v1/error",
            status_code=500,
        )

        assert successful_request.was_successful is True
        assert successful_request.was_client_error is False
        assert successful_request.was_server_error is False

        assert client_error_request.was_successful is False
        assert client_error_request.was_client_error is True
        assert client_error_request.was_server_error is False

        assert server_error_request.was_successful is False
        assert server_error_request.was_client_error is False
        assert server_error_request.was_server_error is True


class TestResponseLog:
    """Test cases for ResponseLog entity."""

    def test_response_log_initialization(self) -> None:
        """Test response log initialization."""
        response_log = ResponseLog(
            request_id=uuid4(),
            status_code=201,
            headers={"Content-Type": "application/json"},
            body={"id": "123", "status": "created"},
            response_time_ms=75,
            content_type="application/json",
            content_length=256,
        )

        assert response_log.status_code == 201
        assert response_log.headers == {"Content-Type": "application/json"}
        assert response_log.body == {"id": "123", "status": "created"}
        assert response_log.response_time_ms == 75
        assert response_log.content_type == "application/json"
        assert response_log.content_length == 256

    def test_response_log_status_properties(self) -> None:
        """Test response log status checking properties."""
        success_response = ResponseLog(
            request_id=uuid4(),
            status_code=200,
            response_time_ms=50,
        )

        client_error_response = ResponseLog(
            request_id=uuid4(),
            status_code=400,
            response_time_ms=25,
        )

        server_error_response = ResponseLog(
            request_id=uuid4(),
            status_code=500,
            response_time_ms=200,
        )

        assert success_response.success is True
        assert success_response.is_client_error is False
        assert success_response.is_server_error is False
        assert success_response.is_fast_response is True

        assert client_error_response.success is False
        assert client_error_response.is_client_error is True
        assert client_error_response.is_server_error is False
        assert client_error_response.is_fast_response is True

        assert server_error_response.success is False
        assert server_error_response.is_client_error is False
        assert server_error_response.is_server_error is True
        assert server_error_response.is_fast_response is False


class TestAPIRequest:
    """Test cases for APIRequest entity."""

    def test_api_request_initialization(self) -> None:
        """Test API request initialization."""
        api_request = APIRequest(
            request_id="api-req-456",
            endpoint="/api/v1/users/123",
            method="PUT",
            query_params={"include": "profile"},
            headers={"Authorization": "Bearer token123"},
            body={"name": "Updated Name"},
            client_ip="192.168.1.100",
            user_agent="Mozilla/5.0",
        )

        assert api_request.method == "PUT"
        assert api_request.endpoint == "/api/v1/users/123"
        assert api_request.query_params == {"include": "profile"}
        assert api_request.headers == {"Authorization": "Bearer token123"}
        assert api_request.body == {"name": "Updated Name"}
        assert api_request.client_ip == "192.168.1.100"
        assert api_request.user_agent == "Mozilla/5.0"
        assert api_request.request_id == "api-req-456"


class TestAPIResponseLog:
    """Test cases for APIResponseLog entity."""

    def test_api_response_initialization(self) -> None:
        """Test API response initialization."""
        api_response = APIResponseLog(
            request_id="req-123",
            response_id="resp-456",
            status_code=200,
            headers={"Cache-Control": "no-cache"},
            body={"message": "Success"},
            content_type="application/json",
            size_bytes=512,
        )

        assert api_response.status_code == 200
        assert api_response.headers == {"Cache-Control": "no-cache"}
        assert api_response.body == {"message": "Success"}
        assert api_response.content_type == "application/json"
        assert api_response.size_bytes == 512

    def test_api_response_status_properties(self) -> None:
        """Test API response status checking properties."""
        success_response = APIResponseLog(
            request_id="req-1",
            response_id="resp-1",
            status_code=204,
        )

        client_error_response = APIResponseLog(
            request_id="req-2",
            response_id="resp-2",
            status_code=422,
        )

        server_error_response = APIResponseLog(
            request_id="req-3",
            response_id="resp-3",
            status_code=503,
        )

        assert success_response.success is True
        assert success_response.is_client_error is False
        assert success_response.is_server_error is False

        assert client_error_response.success is False
        assert client_error_response.is_client_error is True
        assert client_error_response.is_server_error is False

        assert server_error_response.success is False
        assert server_error_response.is_client_error is False
        assert server_error_response.is_server_error is True


class TestDomainEvents:
    """Test cases for domain events."""

    def test_pipeline_created_event(self) -> None:
        """Test pipeline created event."""
        pipeline_id = uuid4()
        event = PipelineCreatedEvent(
            pipeline_id=pipeline_id,
            pipeline_name="test-pipeline",
        )

        assert event.pipeline_id == pipeline_id
        assert event.pipeline_name == "test-pipeline"

    def test_pipeline_executed_event(self) -> None:
        """Test pipeline executed event."""
        pipeline_id = uuid4()
        execution_id = 12345

        event = PipelineExecutedEvent(
            pipeline_id=pipeline_id,
            execution_id=execution_id,
            error_message=None,
        )

        assert event.pipeline_id == pipeline_id
        assert event.execution_id == execution_id
        assert event.error_message is None

    def test_plugin_registered_event(self) -> None:
        """Test plugin registered event."""
        plugin_id = uuid4()

        event = PluginRegisteredEvent(
            plugin_id=plugin_id,
            plugin_name="tap-csv",
            plugin_type=PluginType.TAP,
            version="1.0.0",
        )

        assert event.plugin_id == plugin_id
        assert event.plugin_name == "tap-csv"
        assert event.plugin_type == PluginType.EXTRACTOR
        assert event.version == "1.0.0"
