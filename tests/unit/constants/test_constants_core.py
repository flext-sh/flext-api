"""Tests for constants core functionality.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import http

from flext_core import FlextFieldType

from flext_api import (
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
        if FLEXT_API_VERSION != "0.9.0":
            msg = f"Expected 1.0.0, got {FLEXT_API_VERSION}"
            raise AssertionError(msg)
        assert isinstance(FLEXT_API_VERSION, str)

    def test_timeout_constant(self) -> None:
        """Test timeout constant."""
        if FLEXT_API_TIMEOUT != 30:
            msg = f"Expected 30, got {FLEXT_API_TIMEOUT}"
            raise AssertionError(msg)
        assert isinstance(FLEXT_API_TIMEOUT, int)

    def test_retries_constant(self) -> None:
        """Test max retries constant."""
        if FLEXT_API_MAX_RETRIES != EXPECTED_DATA_COUNT:
            msg = f"Expected 3, got {FLEXT_API_MAX_RETRIES}"
            raise AssertionError(msg)
        assert isinstance(FLEXT_API_MAX_RETRIES, int)

    def test_cache_ttl_constant(self) -> None:
        """Test cache TTL constant."""
        if FLEXT_API_CACHE_TTL != 300:
            msg = f"Expected 300, got {FLEXT_API_CACHE_TTL}"
            raise AssertionError(msg)
        assert isinstance(FLEXT_API_CACHE_TTL, int)


class TestFlextApiConstants:
    """Test FlextApiConstants class."""

    def test_success_codes(self) -> None:
        """Test success codes using http.HTTPStatus constants."""
        ok_code = http.HTTPStatus.OK.value
        created_code = http.HTTPStatus.CREATED.value
        not_found_code = http.HTTPStatus.NOT_FOUND.value

        if ok_code not in FlextApiConstants.SUCCESS_CODES:
            msg = f"Expected {ok_code} in {FlextApiConstants.SUCCESS_CODES}"
            raise AssertionError(
                msg,
            )
        assert created_code in FlextApiConstants.SUCCESS_CODES
        if not_found_code in FlextApiConstants.SUCCESS_CODES:
            msg = f"Expected {not_found_code} not in {FlextApiConstants.SUCCESS_CODES}"
            raise AssertionError(
                msg,
            )

    def test_client_error_codes(self) -> None:
        """Test client error codes using http.HTTPStatus constants."""
        bad_request_code = http.HTTPStatus.BAD_REQUEST.value
        not_found_code = http.HTTPStatus.NOT_FOUND.value
        ok_code = http.HTTPStatus.OK.value

        if bad_request_code not in FlextApiConstants.CLIENT_ERROR_CODES:
            msg = (
                f"Expected {bad_request_code} in {FlextApiConstants.CLIENT_ERROR_CODES}"
            )
            raise AssertionError(
                msg,
            )
        assert not_found_code in FlextApiConstants.CLIENT_ERROR_CODES
        if ok_code in FlextApiConstants.CLIENT_ERROR_CODES:
            msg = f"Expected {ok_code} not in {FlextApiConstants.CLIENT_ERROR_CODES}"
            raise AssertionError(
                msg,
            )

    def test_server_error_codes(self) -> None:
        """Test server error codes using http.HTTPStatus constants."""
        internal_error_code = http.HTTPStatus.INTERNAL_SERVER_ERROR.value
        bad_gateway_code = http.HTTPStatus.BAD_GATEWAY.value
        ok_code = http.HTTPStatus.OK.value

        if internal_error_code not in FlextApiConstants.SERVER_ERROR_CODES:
            msg = f"Expected {internal_error_code} in {FlextApiConstants.SERVER_ERROR_CODES}"
            raise AssertionError(
                msg,
            )
        assert bad_gateway_code in FlextApiConstants.SERVER_ERROR_CODES
        if ok_code in FlextApiConstants.SERVER_ERROR_CODES:
            msg = f"Expected {ok_code} not in {FlextApiConstants.SERVER_ERROR_CODES}"
            raise AssertionError(
                msg,
            )

    def test_rate_limit_constants(self) -> None:
        """Test rate limit constants."""
        if FlextApiConstants.RATE_LIMIT_REQUESTS != 1000:
            msg = f"Expected 1000, got {FlextApiConstants.RATE_LIMIT_REQUESTS}"
            raise AssertionError(
                msg,
            )
        assert FlextApiConstants.RATE_LIMIT_WINDOW == 3600

    def test_response_templates(self) -> None:
        """Test response templates."""
        success_response = FlextApiConstants.SUCCESS_RESPONSE
        if success_response["status"] != "success":
            msg = f"Expected success, got {success_response['status']}"
            raise AssertionError(msg)
        assert success_response["data"] is None
        assert success_response["error"] is None

        error_response = FlextApiConstants.ERROR_RESPONSE
        if error_response["status"] != "error":
            msg = f"Expected error, got {error_response['status']}"
            raise AssertionError(msg)
        assert error_response["data"] is None
        assert error_response["error"] is None


class TestFlextApiFieldType:
    """Test FlextApiFieldType class."""

    def test_field_types(self) -> None:
        """Test API-specific field type constants."""
        assert FlextApiFieldType.API_KEY == "api_key"
        assert FlextApiFieldType.BEARER_TOKEN == "bearer_token"
        assert FlextApiFieldType.PIPELINE_CONFIG == "pipeline_config"
        assert FlextApiFieldType.PLUGIN_CONFIG == "plugin_config"
        assert FlextApiFieldType.USER_ROLE == "user_role"
        assert FlextApiFieldType.ENDPOINT_PATH == "endpoint_path"
        assert FlextApiFieldType.HTTP_METHOD == "http_method"
        assert FlextApiFieldType.RESPONSE_FORMAT == "response_format"

    def test_field_type_validation(self) -> None:
        """Test field type validation using flext-core types."""
        valid_types = [
            FlextFieldType.STRING,
            FlextFieldType.INTEGER,
            FlextFieldType.FLOAT,
            FlextFieldType.BOOLEAN,
            FlextFieldType.DATE,
            FlextFieldType.DATETIME,
            FlextFieldType.UUID,
            FlextFieldType.EMAIL,
        ]

        for field_type in valid_types:
            assert isinstance(field_type.value, str)
            assert len(field_type.value) > 0


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
        assert FlextApiStatus.HEALTHY == "healthy"
        assert FlextApiStatus.DEGRADED == "degraded"
        assert FlextApiStatus.UNHEALTHY == "unhealthy"
        assert FlextApiStatus.MAINTENANCE == "maintenance"

    def test_pipeline_status(self) -> None:
        """Test pipeline status constants."""
        assert FlextApiStatus.PIPELINE_IDLE == "idle"
        assert FlextApiStatus.PIPELINE_RUNNING == "running"
        assert FlextApiStatus.PIPELINE_SUCCESS == "success"
        assert FlextApiStatus.PIPELINE_ERROR == "error"
        assert FlextApiStatus.PIPELINE_TIMEOUT == "timeout"

    def test_plugin_status(self) -> None:
        """Test plugin status constants."""
        assert FlextApiStatus.PLUGIN_LOADED == "loaded"
        assert FlextApiStatus.PLUGIN_ACTIVE == "active"
        assert FlextApiStatus.PLUGIN_INACTIVE == "inactive"
        assert FlextApiStatus.PLUGIN_ERROR == "error"


class TestFlextApiEndpoints:
    """Test FlextApiEndpoints class."""

    def test_base_paths(self) -> None:
        """Test base path constants."""
        assert FlextApiEndpoints.API_V1 == "/api/v1"
        assert FlextApiEndpoints.HEALTH == "/health"
        assert FlextApiEndpoints.METRICS == "/metrics"
        assert FlextApiEndpoints.DOCS == "/docs"

    def test_auth_endpoints(self) -> None:
        """Test authentication endpoints."""
        assert FlextApiEndpoints.AUTH_LOGIN == "/api/v1/auth/login"
        assert FlextApiEndpoints.AUTH_LOGOUT == "/api/v1/auth/logout"
        assert FlextApiEndpoints.AUTH_REFRESH == "/api/v1/auth/refresh"
        assert FlextApiEndpoints.AUTH_VERIFY == "/api/v1/auth/verify"

    def test_pipeline_endpoints(self) -> None:
        """Test pipeline endpoints."""
        assert FlextApiEndpoints.PIPELINES == "/api/v1/pipelines"
        assert FlextApiEndpoints.PIPELINE_RUN == "/api/v1/pipelines/{pipeline_id}/run"
        assert (
            FlextApiEndpoints.PIPELINE_STATUS
            == "/api/v1/pipelines/{pipeline_id}/status"
        )
        assert FlextApiEndpoints.PIPELINE_LOGS == "/api/v1/pipelines/{pipeline_id}/logs"

    def test_plugin_endpoints(self) -> None:
        """Test plugin endpoints."""
        assert FlextApiEndpoints.PLUGINS == "/api/v1/plugins"
        assert FlextApiEndpoints.PLUGIN_INSTALL == "/api/v1/plugins/install"
        assert (
            FlextApiEndpoints.PLUGIN_UNINSTALL
            == "/api/v1/plugins/{plugin_id}/uninstall"
        )
        assert FlextApiEndpoints.PLUGIN_CONFIG == "/api/v1/plugins/{plugin_id}/config"
