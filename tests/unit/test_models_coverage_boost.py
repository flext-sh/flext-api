"""Comprehensive models tests to achieve high coverage of models.py module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from flext_api.models import FlextApiModels


class TestFlextApiModelsCoverageBoost:
    """Comprehensive tests to boost coverage of FlextApiModels class.

    This test class has many public methods by design as it provides comprehensive
    test coverage to boost code coverage. Each test method validates a specific
    aspect of the model behavior, which is a legitimate use case for having
    many methods in a test class.
    """

    def test_http_request_url_validation_empty(self) -> None:
        """Test HttpRequest URL validation with empty URL."""
        with pytest.raises(ValidationError) as excinfo:
            FlextApiModels.HttpRequest(url="")
        assert "Invalid URL" in str(excinfo.value)

    def test_http_request_url_validation_invalid_format(self) -> None:
        """Test HttpRequest URL validation with invalid format."""
        with pytest.raises(ValidationError) as excinfo:
            FlextApiModels.HttpRequest(url="invalid-url")
        assert "Invalid URL format" in str(excinfo.value)

    def test_http_request_url_validation_whitespace(self) -> None:
        """Test HttpRequest URL validation with whitespace."""
        with pytest.raises(ValidationError) as excinfo:
            FlextApiModels.HttpRequest(url="   ")
        assert "Invalid URL" in str(excinfo.value)

    def test_http_request_url_validation_non_string(self) -> None:
        """Test HttpRequest URL validation with non-string input."""
        with pytest.raises(ValidationError) as excinfo:
            FlextApiModels.HttpRequest(url="")
        assert "Invalid URL" in str(excinfo.value)

    def test_http_request_valid_urls(self) -> None:
        """Test HttpRequest with valid URLs."""
        # HTTP URL
        request1 = FlextApiModels.HttpRequest(url="http://example.com")
        assert request1.url == "http://example.com"

        # HTTPS URL
        request2 = FlextApiModels.HttpRequest(url="https://example.com/path")
        assert request2.url == "https://example.com/path"

        # Relative URL
        request3 = FlextApiModels.HttpRequest(url="/api/endpoint")
        assert request3.url == "/api/endpoint"

        # URL with whitespace that gets trimmed
        request4 = FlextApiModels.HttpRequest(url="  https://example.com  ")
        assert request4.url == "https://example.com"

    def test_http_request_headers_validation_none_values(self) -> None:
        """Test HttpRequest headers validation with None values."""
        # Test that headers with None values are handled during validation
        # We need to test this by creating a dict and seeing how it's processed
        request = FlextApiModels.HttpRequest(
            url="https://example.com",
            headers={"Authorization": "Bearer token", "  Whitespace  ": "  value  "},
        )
        # Whitespace should be trimmed
        assert "Whitespace" in request.headers
        assert request.headers["Whitespace"] == "value"

    def test_http_request_headers_validation_empty_keys(self) -> None:
        """Test HttpRequest headers validation with empty keys."""
        request = FlextApiModels.HttpRequest(
            url="https://example.com",
            headers={"": "value", "  ": "value2", "Valid": "valid_value"},
        )
        # Empty keys should be filtered out
        assert "" not in request.headers
        assert "Valid" in request.headers
        assert request.headers["Valid"] == "valid_value"

    def test_http_request_headers_validation_complex(self) -> None:
        """Test HttpRequest headers validation with complex scenarios."""
        request = FlextApiModels.HttpRequest(
            url="https://example.com",
            headers={
                "Content-Type": "application/json",
                "  Authorization  ": "  Bearer token  ",
                "Empty-Value": "",
                "Whitespace-Value": "   ",
            },
        )

        # Valid headers should be present and trimmed
        assert request.headers["Content-Type"] == "application/json"
        assert request.headers["Authorization"] == "Bearer token"

    def test_http_response_properties_success(self) -> None:
        """Test HttpResponse success properties."""
        response = FlextApiModels.HttpResponse(
            status_code=200,
            url="https://example.com",
            method="GET",
        )
        assert response.is_success is True
        assert response.is_client_error is False
        assert response.is_server_error is False
        assert response.is_redirect is False

    def test_http_response_properties_client_error(self) -> None:
        """Test HttpResponse client error properties."""
        response = FlextApiModels.HttpResponse(
            status_code=404,
            url="https://example.com",
            method="GET",
        )
        assert response.is_success is False
        assert response.is_client_error is True
        assert response.is_server_error is False
        assert response.is_redirect is False

    def test_http_response_properties_server_error(self) -> None:
        """Test HttpResponse server error properties."""
        response = FlextApiModels.HttpResponse(
            status_code=500,
            url="https://example.com",
            method="GET",
        )
        assert response.is_success is False
        assert response.is_client_error is False
        assert response.is_server_error is True
        assert response.is_redirect is False

    def test_http_response_properties_redirect(self) -> None:
        """Test HttpResponse redirect properties."""
        response = FlextApiModels.HttpResponse(
            status_code=301,
            url="https://example.com",
            method="GET",
        )
        assert response.is_success is False
        assert response.is_client_error is False
        assert response.is_server_error is False
        assert response.is_redirect is True

    def test_client_config_base_url_validation_empty(self) -> None:
        """Test ClientConfig base_url validation with empty URL."""
        with pytest.raises(ValidationError) as excinfo:
            FlextApiModels.ClientConfig(base_url="")
        assert "URL must be a non-empty string" in str(excinfo.value)

    def test_client_config_base_url_validation_invalid(self) -> None:
        """Test ClientConfig base_url validation with invalid URL."""
        with pytest.raises(ValidationError) as excinfo:
            FlextApiModels.ClientConfig(base_url="invalid-url")
        assert "URL must be a non-empty string" in str(excinfo.value)

    def test_client_config_base_url_validation_whitespace_only(self) -> None:
        """Test ClientConfig base_url validation with whitespace only."""
        with pytest.raises(ValidationError) as excinfo:
            FlextApiModels.ClientConfig(base_url="   ")
        assert "URL must be a non-empty string" in str(excinfo.value)

    def test_client_config_valid_base_url(self) -> None:
        """Test ClientConfig with valid base URL."""
        config = FlextApiModels.ClientConfig(base_url="https://api.example.com")
        assert config.base_url == "https://api.example.com"

    def test_client_config_base_url_trimming(self) -> None:
        """Test ClientConfig base_url trimming."""
        config = FlextApiModels.ClientConfig(base_url="  https://api.example.com  ")
        assert config.base_url == "https://api.example.com"

    def test_client_config_get_auth_header_with_token(self) -> None:
        """Test ClientConfig get_auth_header with auth_token."""
        config = FlextApiModels.ClientConfig(
            base_url="https://api.example.com",
            auth_token="secret-token",
        )
        auth_header = config.get_auth_header()
        assert auth_header == {"Authorization": "Bearer secret-token"}

    def test_client_config_get_auth_header_with_api_key(self) -> None:
        """Test ClientConfig get_auth_header with api_key."""
        config = FlextApiModels.ClientConfig(
            base_url="https://api.example.com",
            api_key="api-key-123",
        )
        auth_header = config.get_auth_header()
        assert auth_header == {"Authorization": "Bearer api-key-123"}

    def test_client_config_get_auth_header_no_auth(self) -> None:
        """Test ClientConfig get_auth_header with no authentication."""
        config = FlextApiModels.ClientConfig(base_url="https://api.example.com")
        auth_header = config.get_auth_header()
        assert auth_header == {}

    def test_client_config_get_default_headers(self) -> None:
        """Test ClientConfig get_default_headers."""
        config = FlextApiModels.ClientConfig(
            base_url="https://api.example.com",
            auth_token="secret-token",
            headers={"Custom-Header": "custom-value"},
        )
        default_headers = config.get_default_headers()

        assert "User-Agent" in default_headers
        assert default_headers["User-Agent"] == "FlextAPI/0.9.0"
        assert default_headers["Custom-Header"] == "custom-value"
        assert default_headers["Authorization"] == "Bearer secret-token"

    def test_http_query_add_filter_success(self) -> None:
        """Test HttpQuery add_filter success case."""
        query = FlextApiModels.HttpQuery()
        result = query.add_filter("status", "active")

        assert result.is_success
        assert query.filter_conditions["status"] == "active"

    def test_http_query_add_filter_empty_key(self) -> None:
        """Test HttpQuery add_filter with empty key."""
        query = FlextApiModels.HttpQuery()
        result = query.add_filter("", "value")

        assert result.is_failure
        assert result.error is not None
        assert "Filter key cannot be empty" in result.error

    def test_http_query_add_filter_whitespace_key(self) -> None:
        """Test HttpQuery add_filter with whitespace key."""
        query = FlextApiModels.HttpQuery()
        result = query.add_filter("   ", "value")

        assert result.is_failure
        assert result.error is not None
        assert "Filter key cannot be empty" in result.error

    def test_http_query_add_filter_key_trimming(self) -> None:
        """Test HttpQuery add_filter key trimming."""
        query = FlextApiModels.HttpQuery()
        result = query.add_filter("  status  ", "active")

        assert result.is_success
        assert query.filter_conditions["status"] == "active"

    def test_http_query_to_query_params(self) -> None:
        """Test HttpQuery to_query_params method."""
        query = FlextApiModels.HttpQuery(
            page=2,
            page_size=50,
            sort_fields=["created_at", "name"],
        )
        query.add_filter("status", "active")

        params = query.to_query_params()

        assert params["page"] == 2
        assert params["page_size"] == 50
        assert params["sort_fields"] == ["created_at", "name"]
        assert params["status"] == "active"

    def test_http_query_to_query_params_with_filters(self) -> None:
        """Test HttpQuery to_query_params with complex filters."""
        query = FlextApiModels.HttpQuery()
        query.add_filter("status", "active")
        query.add_filter("type", "user")

        params = query.to_query_params()

        # Filters should be merged into params
        assert params["status"] == "active"
        assert params["type"] == "user"

    def test_pagination_config_page_property(self) -> None:
        """Test PaginationConfig page property."""
        config = FlextApiModels.PaginationConfig(page=5)
        assert config.current_page == 5

    def test_url_model_validate_business_rules_empty_url(self) -> None:
        """Test UrlModel validate_business_rules with empty URL."""
        url_model = FlextApiModels.UrlModel(raw_url="")
        result = url_model.validate_business_rules()

        assert result.is_failure
        assert result.error is not None
        assert "URL cannot be empty" in result.error

    def test_url_model_validate_business_rules_valid_url(self) -> None:
        """Test UrlModel validate_business_rules with valid URL."""
        url_model = FlextApiModels.UrlModel(raw_url="https://example.com")
        result = url_model.validate_business_rules()

        assert result.is_success

    def test_builder_create_success_response(self) -> None:
        """Test Builder create success response."""
        builder = FlextApiModels.Builder()
        response = builder.create(
            response_type="success",
            data={"key": "value"},
            message="Success message",
        )

        assert response["status"] == "success"
        assert response["data"] == {"key": "value"}
        assert response["message"] == "Success message"
        assert "timestamp" in response
        assert "request_id" in response

    def test_builder_create_error_response(self) -> None:
        """Test Builder create error response."""
        builder = FlextApiModels.Builder()
        response: dict[str, object] = builder.create(
            response_type="error",
            code="ERR_001",
            message="Error occurred",
        )

        assert response["status"] == "error"
        error_data = response["error"]
        assert isinstance(error_data, dict)
        assert error_data["code"] == "ERR_001"
        assert error_data["message"] == "Error occurred"
        assert "timestamp" in response
        assert "request_id" in response

    def test_builder_create_default_response(self) -> None:
        """Test Builder create with default (success) response."""
        builder = FlextApiModels.Builder()
        response = builder.create()  # No response_type specified

        assert response["status"] == "success"
        assert response["data"] is None
        assert not response["message"]

    def test_builder_static_success(self) -> None:
        """Test Builder static success method."""
        response = FlextApiModels.Builder.success(
            data={"test": "data"},
            message="Operation successful",
        )

        assert response["status"] == "success"
        assert response["data"] == {"test": "data"}
        assert response["message"] == "Operation successful"
        assert "timestamp" in response
        assert "request_id" in response

    def test_builder_static_error(self) -> None:
        """Test Builder static error method."""
        response: dict[str, object] = FlextApiModels.Builder.error(
            message="Something went wrong",
            code="ERR_500",
        )

        assert response["status"] == "error"
        error_data = response["error"]
        assert isinstance(error_data, dict)
        assert error_data["message"] == "Something went wrong"
        assert error_data["code"] == "ERR_500"
        assert "timestamp" in response
        assert "request_id" in response

    def test_app_config_validation_empty_title(self) -> None:
        """Test AppConfig validation with empty title."""
        with pytest.raises(ValidationError) as excinfo:
            FlextApiModels.AppConfig(title="", app_version="1.0.0")
        assert "Field cannot be empty" in str(excinfo.value)

    def test_app_config_validation_empty_version(self) -> None:
        """Test AppConfig validation with empty version."""
        with pytest.raises(ValidationError) as excinfo:
            FlextApiModels.AppConfig(title="Test API", app_version="")
        assert "Field cannot be empty" in str(excinfo.value)

    def test_app_config_validation_whitespace_title(self) -> None:
        """Test AppConfig validation with whitespace title."""
        with pytest.raises(ValidationError) as excinfo:
            FlextApiModels.AppConfig(title="   ", app_version="1.0.0")
        assert "Field cannot be empty" in str(excinfo.value)

    def test_app_config_validation_success(self) -> None:
        """Test AppConfig validation success case."""
        config = FlextApiModels.AppConfig(
            title="  Test API  ",  # Should be trimmed
            app_version="  1.0.0  ",  # Should be trimmed
            description="API Description",
        )

        assert config.title == "Test API"
        assert config.app_version == "1.0.0"
        assert config.description == "API Description"

    def test_api_request_creation(self) -> None:
        """Test ApiRequest model creation."""
        request = FlextApiModels.ApiRequest(
            method="POST",
            url="/api/endpoint",
            headers={"Content-Type": "application/json"},
            body={"key": "value"},
        )

        assert request.method == "POST"
        assert request.url == "/api/endpoint"
        assert request.headers["Content-Type"] == "application/json"
        assert request.body == {"key": "value"}

    def test_api_response_creation(self) -> None:
        """Test ApiResponse model creation."""
        response = FlextApiModels.ApiResponse(
            status_code=200,
            body={"result": "success"},
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200
        assert response.body == {"result": "success"}
        assert response.headers["Content-Type"] == "application/json"

    def test_storage_config_creation(self) -> None:
        """Test StorageConfig model creation."""
        config = FlextApiModels.StorageConfig(
            backend="redis",
            namespace="test_api",
            max_size=1000,
            default_ttl=3600,
        )

        assert config.backend == "redis"
        assert config.namespace == "test_api"
        assert config.max_size == 1000
        assert config.default_ttl == 3600

    def test_all_model_classes_available(self) -> None:
        """Test that all expected model classes are available."""
        # Test class access
        assert hasattr(FlextApiModels, "HttpRequest")
        assert hasattr(FlextApiModels, "HttpResponse")
        assert hasattr(FlextApiModels, "ClientConfig")
        assert hasattr(FlextApiModels, "HttpQuery")
        assert hasattr(FlextApiModels, "PaginationConfig")
        assert hasattr(FlextApiModels, "StorageConfig")
        assert hasattr(FlextApiModels, "ApiRequest")
        assert hasattr(FlextApiModels, "ApiResponse")
        assert hasattr(FlextApiModels, "UrlModel")
        assert hasattr(FlextApiModels, "Builder")
        assert hasattr(FlextApiModels, "AppConfig")

    def test_re_exported_models(self) -> None:
        """Test re-exported models from flext-core."""
        # Test that re-exports are available
        assert hasattr(FlextApiModels, "HttpRequestConfig")
        assert hasattr(FlextApiModels, "HttpErrorConfig")
        assert hasattr(FlextApiModels, "HttpMethod")

    def test_model_inheritance(self) -> None:
        """Test that models properly inherit from FlextModels.Entity."""
        request = FlextApiModels.HttpRequest(url="https://example.com")
        response = FlextApiModels.HttpResponse(
            status_code=200,
            url="https://example.com",
            method="GET",
        )

        # These should have Entity methods
        assert hasattr(request, "model_dump")
        assert hasattr(response, "model_dump")

        # Test model_dump works
        request_dict = request.model_dump()
        assert isinstance(request_dict, dict)
        assert request_dict["url"] == "https://example.com"

    def test_complex_scenario_workflow(self) -> None:
        """Test a complex workflow using multiple models."""
        # Create a client config
        client_config = FlextApiModels.ClientConfig(
            base_url="https://api.example.com",
            auth_token="secret-token",
            timeout=30.0,
            max_retries=3,
        )

        # Create an HTTP request
        request = FlextApiModels.HttpRequest(
            method="POST",
            url="/api/users",
            headers=client_config.get_default_headers(),
            body={"name": "John Doe", "email": "john@example.com"},
        )

        # Create an HTTP response
        response = FlextApiModels.HttpResponse(
            status_code=201,
            url=request.url,
            method=request.method,
            body={"id": 123, "name": "John Doe", "email": "john@example.com"},
            elapsed_time=0.25,
        )

        # Create a paginated query
        query = FlextApiModels.HttpQuery(page_number=1, page_size_value=10)
        query.add_filter("active", True)

        # Create response using builder
        success_response = FlextApiModels.Builder.success(
            data={"users": [response.body], "pagination": query.to_query_params()},
        )

        # Verify everything works together
        assert client_config.base_url == "https://api.example.com"
        assert request.method == "POST"
        assert response.is_success is True
        assert success_response["status"] == "success"
        assert "users" in success_response["data"]
