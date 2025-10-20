"""Unit tests for flext-api models using FLEXT-pure patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT.
"""

from __future__ import annotations

from flext_api import FlextApiModels


class TestFlextApiModelsFlextPure:
    """Test FlextApiModels using FLEXT-pure patterns with direct construction."""

    def test_http_request_creation(self) -> None:
        """Test HttpRequest model creation."""
        request = FlextApiModels.HttpRequest(
            method="GET",
            url="https://api.example.com/test",
            headers={"Accept": "application/json"},
        )

        assert request.method == "GET"
        assert request.url == "https://api.example.com/test"
        assert request.headers["Accept"] == "application/json"
        assert request.timeout == 30.0  # Default timeout

    def test_http_response_creation(self) -> None:
        """Test HttpResponse model creation."""
        response = FlextApiModels.HttpResponse(
            status_code=200,
            headers={"Content-Type": "application/json"},
            body={"data": "test"},
        )

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert response.body == {"data": "test"}
        assert response.is_success is True

    def test_http_response_success_codes(self) -> None:
        """Test HTTP response success detection."""
        success_codes = [200, 201, 202, 204]

        for code in success_codes:
            response = FlextApiModels.HttpResponse(status_code=code)
            assert response.is_success is True, f"Status {code} should be success"

    def test_http_response_error_codes(self) -> None:
        """Test HTTP response error detection."""
        error_codes = [400, 401, 403, 404, 500, 502, 503]

        for code in error_codes:
            response = FlextApiModels.HttpResponse(status_code=code)
            assert response.is_success is False, f"Status {code} should be error"

    def test_client_config_creation(self) -> None:
        """Test ClientConfig model creation."""
        config = FlextApiModels.ClientConfig(
            base_url="https://api.example.com",
            timeout=45.0,
            max_retries=5,
            headers={"Authorization": "Bearer token"},
        )

        assert config.base_url == "https://api.example.com"
        assert config.timeout == 45.0
        assert config.max_retries == 5
        assert config.headers["Authorization"] == "Bearer token"

    def test_pagination_model(self) -> None:
        """Test Pagination model."""
        pagination = FlextApiModels.HttpPagination(
            page=2,
            page_size=25,
            total_items=100,
            total_pages=4,
        )

        assert pagination.page == 2
        assert pagination.page_size == 25
        assert pagination.total_items == 100
        assert pagination.has_next is True
        assert pagination.has_previous is True
        assert pagination.offset == 25  # (2-1) * 25

    def test_error_model_creation(self) -> None:
        """Test Error model creation."""
        error = FlextApiModels.Error(
            message="Test error message",
            error_code="TEST_ERROR",
            status_code=404,
        )

        assert error.message == "Test error message"
        assert error.error_code == "TEST_ERROR"
        assert error.status_code == 404
        assert error.is_client_error is True

    def test_query_params_model(self) -> None:
        """Test QueryParams model."""
        query = FlextApiModels.QueryParams(
            params={"search": "test", "limit": ["10", "20"]}
        )

        assert query.get_param("search") == "test"
        assert query.get_param("limit") == ["10", "20"]

    def test_headers_model(self) -> None:
        """Test Headers model."""
        headers = FlextApiModels.Headers(
            headers={"Content-Type": "application/json", "Authorization": "Bearer"}
        )

        assert headers.get_header("content-type") == "application/json"
        assert headers.get_header("authorization") == "Bearer"
