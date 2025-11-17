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

    def test_http_request_with_body(self) -> None:
        """Test HttpRequest with request body."""
        request = FlextApiModels.HttpRequest(
            method="POST",
            url="https://api.example.com/users",
            body={"name": "John", "email": "john@example.com"},
            headers={"Content-Type": "application/json"},
        )

        assert request.method == "POST"
        assert request.body == {"name": "John", "email": "john@example.com"}
        assert request.headers["Content-Type"] == "application/json"

    def test_http_request_custom_timeout(self) -> None:
        """Test HttpRequest with custom timeout."""
        request = FlextApiModels.HttpRequest(
            method="GET",
            url="https://api.example.com/test",
            timeout=60.0,
        )

        assert request.timeout == 60.0

    def test_http_response_with_headers(self) -> None:
        """Test HttpResponse with various response headers."""
        response = FlextApiModels.HttpResponse(
            status_code=201,
            headers={
                "Content-Type": "application/json",
                "X-Custom-Header": "custom-value",
                "Set-Cookie": "session=abc123",
            },
            body={"id": 1, "name": "Created"},
        )

        assert response.status_code == 201
        assert response.headers["Content-Type"] == "application/json"
        assert response.headers["X-Custom-Header"] == "custom-value"
        assert response.is_success is True

    def test_error_model_client_errors(self) -> None:
        """Test Error model detection for client errors."""
        error_codes = [400, 401, 403, 404, 405, 409, 422]

        for code in error_codes:
            error = FlextApiModels.Error(
                message="Client error",
                error_code=f"ERROR_{code}",
                status_code=code,
            )
            assert error.is_client_error is True, f"Code {code} should be client error"

    def test_error_model_server_errors(self) -> None:
        """Test Error model detection for server errors."""
        error_codes = [500, 501, 502, 503, 504]

        for code in error_codes:
            error = FlextApiModels.Error(
                message="Server error",
                error_code=f"ERROR_{code}",
                status_code=code,
            )
            assert error.is_client_error is False, f"Code {code} should be server error"

    def test_pagination_model_edge_cases(self) -> None:
        """Test Pagination model edge cases."""
        # First page
        pagination = FlextApiModels.HttpPagination(
            page=1,
            page_size=25,
            total_items=100,
            total_pages=4,
        )

        assert pagination.has_previous is False
        assert pagination.has_next is True
        assert pagination.offset == 0

        # Last page
        last_page = FlextApiModels.HttpPagination(
            page=4,
            page_size=25,
            total_items=100,
            total_pages=4,
        )

        assert last_page.has_previous is True
        assert last_page.has_next is False

    def test_query_params_missing_param(self) -> None:
        """Test QueryParams with missing parameter."""
        query = FlextApiModels.QueryParams(params={"search": "test"})

        assert query.get_param("search") == "test"
        assert query.get_param("missing") == ""  # Returns empty string, not None

    def test_headers_case_insensitive(self) -> None:
        """Test Headers model case-insensitive access."""
        headers = FlextApiModels.Headers(
            headers={"Content-Type": "application/json", "X-Custom": "value"}
        )

        assert headers.get_header("CONTENT-TYPE") == "application/json"
        assert headers.get_header("content-type") == "application/json"
        assert headers.get_header("Content-Type") == "application/json"
        assert headers.get_header("x-custom") == "value"
        assert headers.get_header("X-CUSTOM") == "value"

    def test_client_config_defaults(self) -> None:
        """Test ClientConfig default values."""
        config = FlextApiModels.ClientConfig(base_url="https://api.example.com")

        assert config.base_url == "https://api.example.com"
        assert isinstance(config.timeout, (int, float))
        assert config.max_retries >= 0

    def test_http_response_with_complex_body(self) -> None:
        """Test HttpResponse with complex nested body."""
        response = FlextApiModels.HttpResponse(
            status_code=200,
            body={
                "data": {
                    "users": [
                        {"id": 1, "name": "Alice"},
                        {"id": 2, "name": "Bob"},
                    ],
                    "meta": {"total": 2, "page": 1},
                }
            },
        )

        assert response.status_code == 200
        assert response.is_success is True
        assert isinstance(response.body, dict)
        assert "data" in response.body

    def test_http_request_minimal(self) -> None:
        """Test HttpRequest with minimal parameters."""
        request = FlextApiModels.HttpRequest(
            method="GET",
            url="https://api.example.com",
        )

        assert request.method == "GET"
        assert request.url == "https://api.example.com"
        assert request.headers == {}
        assert request.body == {}  # Empty dict, not None

    def test_http_request_all_parameters(self) -> None:
        """Test HttpRequest with all parameters."""
        request = FlextApiModels.HttpRequest(
            method="PUT",
            url="https://api.example.com/resource/1",
            headers={"Authorization": "Bearer token"},
            body={"data": "update"},
            timeout=120.0,
        )

        assert request.method == "PUT"
        assert request.url == "https://api.example.com/resource/1"
        assert request.headers["Authorization"] == "Bearer token"
        assert request.body == {"data": "update"}
        assert request.timeout == 120.0

    def test_http_response_minimal(self) -> None:
        """Test HttpResponse with minimal parameters."""
        response = FlextApiModels.HttpResponse(status_code=200)

        assert response.status_code == 200
        assert response.is_success is True
        assert response.headers == {}
        assert response.body == {}  # Empty dict, not None

    def test_http_response_all_parameters(self) -> None:
        """Test HttpResponse with all parameters."""
        response = FlextApiModels.HttpResponse(
            status_code=201,
            headers={"Location": "/resource/1"},
            body={"id": 1},
        )

        assert response.status_code == 201
        assert response.is_success is True
        assert response.headers["Location"] == "/resource/1"
        assert response.body == {"id": 1}

    def test_pagination_single_page(self) -> None:
        """Test Pagination with single page of results."""
        pagination = FlextApiModels.HttpPagination(
            page=1,
            page_size=50,
            total_items=25,
            total_pages=1,
        )

        assert pagination.page == 1
        assert pagination.has_previous is False
        assert pagination.has_next is False
        assert pagination.offset == 0

    def test_pagination_middle_page(self) -> None:
        """Test Pagination in middle of results."""
        pagination = FlextApiModels.HttpPagination(
            page=5,
            page_size=10,
            total_items=100,
            total_pages=10,
        )

        assert pagination.has_previous is True
        assert pagination.has_next is True
        assert pagination.offset == 40  # (5-1) * 10

    def test_error_model_minimal(self) -> None:
        """Test Error model with minimal parameters."""
        error = FlextApiModels.Error(
            message="An error occurred",
            status_code=500,
        )

        assert error.message == "An error occurred"
        assert error.status_code == 500
        assert error.error_code is None or isinstance(error.error_code, str)

    def test_error_model_with_code(self) -> None:
        """Test Error model with error code."""
        error = FlextApiModels.Error(
            message="Unauthorized",
            error_code="UNAUTHORIZED",
            status_code=401,
        )

        assert error.message == "Unauthorized"
        assert error.error_code == "UNAUTHORIZED"
        assert error.status_code == 401
        assert error.is_client_error is True

    def test_query_params_empty(self) -> None:
        """Test QueryParams with empty parameters."""
        query = FlextApiModels.QueryParams(params={})

        assert query.get_param("any_key") == ""  # Returns empty string, not None

    def test_query_params_multiple_values(self) -> None:
        """Test QueryParams with multiple values per key."""
        query = FlextApiModels.QueryParams(
            params={"tags": ["python", "testing", "api"]}
        )

        assert query.get_param("tags") == ["python", "testing", "api"]

    def test_query_params_mixed_types(self) -> None:
        """Test QueryParams with mixed value types."""
        query = FlextApiModels.QueryParams(
            params={
                "name": "test",
                "ids": ["1", "2", "3"],
                "active": "true",
            }
        )

        assert query.get_param("name") == "test"
        assert query.get_param("ids") == ["1", "2", "3"]
        assert query.get_param("active") == "true"

    def test_headers_empty(self) -> None:
        """Test Headers with empty headers."""
        headers = FlextApiModels.Headers(headers={})

        assert headers.get_header("any_header") == ""  # Returns empty string, not None

    def test_headers_multiple_values(self) -> None:
        """Test Headers model with multiple headers."""
        headers = FlextApiModels.Headers(
            headers={
                "Content-Type": "application/json",
                "Content-Length": "1234",
                "Cache-Control": "no-cache",
                "X-Request-ID": "req-123",
            }
        )

        assert headers.get_header("content-type") == "application/json"
        assert headers.get_header("content-length") == "1234"
        assert headers.get_header("cache-control") == "no-cache"
        assert headers.get_header("x-request-id") == "req-123"

    def test_client_config_all_fields(self) -> None:
        """Test ClientConfig with all fields."""
        config = FlextApiModels.ClientConfig(
            base_url="https://api.example.com",
            timeout=30.0,
            max_retries=3,
            headers={
                "User-Agent": "MyApp/1.0",
                "Authorization": "Bearer token",
            },
        )

        assert config.base_url == "https://api.example.com"
        assert config.timeout == 30.0
        assert config.max_retries == 3
        assert "User-Agent" in config.headers
        assert "Authorization" in config.headers

    def test_http_request_methods_variety(self) -> None:
        """Test HttpRequest with various HTTP methods."""
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]

        for method in methods:
            request = FlextApiModels.HttpRequest(
                method=method,
                url="https://api.example.com",
            )
            assert request.method == method

    def test_http_response_status_code_ranges(self) -> None:
        """Test HttpResponse success detection across status code ranges."""
        # Test various 2xx codes
        for code in [200, 201, 202, 203, 204, 205, 206]:
            response = FlextApiModels.HttpResponse(status_code=code)
            assert response.is_success is True, f"2xx status {code} should be success"

    def test_http_response_redirect_codes(self) -> None:
        """Test HttpResponse with redirect codes."""
        redirect_codes = [300, 301, 302, 303, 304, 307, 308]

        for code in redirect_codes:
            response = FlextApiModels.HttpResponse(status_code=code)
            # Redirect codes are not successful responses
            assert response.is_success is False

    def test_error_is_server_error(self) -> None:
        """Test Error detection of server errors."""
        server_error_codes = [500, 501, 502, 503, 504, 505]

        for code in server_error_codes:
            error = FlextApiModels.Error(
                message="Server error",
                status_code=code,
            )
            assert error.is_client_error is False

    def test_pagination_large_dataset(self) -> None:
        """Test Pagination with large dataset."""
        pagination = FlextApiModels.HttpPagination(
            page=50,
            page_size=100,
            total_items=10000,
            total_pages=100,
        )

        assert pagination.page == 50
        assert pagination.offset == 4900  # (50-1) * 100
        assert pagination.has_previous is True
        assert pagination.has_next is True

    def test_headers_default_values(self) -> None:
        """Test Headers with various default values."""
        headers1 = FlextApiModels.Headers(headers={"Content-Type": "text/plain"})
        assert (
            headers1.get_header("missing-header") == ""
        )  # Returns empty string, not None

    def test_query_params_special_characters(self) -> None:
        """Test QueryParams with special characters."""
        query = FlextApiModels.QueryParams(
            params={
                "search": "hello world",
                "filter": "name=john&age=30",
                "url": "https://example.com",
            }
        )

        assert "hello world" in query.get_param("search")
        assert "=" in query.get_param("filter")
        assert "://" in query.get_param("url")
