"""Tests for flext_api.models module - REAL classes only.

Tests using only REAL classes:
- FlextApiModels

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from flext_api import FlextApiModels
from tests.conftest import assert_flext_result_failure, assert_flext_result_success


class TestFlextApiModels:
    """Test FlextApiModels REAL class functionality."""

    def test_models_class_exists(self) -> None:
        """Test FlextApiModels class exists and is accessible."""
        assert FlextApiModels is not None
        assert hasattr(FlextApiModels, "HttpMethod")
        assert hasattr(FlextApiModels, "HttpStatus")
        assert hasattr(FlextApiModels, "ClientConfig")
        assert hasattr(FlextApiModels, "ApiRequest")
        assert hasattr(FlextApiModels, "ApiResponse")
        assert hasattr(FlextApiModels, "QueryBuilder")
        assert hasattr(FlextApiModels, "ResponseBuilder")

    def test_http_method_enum(self) -> None:
        """Test HttpMethod enum values."""
        assert FlextApiModels.HttpMethod.GET == "GET"
        assert FlextApiModels.HttpMethod.POST == "POST"
        assert FlextApiModels.HttpMethod.PUT == "PUT"
        assert FlextApiModels.HttpMethod.DELETE == "DELETE"
        assert FlextApiModels.HttpMethod.PATCH == "PATCH"
        assert FlextApiModels.HttpMethod.HEAD == "HEAD"
        assert FlextApiModels.HttpMethod.OPTIONS == "OPTIONS"

    def test_http_status_enum(self) -> None:
        """Test HttpStatus enum values."""
        assert FlextApiModels.HttpStatus.SUCCESS == "success"
        assert FlextApiModels.HttpStatus.ERROR == "error"
        assert FlextApiModels.HttpStatus.PENDING == "pending"
        assert FlextApiModels.HttpStatus.TIMEOUT == "timeout"

    def test_client_config_creation_basic(self) -> None:
        """Test basic ClientConfig creation."""
        config = FlextApiModels.ClientConfig(base_url="https://api.example.com")

        assert config.base_url == "https://api.example.com"
        assert config.timeout == 30.0  # default
        assert config.max_retries == 3  # default
        assert config.headers == {}  # default

    def test_client_config_creation_custom(self) -> None:
        """Test ClientConfig creation with custom values."""
        headers = {"Authorization": "Bearer token", "Accept": "application/json"}

        config = FlextApiModels.ClientConfig(
            base_url="https://api.test.com",
            timeout=60.0,
            max_retries=5,
            headers=headers,
        )

        assert config.base_url == "https://api.test.com"
        assert config.timeout == 60.0
        assert config.max_retries == 5
        assert config.headers == headers

    def test_client_config_base_url_validation(self) -> None:
        """Test ClientConfig base_url validation."""
        # Valid URLs
        for url in [
            "http://localhost",
            "https://api.example.com",
            "https://test.com:8080/api",
        ]:
            config = FlextApiModels.ClientConfig(base_url=url)
            assert config.base_url == url

        # Empty base_url should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            FlextApiModels.ClientConfig(base_url="")
        assert "Base URL cannot be empty" in str(exc_info.value)

        # Invalid URL format should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            FlextApiModels.ClientConfig(base_url="not-a-url")
        assert "Base URL must include scheme and host" in str(exc_info.value)

    def test_client_config_timeout_validation(self) -> None:
        """Test ClientConfig timeout validation."""
        # Valid timeout
        config = FlextApiModels.ClientConfig(
            base_url="https://api.example.com", timeout=45.0
        )
        assert config.timeout == 45.0

        # Invalid timeout should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            FlextApiModels.ClientConfig(base_url="https://api.example.com", timeout=0.0)
        assert "greater than 0" in str(exc_info.value)

    def test_client_config_max_retries_validation(self) -> None:
        """Test ClientConfig max_retries validation."""
        # Valid retries
        config = FlextApiModels.ClientConfig(
            base_url="https://api.example.com", max_retries=10
        )
        assert config.max_retries == 10

        # Zero retries is valid
        config = FlextApiModels.ClientConfig(
            base_url="https://api.example.com", max_retries=0
        )
        assert config.max_retries == 0

        # Negative retries should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            FlextApiModels.ClientConfig(
                base_url="https://api.example.com", max_retries=-1
            )
        assert "greater than or equal to 0" in str(exc_info.value)

    def test_api_request_creation(self) -> None:
        """Test ApiRequest creation."""
        headers = {"Content-Type": "application/json"}
        data = {"name": "test", "value": 123}

        request = FlextApiModels.ApiRequest(
            method=FlextApiModels.HttpMethod.POST,
            url="/api/test",
            headers=headers,
            data=data,
        )

        assert request.method == FlextApiModels.HttpMethod.POST
        assert request.url == "/api/test"
        assert request.headers == headers
        assert request.data == data

    def test_api_request_url_validation(self) -> None:
        """Test ApiRequest URL validation."""
        # Valid URL
        request = FlextApiModels.ApiRequest(
            method=FlextApiModels.HttpMethod.GET, url="/api/users"
        )
        assert request.url == "/api/users"

        # Empty URL should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            FlextApiModels.ApiRequest(method=FlextApiModels.HttpMethod.GET, url="")
        assert "URL cannot be empty" in str(exc_info.value)

    def test_api_response_creation(self) -> None:
        """Test ApiResponse creation."""
        headers = {"Content-Type": "application/json"}
        data = {"result": "success"}

        response = FlextApiModels.ApiResponse(
            status_code=200, data=data, headers=headers, url="/api/test"
        )

        assert response.status_code == 200
        assert response.data == data
        assert response.headers == headers
        assert response.url == "/api/test"

    def test_api_response_status_validation(self) -> None:
        """Test ApiResponse status code validation."""
        # Valid status codes
        for code in [100, 200, 404, 500, 599]:
            response = FlextApiModels.ApiResponse(status_code=code, url="/test")
            assert response.status_code == code

        # Invalid status codes should raise ValidationError
        for code in [99, 600]:
            with pytest.raises(ValidationError):
                FlextApiModels.ApiResponse(status_code=code, url="/test")

    def test_api_response_status_properties(self) -> None:
        """Test ApiResponse status checking properties."""
        # Success response
        response = FlextApiModels.ApiResponse(status_code=200, url="/test")
        assert response.is_success is True
        assert response.is_client_error is False
        assert response.is_server_error is False

        # Client error response
        response = FlextApiModels.ApiResponse(status_code=404, url="/test")
        assert response.is_success is False
        assert response.is_client_error is True
        assert response.is_server_error is False

        # Server error response
        response = FlextApiModels.ApiResponse(status_code=500, url="/test")
        assert response.is_success is False
        assert response.is_client_error is False
        assert response.is_server_error is True

    def test_query_builder_creation(self) -> None:
        """Test QueryBuilder creation."""
        builder = FlextApiModels.QueryBuilder()

        assert builder.filters == {}
        assert builder.sort_by is None
        assert builder.sort_order == "asc"
        assert builder.page == 1
        assert builder.page_size == 50

    def test_query_builder_custom_values(self) -> None:
        """Test QueryBuilder with custom values."""
        filters = {"status": "active", "category": "premium"}

        builder = FlextApiModels.QueryBuilder(
            filters=filters,
            sort_by="created_at",
            sort_order="desc",
            page=2,
            page_size=25,
        )

        assert builder.filters == filters
        assert builder.sort_by == "created_at"
        assert builder.sort_order == "desc"
        assert builder.page == 2
        assert builder.page_size == 25

    def test_query_builder_page_validation(self) -> None:
        """Test QueryBuilder page validation."""
        # Valid page
        builder = FlextApiModels.QueryBuilder(page=5)
        assert builder.page == 5

        # Invalid page should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            FlextApiModels.QueryBuilder(page=0)
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_query_builder_page_size_validation(self) -> None:
        """Test QueryBuilder page_size validation."""
        # Valid page sizes
        for size in [1, 50, 100, 1000]:
            builder = FlextApiModels.QueryBuilder(page_size=size)
            assert builder.page_size == size

        # Invalid page sizes should raise ValidationError
        with pytest.raises(ValidationError):
            FlextApiModels.QueryBuilder(page_size=0)

        with pytest.raises(ValidationError):
            FlextApiModels.QueryBuilder(page_size=1001)

    def test_query_builder_add_filter_success(self) -> None:
        """Test QueryBuilder add_filter success."""
        builder = FlextApiModels.QueryBuilder()

        result = builder.add_filter("status", "active")
        assert_flext_result_success(result)

        assert builder.filters["status"] == "active"

    def test_query_builder_add_filter_empty_key_failure(self) -> None:
        """Test QueryBuilder add_filter with empty key fails."""
        builder = FlextApiModels.QueryBuilder()

        result = builder.add_filter("", "value")
        assert_flext_result_failure(result, "Filter key cannot be empty")

    def test_query_builder_to_query_params(self) -> None:
        """Test QueryBuilder to_query_params conversion."""
        builder = FlextApiModels.QueryBuilder(
            filters={"status": "active", "type": "premium"},
            sort_by="name",
            sort_order="asc",
            page=2,
            page_size=25,
        )

        result = builder.to_query_params()
        assert_flext_result_success(result)

        params = result.data
        assert isinstance(params, dict)
        assert params["status"] == "active"
        assert params["type"] == "premium"
        assert params["sort_by"] == "name"
        assert params["sort_order"] == "asc"
        assert params["page"] == 2
        assert params["page_size"] == 25

    def test_response_builder_creation(self) -> None:
        """Test ResponseBuilder creation."""
        builder = FlextApiModels.ResponseBuilder()

        assert builder.status_code == 200
        assert builder.data is None
        assert builder.message == ""

    def test_response_builder_custom_values(self) -> None:
        """Test ResponseBuilder with custom values."""
        data = {"id": 123, "name": "test"}

        builder = FlextApiModels.ResponseBuilder(
            status_code=201, data=data, message="Created successfully"
        )

        assert builder.status_code == 201
        assert builder.data == data
        assert builder.message == "Created successfully"

    def test_response_builder_success(self) -> None:
        """Test ResponseBuilder success method."""
        builder = FlextApiModels.ResponseBuilder()
        data = {"result": "completed"}

        result = builder.success(data=data, message="Operation successful")
        assert_flext_result_success(result)

        response = result.data
        assert isinstance(response, dict)
        assert response["status"] == "success"
        assert response["status_code"] == 200
        assert response["data"] == data
        assert response["message"] == "Operation successful"

    def test_response_builder_error(self) -> None:
        """Test ResponseBuilder error method."""
        builder = FlextApiModels.ResponseBuilder()

        result = builder.error(message="Validation failed", status_code=400)
        assert_flext_result_success(result)

        response = result.data
        assert isinstance(response, dict)
        assert response["status"] == "error"
        assert response["status_code"] == 400
        assert response["data"] is None
        assert response["message"] == "Validation failed"

    def test_models_type_validation(self) -> None:
        """Test models are proper types."""
        # Main class
        assert FlextApiModels is not None
        assert type(FlextApiModels).__name__ == "type"

        # Nested classes
        config = FlextApiModels.ClientConfig(base_url="https://api.example.com")
        assert isinstance(config, FlextApiModels.ClientConfig)

        request = FlextApiModels.ApiRequest(
            method=FlextApiModels.HttpMethod.GET, url="/test"
        )
        assert isinstance(request, FlextApiModels.ApiRequest)

    def test_models_inheritance(self) -> None:
        """Test models properly inherit from FlextModels."""
        # Main class should inherit from FlextModels
        assert issubclass(FlextApiModels, type(FlextApiModels).__bases__[0])

        # Nested models should have BaseModel functionality
        config = FlextApiModels.ClientConfig(base_url="https://api.example.com")
        assert hasattr(config, "model_dump")
        assert hasattr(config, "model_validate")
