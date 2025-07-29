#!/usr/bin/env python3
"""Tests for constants module."""

from flext_api.constants import (
    FLEXT_API_CACHE_TTL,
    FLEXT_API_MAX_RETRIES,
    FLEXT_API_TIMEOUT,
    FLEXT_API_VERSION,
    FlextApiConstants,
    FlextApiEndpoints,
    FlextApiFieldType,
    FlextApiStatus,
)

# Constants
EXPECTED_DATA_COUNT = 3


class TestConstants:
    """Test cases for constants."""

    def test_version_constant(self) -> None:
        """Test version constant."""
        if FLEXT_API_VERSION != "1.0.0":
            raise AssertionError(f"Expected 1.0.0, got {FLEXT_API_VERSION}")
        assert isinstance(FLEXT_API_VERSION, str)

    def test_timeout_constant(self) -> None:
        """Test timeout constant."""
        if FLEXT_API_TIMEOUT != 30:
            raise AssertionError(f"Expected 30, got {FLEXT_API_TIMEOUT}")
        assert isinstance(FLEXT_API_TIMEOUT, int)

    def test_retries_constant(self) -> None:
        """Test max retries constant."""
        if FLEXT_API_MAX_RETRIES != EXPECTED_DATA_COUNT:
            raise AssertionError(f"Expected 3, got {FLEXT_API_MAX_RETRIES}")
        assert isinstance(FLEXT_API_MAX_RETRIES, int)

    def test_cache_ttl_constant(self) -> None:
        """Test cache TTL constant."""
        if FLEXT_API_CACHE_TTL != 300:
            raise AssertionError(f"Expected 300, got {FLEXT_API_CACHE_TTL}")
        assert isinstance(FLEXT_API_CACHE_TTL, int)


class TestFlextApiConstants:
    """Test FlextApiConstants class."""

    def test_success_codes(self) -> None:
        """Test success codes."""
        if 200 not in FlextApiConstants.SUCCESS_CODES:
            raise AssertionError(f"Expected 200 in {FlextApiConstants.SUCCESS_CODES}")
        assert 201 in FlextApiConstants.SUCCESS_CODES
        if 404 in FlextApiConstants.SUCCESS_CODES:
            raise AssertionError(
                f"Expected 404 not in {FlextApiConstants.SUCCESS_CODES}"
            )

    def test_client_error_codes(self) -> None:
        """Test client error codes."""
        if 400 not in FlextApiConstants.CLIENT_ERROR_CODES:
            raise AssertionError(
                f"Expected 400 in {FlextApiConstants.CLIENT_ERROR_CODES}"
            )
        assert 404 in FlextApiConstants.CLIENT_ERROR_CODES
        if 200 in FlextApiConstants.CLIENT_ERROR_CODES:
            raise AssertionError(
                f"Expected 200 not in {FlextApiConstants.CLIENT_ERROR_CODES}"
            )

    def test_server_error_codes(self) -> None:
        """Test server error codes."""
        if 500 not in FlextApiConstants.SERVER_ERROR_CODES:
            raise AssertionError(
                f"Expected 500 in {FlextApiConstants.SERVER_ERROR_CODES}"
            )
        assert 502 in FlextApiConstants.SERVER_ERROR_CODES
        if 200 in FlextApiConstants.SERVER_ERROR_CODES:
            raise AssertionError(
                f"Expected 200 not in {FlextApiConstants.SERVER_ERROR_CODES}"
            )

    def test_rate_limit_constants(self) -> None:
        """Test rate limit constants."""
        if FlextApiConstants.RATE_LIMIT_REQUESTS != 1000:
            raise AssertionError(
                f"Expected 1000, got {FlextApiConstants.RATE_LIMIT_REQUESTS}"
            )
        assert FlextApiConstants.RATE_LIMIT_WINDOW == 3600

    def test_response_templates(self) -> None:
        """Test response templates."""
        success_response = FlextApiConstants.SUCCESS_RESPONSE
        if success_response["status"] != "success":
            raise AssertionError(f"Expected success, got {success_response['status']}")
        assert success_response["data"] is None
        assert success_response["error"] is None

        error_response = FlextApiConstants.ERROR_RESPONSE
        if error_response["status"] != "error":
            raise AssertionError(f"Expected error, got {error_response['status']}")
        assert error_response["data"] is None
        assert error_response["error"] is None


class TestFlextApiFieldType:
    """Test FlextApiFieldType class."""

    def test_field_types(self) -> None:
        """Test field type constants."""
        assert FlextApiFieldType.STRING == "string"
        assert FlextApiFieldType.INTEGER == "integer"
        assert FlextApiFieldType.FLOAT == "float"
        assert FlextApiFieldType.BOOLEAN == "boolean"
        assert FlextApiFieldType.DATE == "date"
        assert FlextApiFieldType.DATETIME == "datetime"
        assert FlextApiFieldType.OBJECT == "object"
        assert FlextApiFieldType.ARRAY == "array"

    def test_field_type_validation(self) -> None:
        """Test field type validation."""
        valid_types = [
            FlextApiFieldType.STRING,
            FlextApiFieldType.INTEGER,
            FlextApiFieldType.FLOAT,
            FlextApiFieldType.BOOLEAN,
            FlextApiFieldType.DATE,
            FlextApiFieldType.DATETIME,
            FlextApiFieldType.OBJECT,
            FlextApiFieldType.ARRAY,
        ]

        for field_type in valid_types:
            assert isinstance(field_type, str)
            assert len(field_type) > 0


class TestFlextApiStatus:
    """Test FlextApiStatus class."""

    def test_request_status(self) -> None:
        """Test request status constants."""
        assert FlextApiStatus.PENDING == "pending"
        assert FlextApiStatus.PROCESSING == "processing"
        assert FlextApiStatus.COMPLETED == "completed"
        assert FlextApiStatus.FAILED == "failed"
        assert FlextApiStatus.CANCELLED == "cancelled"

    def test_service_status(self) -> None:
        """Test service status constants."""
        assert FlextApiStatus.IDLE == "idle"
        assert FlextApiStatus.RUNNING == "running"
        assert FlextApiStatus.STOPPED == "stopped"
        assert FlextApiStatus.ERROR == "error"

    def test_pipeline_status(self) -> None:
        """Test pipeline status constants."""
        assert FlextApiStatus.CREATED == "created"
        assert FlextApiStatus.STARTED == "started"
        assert FlextApiStatus.PAUSED == "paused"
        assert FlextApiStatus.RESUMED == "resumed"
        assert FlextApiStatus.FINISHED == "finished"

    def test_plugin_status(self) -> None:
        """Test plugin status constants."""
        assert FlextApiStatus.ENABLED == "enabled"
        assert FlextApiStatus.DISABLED == "disabled"
        assert FlextApiStatus.LOADING == "loading"
        assert FlextApiStatus.ERROR == "error"


class TestFlextApiEndpoints:
    """Test FlextApiEndpoints class."""

    def test_base_paths(self) -> None:
        """Test base path constants."""
        assert FlextApiEndpoints.API_BASE == "/api"
        assert FlextApiEndpoints.V1_BASE == "/api/v1"
        assert FlextApiEndpoints.HEALTH == "/health"
        assert FlextApiEndpoints.STATUS == "/status"

    def test_auth_endpoints(self) -> None:
        """Test authentication endpoints."""
        assert FlextApiEndpoints.LOGIN == "/auth/login"
        assert FlextApiEndpoints.LOGOUT == "/auth/logout"
        assert FlextApiEndpoints.REFRESH == "/auth/refresh"
        assert FlextApiEndpoints.VERIFY == "/auth/verify"

    def test_pipeline_endpoints(self) -> None:
        """Test pipeline endpoints."""
        assert FlextApiEndpoints.PIPELINES == "/pipelines"
        assert FlextApiEndpoints.PIPELINE_DETAIL == "/pipelines/{id}"
        assert FlextApiEndpoints.PIPELINE_START == "/pipelines/{id}/start"
        assert FlextApiEndpoints.PIPELINE_STOP == "/pipelines/{id}/stop"

    def test_plugin_endpoints(self) -> None:
        """Test plugin endpoints."""
        assert FlextApiEndpoints.PLUGINS == "/plugins"
        assert FlextApiEndpoints.PLUGIN_DETAIL == "/plugins/{id}"
        assert FlextApiEndpoints.PLUGIN_ENABLE == "/plugins/{id}/enable"
        assert FlextApiEndpoints.PLUGIN_DISABLE == "/plugins/{id}/disable"
