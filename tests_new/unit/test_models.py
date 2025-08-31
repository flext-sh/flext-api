"""Tests for flext_api.models module - REAL classes only.

Tests using only REAL classes:
- FlextApiModels and nested classes

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api import FlextApiModels


class TestFlextApiModels:
    """Test FlextApiModels REAL class functionality."""

    def test_http_method_enum(self) -> None:
        """Test HttpMethod enum."""
        # Should have all standard HTTP methods
        assert FlextApiModels.HttpMethod.GET == "GET"
        assert FlextApiModels.HttpMethod.POST == "POST"
        assert FlextApiModels.HttpMethod.PUT == "PUT"
        assert FlextApiModels.HttpMethod.DELETE == "DELETE"
        assert FlextApiModels.HttpMethod.PATCH == "PATCH"
        assert FlextApiModels.HttpMethod.HEAD == "HEAD"
        assert FlextApiModels.HttpMethod.OPTIONS == "OPTIONS"

    def test_http_status_enum(self) -> None:
        """Test HttpStatus enum."""
        # Should have status categories
        assert FlextApiModels.HttpStatus.SUCCESS == "success"
        assert FlextApiModels.HttpStatus.ERROR == "error"
        assert FlextApiModels.HttpStatus.PENDING == "pending"
        assert FlextApiModels.HttpStatus.TIMEOUT == "timeout"

    def test_client_config_model(self) -> None:
        """Test ClientConfig model."""
        config = FlextApiModels.ClientConfig(
            base_url="https://api.example.com",
            timeout=30.0,
            max_retries=3,
            headers={"Authorization": "Bearer test"}
        )

        assert config.base_url == "https://api.example.com"
        assert config.timeout == 30.0
        assert config.max_retries == 3
        assert config.headers["Authorization"] == "Bearer test"

    def test_client_config_validation(self) -> None:
        """Test ClientConfig validation."""
        # Valid config should work
        config = FlextApiModels.ClientConfig(base_url="https://api.example.com")
        assert config.base_url == "https://api.example.com"

        # Invalid base URL should fail
        with pytest.raises(ValueError, match="Base URL"):
            FlextApiModels.ClientConfig(base_url="")

        with pytest.raises(ValueError, match="Base URL"):
            FlextApiModels.ClientConfig(base_url="invalid-url")

        # Invalid timeout should fail
        with pytest.raises(ValueError):
            FlextApiModels.ClientConfig(base_url="https://api.example.com", timeout=0)

    def test_api_request_model(self) -> None:
        """Test ApiRequest model."""
        request = FlextApiModels.ApiRequest(
            method=FlextApiModels.HttpMethod.POST,
            url="https://api.example.com/users",
            headers={"Content-Type": "application/json"},
            data={"name": "John", "email": "john@example.com"}
        )

        assert request.method == FlextApiModels.HttpMethod.POST
        assert request.url == "https://api.example.com/users"
        assert request.headers["Content-Type"] == "application/json"
        assert request.data["name"] == "John"

    def test_api_request_validation(self) -> None:
        """Test ApiRequest validation."""
        # Valid request should work
        request = FlextApiModels.ApiRequest(
            method=FlextApiModels.HttpMethod.GET,
            url="https://api.example.com"
        )
        assert request.url == "https://api.example.com"

        # Empty URL should fail
        with pytest.raises(ValueError, match="URL cannot be empty"):
            FlextApiModels.ApiRequest(
                method=FlextApiModels.HttpMethod.GET,
                url=""
            )

    def test_api_response_model(self) -> None:
        """Test ApiResponse model."""
        response = FlextApiModels.ApiResponse(
            status_code=200,
            url="https://api.example.com/users",
            data={"id": 123, "name": "John"},
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 200
        assert response.url == "https://api.example.com/users"
        assert response.data["id"] == 123
        assert response.headers["Content-Type"] == "application/json"

    def test_api_response_properties(self) -> None:
        """Test ApiResponse status properties."""
        # Success response
        success_response = FlextApiModels.ApiResponse(
            status_code=200,
            url="https://api.example.com"
        )
        assert success_response.is_success is True
        assert success_response.is_client_error is False
        assert success_response.is_server_error is False

        # Client error response
        client_error = FlextApiModels.ApiResponse(
            status_code=400,
            url="https://api.example.com"
        )
        assert client_error.is_success is False
        assert client_error.is_client_error is True
        assert client_error.is_server_error is False

        # Server error response
        server_error = FlextApiModels.ApiResponse(
            status_code=500,
            url="https://api.example.com"
        )
        assert server_error.is_success is False
        assert server_error.is_client_error is False
        assert server_error.is_server_error is True

    def test_query_builder_model(self) -> None:
        """Test QueryBuilder model."""
        query = FlextApiModels.QueryBuilder(
            filters={"status": "active"},
            sort_by="created_at",
            sort_order="desc",
            page=2,
            page_size=25
        )

        assert query.filters["status"] == "active"
        assert query.sort_by == "created_at"
        assert query.sort_order == "desc"
        assert query.page == 2
        assert query.page_size == 25

    def test_query_builder_add_filter(self) -> None:
        """Test QueryBuilder add_filter method."""
        query = FlextApiModels.QueryBuilder()

        # Add valid filter
        result = query.add_filter("role", "admin")
        assert result.success
        assert query.filters["role"] == "admin"

        # Add invalid filter (empty key)
        result = query.add_filter("", "value")
        assert not result.success
        assert "empty" in result.error.lower()

    def test_query_builder_to_query_params(self) -> None:
        """Test QueryBuilder to_query_params method."""
        query = FlextApiModels.QueryBuilder(
            filters={"status": "active", "role": "admin"},
            sort_by="name",
            sort_order="asc",
            page=1,
            page_size=10
        )

        result = query.to_query_params()
        assert result.success

        params = result.data
        assert params["status"] == "active"
        assert params["role"] == "admin"
        assert params["sort_by"] == "name"
        assert params["sort_order"] == "asc"
        assert params["page"] == 1
        assert params["page_size"] == 10

    def test_response_builder_model(self) -> None:
        """Test ResponseBuilder model."""
        builder = FlextApiModels.ResponseBuilder(
            status_code=201,
            message="Resource created"
        )

        assert builder.status_code == 201
        assert builder.message == "Resource created"

    def test_response_builder_success(self) -> None:
        """Test ResponseBuilder success method."""
        builder = FlextApiModels.ResponseBuilder()

        result = builder.success(
            data={"id": 123, "name": "Test"},
            message="Operation successful"
        )

        assert result.success
        response = result.data
        assert response["status"] == "success"
        assert response["status_code"] == 200
        assert response["data"]["id"] == 123
        assert response["message"] == "Operation successful"

    def test_response_builder_error(self) -> None:
        """Test ResponseBuilder error method."""
        builder = FlextApiModels.ResponseBuilder()

        result = builder.error("Validation failed", 400)

        assert result.success
        response = result.data
        assert response["status"] == "error"
        assert response["status_code"] == 400
        assert response["data"] is None
        assert response["message"] == "Validation failed"
