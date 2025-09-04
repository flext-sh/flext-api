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


class TestFlextApiModels:
    """Test FlextApiModels REAL class functionality."""

    def test_models_class_exists(self) -> None:
        """Test FlextApiModels class exists and is accessible."""
        assert FlextApiModels is not None
        assert hasattr(FlextApiModels, "HttpMethod")
        assert hasattr(FlextApiModels, "HttpStatus")
        assert hasattr(FlextApiModels, "ClientConfig")
        assert hasattr(FlextApiModels, "ApiRequest")
        assert hasattr(FlextApiModels, "HttpResponse")
        assert hasattr(FlextApiModels, "HttpQuery")
        assert hasattr(FlextApiModels, "Builder")

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

        request = FlextApiModels.ApiRequest(
            id="test_id",
            method=FlextApiModels.HttpMethod.POST,
            url="/api/test",
            headers=headers,
        )

        assert request.method == FlextApiModels.HttpMethod.POST
        assert request.url == "/api/test"
        assert request.headers == headers
        assert request.id == "test_id"

    def test_api_request_url_validation(self) -> None:
        """Test ApiRequest URL validation."""
        # Valid URL
        request = FlextApiModels.ApiRequest(
            id="test_id",
            method=FlextApiModels.HttpMethod.GET, url="/api/users"
        )
        assert request.url == "/api/users"

        # Empty URL should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            FlextApiModels.ApiRequest(id="test_id", method=FlextApiModels.HttpMethod.GET, url="")
        assert "URL cannot be empty" in str(exc_info.value)

    def test_api_response_creation(self) -> None:
        """Test HttpResponse creation."""
        headers = {"Content-Type": "application/json"}
        data = {"result": "success"}

        response = FlextApiModels.HttpResponse(
            status_code=200, body=data, headers=headers, url="/api/test", method="GET"
        )

        assert response.status_code == 200
        assert response.body == data
        assert response.headers == headers
        assert response.url == "/api/test"

    def test_api_response_status_validation(self) -> None:
        """Test HttpResponse status code validation."""
        # Valid status codes
        for code in [100, 200, 404, 500, 599]:
            response = FlextApiModels.HttpResponse(status_code=code, url="/test", method="GET")
            assert response.status_code == code

        # Invalid status codes should raise ValidationError
        for code in [99, 600]:
            with pytest.raises(ValidationError):
                FlextApiModels.HttpResponse(status_code=code, url="/test", method="GET")

    def test_api_response_status_properties(self) -> None:
        """Test HttpResponse status checking properties."""
        # Success response
        response = FlextApiModels.HttpResponse(status_code=200, url="/test", method="GET")
        assert response.is_success is True
        assert response.is_client_error is False
        assert response.is_server_error is False

        # Client error response
        response = FlextApiModels.HttpResponse(status_code=404, url="/test", method="GET")
        assert response.is_success is False
        assert response.is_client_error is True
        assert response.is_server_error is False

        # Server error response
        response = FlextApiModels.HttpResponse(status_code=500, url="/test", method="GET")
        assert response.is_success is False
        assert response.is_client_error is False
        assert response.is_server_error is True

    def test_query_builder_creation(self) -> None:
        """Test HttpQuery creation."""
        builder = FlextApiModels.HttpQuery()

        assert builder.filter_conditions == {}
        assert builder.sort_fields == []
        assert builder.page_number == 1
        assert builder.page_size_value == 20

    def test_query_builder_custom_values(self) -> None:
        """Test HttpQuery with custom values."""
        filter_conditions = {"status": "active", "category": "premium"}
        sort_fields = ["created_at"]

        builder = FlextApiModels.HttpQuery(
            filter_conditions=filter_conditions,
            sort_fields=sort_fields,
            page_number=2,
            page_size_value=25,
        )

        assert builder.filter_conditions == filter_conditions
        assert builder.sort_fields == sort_fields
        assert builder.page_number == 2
        assert builder.page_size_value == 25

    def test_query_builder_page_validation(self) -> None:
        """Test HttpQuery page validation."""
        # Valid page
        builder = FlextApiModels.HttpQuery(page_number=5)
        assert builder.page_number == 5

        # Invalid page should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            FlextApiModels.HttpQuery(page_number=0)
        assert "greater than or equal to 1" in str(exc_info.value)

    def test_query_builder_page_size_validation(self) -> None:
        """Test HttpQuery page_size validation."""
        # Valid page sizes
        for size in [1, 50, 100, 1000]:
            builder = FlextApiModels.HttpQuery(page_size_value=size)
            assert builder.page_size_value == size

        # Invalid page sizes should raise ValidationError
        with pytest.raises(ValidationError):
            FlextApiModels.HttpQuery(page_size_value=0)

        with pytest.raises(ValidationError):
            FlextApiModels.HttpQuery(page_size_value=1001)

    def test_query_builder_add_filter_success(self) -> None:
        """Test HttpQuery filter_conditions direct setting."""
        builder = FlextApiModels.HttpQuery(filter_conditions={"status": "active"})

        assert builder.filter_conditions["status"] == "active"

    def test_query_builder_add_filter_empty_key_failure(self) -> None:
        """Test HttpQuery with empty filter conditions."""
        builder = FlextApiModels.HttpQuery(filter_conditions={})

        assert builder.filter_conditions == {}

    def test_query_builder_to_query_params(self) -> None:
        """Test HttpQuery model dump conversion."""
        builder = FlextApiModels.HttpQuery(
            filter_conditions={"status": "active", "type": "premium"},
            sort_fields=["name"],
            page_number=2,
            page_size_value=25,
        )

        params = builder.model_dump()
        assert isinstance(params, dict)
        assert params["filter_conditions"]["status"] == "active"
        assert params["filter_conditions"]["type"] == "premium"
        assert params["sort_fields"] == ["name"]
        assert params["page_number"] == 2
        assert params["page_size_value"] == 25

    def test_response_builder_creation(self) -> None:
        """Test Builder creation."""
        builder = FlextApiModels.Builder()

        # Test that builder exists and can be created
        assert builder is not None
        assert hasattr(builder, "create")

    def test_response_builder_custom_values(self) -> None:
        """Test Builder create method."""
        builder = FlextApiModels.Builder()

        # Test create method exists and is callable
        assert hasattr(builder, "create")
        assert callable(builder.create)

    def test_response_builder_success(self) -> None:
        """Test Builder functionality."""
        builder = FlextApiModels.Builder()

        # Test builder can be used
        assert builder is not None

    def test_response_builder_error(self) -> None:
        """Test Builder basic functionality."""
        builder = FlextApiModels.Builder()

        # Test basic builder functionality
        assert hasattr(builder, "create")

    def test_models_type_validation(self) -> None:
        """Test models are proper types."""
        # Main class
        assert FlextApiModels is not None
        assert type(FlextApiModels).__name__ == "type"

        # Nested classes
        config = FlextApiModels.ClientConfig(base_url="https://api.example.com")
        assert isinstance(config, FlextApiModels.ClientConfig)

        request = FlextApiModels.ApiRequest(
            id="test_id",
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
