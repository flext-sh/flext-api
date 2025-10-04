"""Focused models tests for maximum coverage improvement.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Literal, cast

import pytest
from flext_core import FlextConstants, FlextTypes
from pydantic import ValidationError

from flext_api import FlextApiModels
from flext_api.constants import FlextApiConstants

# Import HTTP method constants
GET = FlextConstants.Http.Method.GET
POST = FlextConstants.Http.Method.POST
PUT = FlextConstants.Http.Method.PUT
DELETE = FlextConstants.Http.Method.DELETE
PATCH = FlextConstants.Http.Method.PATCH
HEAD = FlextConstants.Http.Method.HEAD
OPTIONS = FlextConstants.Http.Method.OPTIONS


class TestFlextApiModelsFocused:
    """Focused tests to improve models.py coverage from 58% to 80%+.

    This test class has many public methods by design as it provides focused
    test coverage to improve code coverage. Each test method validates a specific
    aspect of the model behavior, which is a legitimate use case for having
    many methods in a test class.
    """

    # =============================================================================
    # HttpRequest Model Tests
    # =============================================================================

    def test_http_request_default_values(self) -> None:
        """Test HttpRequest with default values."""
        request = FlextApiModels.HttpRequest(url="https://api.example.com/test")

        assert request.method == "GET"
        assert request.url == "https://api.example.com/test"
        assert request.headers == {}
        assert request.body is None
        assert request.timeout == 30

    def test_http_request_all_parameters(self) -> None:
        """Test HttpRequest with all parameters set."""
        headers = {"Authorization": "Bearer token", "Content-Type": "application/json"}
        body: FlextTypes.Dict = {"data": "test"}

        request = FlextApiModels.HttpRequest(
            method="POST",
            url="https://api.example.com/create",
            headers=headers,
            body=body,
            timeout=FlextApiConstants.DEVELOPMENT_TIMEOUT,
        )

        assert request.method == "POST"
        assert request.url == "https://api.example.com/create"
        assert request.headers == headers
        assert request.body == body
        assert request.timeout == 60

    def test_http_request_url_validation_empty(self) -> None:
        """Test HttpRequest URL validation with empty URL."""
        with pytest.raises(ValidationError) as exc_info:
            FlextApiModels.HttpRequest(url="")

        assert "Invalid URL" in str(exc_info.value)

    def test_http_request_url_validation_none(self) -> None:
        """Test HttpRequest URL validation with None URL."""
        # Test with invalid URL type
        with pytest.raises(ValidationError) as exc_info:
            FlextApiModels.HttpRequest(
                url=cast("str", None),
            )  # Intentionally testing None type

        # Pydantic validates type first, so None fails string type validation
        assert "Input should be a valid string" in str(exc_info.value)

    def test_http_request_url_validation_invalid_format(self) -> None:
        """Test HttpRequest URL validation with invalid format."""
        with pytest.raises(ValidationError) as exc_info:
            FlextApiModels.HttpRequest(url="invalid-url")

        assert "Invalid URL format" in str(exc_info.value)

    def test_http_request_url_validation_valid_formats(self) -> None:
        """Test HttpRequest URL validation with valid formats."""
        valid_urls = [
            "https://api.example.com",
            f"http://localhost:{FlextApiConstants.DEFAULT_BASE_URL.split(':')[-1] if ':' in FlextApiConstants.DEFAULT_BASE_URL else '8000'}",
            "/api/v1/users",
        ]

        for url in valid_urls:
            request = FlextApiModels.HttpRequest(url=url)
            assert request.url == url

    def test_http_request_url_validation_strips_whitespace(self) -> None:
        """Test HttpRequest URL validation strips whitespace."""
        request = FlextApiModels.HttpRequest(url="  https://api.example.com  ")
        assert request.url == "https://api.example.com"

    def test_http_request_headers_validation_empty_values(self) -> None:
        """Test HttpRequest headers validation filters empty values."""
        headers = {
            "Valid-Header": "value",
            "Empty-Header": "",
            "  Whitespace-Key  ": "  whitespace-value  ",
        }

        request = FlextApiModels.HttpRequest(url="https://test.com", headers=headers)

        # Should filter out empty values, strip whitespace (None values not allowed in FlextTypes.StringDict)
        assert request.headers["Valid-Header"] == "value"
        assert "Empty-Header" not in request.headers
        assert request.headers["Whitespace-Key"] == "whitespace-value"

    def test_http_request_method_literals(self) -> None:
        """Test HttpRequest accepts all valid HTTP methods."""
        valid_methods: list[Literal[GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS]] = [
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "PATCH",
            "HEAD",
            "OPTIONS",
        ]

        for method in valid_methods:
            request = FlextApiModels.HttpRequest(method=method, url="https://test.com")
            assert request.method == method

    # =============================================================================
    # HttpResponse Model Tests
    # =============================================================================

    def test_http_response_basic_creation(self) -> None:
        """Test HttpResponse basic creation."""
        response = FlextApiModels.HttpResponse(
            status_code=200,
            body="Success",
            url="https://api.example.com/test",
            method="GET",
        )

        assert response.status_code == 200
        assert response.body == "Success"
        assert response.headers == {}
        assert response.url == "https://api.example.com/test"
        assert response.method == "GET"

    def test_http_response_with_all_fields(self) -> None:
        """Test HttpResponse with all fields."""
        headers = {"Content-Type": "application/json"}
        body: FlextTypes.Dict = {"result": "success"}

        response = FlextApiModels.HttpResponse(
            status_code=201,
            body=body,
            headers=headers,
            url="https://api.example.com/create",
            method="POST",
        )

        assert response.status_code == 201
        assert response.body == body
        assert response.headers == headers
        assert response.url == "https://api.example.com/create"
        assert response.method == "POST"

    def test_http_response_is_success_2xx(self) -> None:
        """Test HttpResponse.is_success for 2xx status codes."""
        success_codes = [200, 201, 202, 204, 299]

        for code in success_codes:
            response = FlextApiModels.HttpResponse(
                status_code=code,
                url="https://test.com",
                method="GET",
            )
            assert response.is_success is True

    def test_http_response_is_success_non_2xx(self) -> None:
        """Test HttpResponse.is_success for non-2xx status codes."""
        non_success_codes = [100, 199, 300, 301, 400, 404, 500, 503]

        for code in non_success_codes:
            response = FlextApiModels.HttpResponse(
                status_code=code,
                url="https://test.com",
                method="GET",
            )
            assert response.is_success is False

    def test_http_response_is_client_error_4xx(self) -> None:
        """Test HttpResponse.is_client_error for 4xx status codes."""
        client_error_codes = [400, 401, 403, 404, 422, 499]

        for code in client_error_codes:
            response = FlextApiModels.HttpResponse(
                status_code=code,
                url="https://test.com",
                method="GET",
            )
            assert response.is_client_error is True

    def test_http_response_is_client_error_non_4xx(self) -> None:
        """Test HttpResponse.is_client_error for non-4xx status codes."""
        non_client_error_codes = [200, 300, 399, 500, 503]

        for code in non_client_error_codes:
            response = FlextApiModels.HttpResponse(
                status_code=code,
                url="https://test.com",
                method="GET",
            )
            assert response.is_client_error is False

    def test_http_response_is_server_error_5xx(self) -> None:
        """Test HttpResponse.is_server_error for 5xx status codes."""
        server_error_codes = [500, 501, 502, 503, 504, 599]

        for code in server_error_codes:
            response = FlextApiModels.HttpResponse(
                status_code=code,
                url="https://test.com",
                method="GET",
            )
            assert response.is_server_error is True

    def test_http_response_is_server_error_non_5xx(self) -> None:
        """Test HttpResponse.is_server_error for non-5xx status codes."""
        non_server_error_codes = [200, 300, 400, 499]

        for code in non_server_error_codes:
            response = FlextApiModels.HttpResponse(
                status_code=code,
                url="https://test.com",
                method="GET",
            )
            assert response.is_server_error is False

    def test_http_response_is_redirect_3xx(self) -> None:
        """Test HttpResponse.is_redirect for 3xx status codes."""
        redirect_codes = [300, 301, 302, 303, 304, 307, 308, 399]

        for code in redirect_codes:
            response = FlextApiModels.HttpResponse(
                status_code=code,
                url="https://test.com",
                method="GET",
            )
            assert response.is_redirect is True

    def test_http_response_is_redirect_non_3xx(self) -> None:
        """Test HttpResponse.is_redirect for non-3xx status codes."""
        non_redirect_codes = [200, 299, 400, 500]

        for code in non_redirect_codes:
            response = FlextApiModels.HttpResponse(
                status_code=code,
                url="https://test.com",
                method="GET",
            )
            assert response.is_redirect is False

    def test_http_response_status_code_validation_valid(self) -> None:
        """Test HttpResponse status code validation with valid codes."""
        valid_codes = [100, 200, 404, 500, 599]

        for code in valid_codes:
            response = FlextApiModels.HttpResponse(
                status_code=code,
                url="https://test.com",
                method="GET",
            )
            assert response.status_code == code

    def test_http_response_status_code_validation_invalid(self) -> None:
        """Test HttpResponse status code validation with invalid codes."""
        invalid_codes = [99, 600, 700, -1]

        for code in invalid_codes:
            with pytest.raises(ValidationError) as exc_info:
                FlextApiModels.HttpResponse(
                    status_code=code,
                    url="https://test.com",
                    method="GET",
                )
            # Pydantic field validation happens first with ge/le constraints
            assert (
                "ensure this value is greater than or equal to 100"
                in str(exc_info.value)
                or "ensure this value is less than or equal to 599"
                in str(exc_info.value)
                or "Input should be greater than or equal to 100" in str(exc_info.value)
                or "Input should be less than or equal to 599" in str(exc_info.value)
            )

    def test_http_response_status_code_validation_non_integer(self) -> None:
        """Test HttpResponse status code validation with non-integer."""
        # Pydantic 2 automatically converts "200" to 200, so let's test with a truly invalid type
        # Test with invalid status code type
        invalid_status: str = "invalid"
        with pytest.raises(ValidationError) as exc_info:
            FlextApiModels.HttpResponse(
                status_code=cast(
                    "int",
                    invalid_status,
                ),  # Intentionally testing invalid type
                url="https://test.com",
                method="GET",
            )

        # Pydantic should fail on type conversion
        assert "Input should be a valid integer" in str(
            exc_info.value,
        ) or "invalid literal for int()" in str(exc_info.value)

    # =============================================================================
    # ClientConfig Model Tests
    # =============================================================================

    def test_client_config_default_values(self) -> None:
        """Test ClientConfig with default values."""
        config = FlextApiModels.ClientConfig()

        assert (
            config.base_url
            == f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
        )
        assert config.timeout == float(FlextConstants.Network.DEFAULT_TIMEOUT)
        assert config.max_retries == FlextConstants.Reliability.MAX_RETRY_ATTEMPTS
        assert config.headers == {}
        assert config.auth_token is None
        assert config.api_key is None

    def test_client_config_all_parameters(self) -> None:
        """Test ClientConfig with all parameters."""
        headers = {"User-Agent": "TestClient/1.0"}

        config = FlextApiModels.ClientConfig(
            base_url="https://api.production.com",
            timeout=FlextApiConstants.DEVELOPMENT_TIMEOUT,
            max_retries=5,
            headers=headers,
            auth_token="bearer_token_123",
            api_key="api_key_456",
        )

        assert config.base_url == "https://api.production.com"
        assert config.timeout == 60.0
        assert config.max_retries == 5
        assert config.headers == headers
        assert config.auth_token == "bearer_token_123"
        assert config.api_key == "api_key_456"

    def test_client_config_base_url_validation_empty(self) -> None:
        """Test ClientConfig base_url validation with empty URL."""
        with pytest.raises(ValidationError) as exc_info:
            FlextApiModels.ClientConfig(base_url="")

        assert "URL must be a non-empty string" in str(exc_info.value)

    def test_client_config_base_url_validation_whitespace(self) -> None:
        """Test ClientConfig base_url validation with whitespace URL."""
        with pytest.raises(ValidationError) as exc_info:
            FlextApiModels.ClientConfig(base_url="   ")

        assert "URL must be a non-empty string" in str(exc_info.value)

    def test_client_config_base_url_validation_invalid_format(self) -> None:
        """Test ClientConfig base_url validation with invalid format."""
        with pytest.raises(ValidationError) as exc_info:
            FlextApiModels.ClientConfig(base_url="invalid-url")

        assert "URL must be a non-empty string" in str(exc_info.value)

    def test_client_config_base_url_validation_strips_whitespace(self) -> None:
        """Test ClientConfig base_url validation strips whitespace."""
        config = FlextApiModels.ClientConfig(base_url="  https://api.example.com  ")
        assert config.base_url == "https://api.example.com"

    def test_client_config_timeout_validation(self) -> None:
        """Test ClientConfig timeout validation."""
        # Valid timeout
        config = FlextApiModels.ClientConfig(timeout=45.5)
        assert config.timeout == 45.5

        # Invalid timeout (zero or negative)
        with pytest.raises(ValidationError):
            FlextApiModels.ClientConfig(timeout=0)

        with pytest.raises(ValidationError):
            FlextApiModels.ClientConfig(timeout=-1)

    def test_client_config_max_retries_validation(self) -> None:
        """Test ClientConfig max_retries validation."""
        # Valid retries
        config = FlextApiModels.ClientConfig(max_retries=10)
        assert config.max_retries == 10

        config_zero = FlextApiModels.ClientConfig(max_retries=0)
        assert config_zero.max_retries == 0

        # Invalid retries (negative)
        with pytest.raises(ValidationError):
            FlextApiModels.ClientConfig(max_retries=-1)

    def test_client_config_get_auth_header_with_token(self) -> None:
        """Test ClientConfig.get_auth_header with auth_token."""
        config = FlextApiModels.ClientConfig(auth_token="my_token")

        auth_header = config.get_auth_header()

        assert auth_header == {"Authorization": "Bearer my_token"}

    def test_client_config_get_auth_header_with_api_key(self) -> None:
        """Test ClientConfig.get_auth_header with api_key."""
        config = FlextApiModels.ClientConfig(api_key="my_api_key")

        auth_header = config.get_auth_header()

        assert auth_header == {"Authorization": "Bearer my_api_key"}

    def test_client_config_get_auth_header_token_priority(self) -> None:
        """Test ClientConfig.get_auth_header auth_token takes priority over api_key."""
        config = FlextApiModels.ClientConfig(
            auth_token="token_priority",
            api_key="api_key_fallback",
        )

        auth_header = config.get_auth_header()

        assert auth_header == {"Authorization": "Bearer token_priority"}

    def test_client_config_get_auth_header_no_auth(self) -> None:
        """Test ClientConfig.get_auth_header with no authentication."""
        config = FlextApiModels.ClientConfig()

        auth_header = config.get_auth_header()

        assert auth_header == {}

    def test_client_config_get_default_headers(self) -> None:
        """Test ClientConfig.get_default_headers method."""
        custom_headers = {"Custom-Header": "custom_value"}
        config = FlextApiModels.ClientConfig(
            headers=custom_headers,
            auth_token="test_token",
        )

        default_headers = config.get_default_headers()

        assert default_headers["User-Agent"] == "FlextAPI/0.9.0"
        assert default_headers["Custom-Header"] == "custom_value"
        assert default_headers["Authorization"] == "Bearer test_token"

    def test_client_config_get_default_headers_no_auth(self) -> None:
        """Test ClientConfig.get_default_headers without authentication."""
        config = FlextApiModels.ClientConfig()

        default_headers = config.get_default_headers()

        assert default_headers["User-Agent"] == "FlextAPI/0.9.0"
        assert "Authorization" not in default_headers

    # =============================================================================
    # HttpQuery Model Tests
    # =============================================================================

    def test_http_query_default_values(self) -> None:
        """Test HttpQuery with default values."""
        query = FlextApiModels.HttpQuery()

        assert query.filter_conditions == {}
        assert query.sort_fields == []
        assert query.page_number == 1
        assert query.page_size_value == 20

    def test_http_query_with_parameters(self) -> None:
        """Test HttpQuery with all parameters."""
        filter_conditions = {"name": "test", "active": True}
        sort_fields = ["name", "-created_at"]

        query = FlextApiModels.HttpQuery(
            filters=filter_conditions,
            sort_fields=sort_fields,
            page=2,
            page_size=50,
        )

        assert query.filter_conditions == filter_conditions
        assert query.sort_fields == sort_fields
        assert query.page_number == 2
        assert query.page_size_value == 50

    def test_http_query_direct_field_access(self) -> None:
        """Test HttpQuery with direct field names."""
        query = FlextApiModels.HttpQuery(
            filters={"status": "active"},
            page=3,
            page_size=100,
        )

        assert query.filter_conditions == {"status": "active"}
        assert query.page_number == 3
        assert query.page_size_value == 100

    def test_http_query_page_number_validation(self) -> None:
        """Test HttpQuery page_number validation."""
        # Valid page numbers
        query = FlextApiModels.HttpQuery(page=1)
        assert query.page_number == 1

        query_large = FlextApiModels.HttpQuery(page=100)
        assert query_large.page_number == 100

        # Invalid page numbers
        with pytest.raises(ValidationError):
            FlextApiModels.HttpQuery(page=0)

        with pytest.raises(ValidationError):
            FlextApiModels.HttpQuery(page=-1)

    def test_http_query_page_size_validation(self) -> None:
        """Test HttpQuery page_size validation."""
        # Valid page sizes
        query = FlextApiModels.HttpQuery(page_size=1)
        assert query.page_size_value == 1

        query_max = FlextApiModels.HttpQuery(page_size=FlextApiConstants.MAX_PAGE_SIZE)
        assert query_max.page_size_value == FlextApiConstants.MAX_PAGE_SIZE

        # Invalid page sizes
        with pytest.raises(ValidationError):
            FlextApiModels.HttpQuery(page_size=0)

        with pytest.raises(ValidationError):
            FlextApiModels.HttpQuery(page_size=-1)

        with pytest.raises(ValidationError):
            FlextApiModels.HttpQuery(page_size=1001)

    def test_http_query_add_filter_success(self) -> None:
        """Test HttpQuery.add_filter successful cases."""
        query = FlextApiModels.HttpQuery()

        result = query.add_filter("status", "active")
        assert result.is_success
        assert query.filter_conditions["status"] == "active"

    def test_http_query_add_filter_strips_key(self) -> None:
        """Test HttpQuery.add_filter strips whitespace from key."""
        query = FlextApiModels.HttpQuery()

        result = query.add_filter("  name  ", "test_value")
        assert result.is_success
        assert query.filter_conditions["name"] == "test_value"
        assert "  name  " not in query.filter_conditions

    def test_http_query_add_filter_empty_key(self) -> None:
        """Test HttpQuery.add_filter with empty key."""
        query = FlextApiModels.HttpQuery()

        result = query.add_filter("", "value")
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None and "Filter key cannot be empty" in result.error

    def test_http_query_add_filter_whitespace_key(self) -> None:
        """Test HttpQuery.add_filter with whitespace-only key."""
        query = FlextApiModels.HttpQuery()

        result = query.add_filter("   ", "value")
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None and "Filter key cannot be empty" in result.error

    def test_http_query_to_query_params(self) -> None:
        """Test HttpQuery.to_query_params method."""
        filter_conditions: FlextTypes.Dict = {"status": "active", "type": "user"}
        query = FlextApiModels.HttpQuery(
            filters=filter_conditions,
            page=3,
            page_size=25,
        )

        params = query.to_query_params()

        assert params["page"] == 3
        assert params["page_size"] == 25
        assert params["filters"] == filter_conditions
        assert params["status"] == "active"  # Flattened filter
        assert params["type"] == "user"  # Flattened filter

    # =============================================================================
    # PaginationConfig Model Tests
    # =============================================================================

    def test_pagination_config_default_values(self) -> None:
        """Test PaginationConfig with default values."""
        config = FlextApiModels.PaginationConfig()

        assert config.page_size == 20
        assert config.current_page == 1
        assert config.max_pages is None
        assert config.total == 0

    def test_pagination_config_with_parameters(self) -> None:
        """Test PaginationConfig with all parameters."""
        config = FlextApiModels.PaginationConfig(
            page_size=50,
            page=3,
            max_pages=10,
            total=500,
        )

        assert config.page_size == 50
        assert config.current_page == 3
        assert config.max_pages == 10
        assert config.total == 500

    def test_pagination_config_init_with_page_parameter(self) -> None:
        """Test PaginationConfig.__init__ with page parameter."""
        config = FlextApiModels.PaginationConfig(page=5, total=100)

        assert config.current_page == 5
        assert config.total == 100

    def test_pagination_config_page_property(self) -> None:
        """Test PaginationConfig.current_page property."""
        config = FlextApiModels.PaginationConfig(page=7)

        assert config.current_page == 7
        assert config.current_page == 7

    def test_pagination_config_validation_page_size(self) -> None:
        """Test PaginationConfig page_size validation."""
        # Valid page sizes
        config = FlextApiModels.PaginationConfig(page_size=1)
        assert config.page_size == 1

        config_max = FlextApiModels.PaginationConfig(
            page_size=FlextApiConstants.MAX_PAGE_SIZE
        )
        assert config_max.page_size == FlextApiConstants.MAX_PAGE_SIZE

        # Invalid page sizes
        with pytest.raises(ValidationError):
            FlextApiModels.PaginationConfig(page_size=0)

        with pytest.raises(ValidationError):
            FlextApiModels.PaginationConfig(page_size=-1)

        with pytest.raises(ValidationError):
            FlextApiModels.PaginationConfig(page_size=1001)

    def test_pagination_config_validation_current_page(self) -> None:
        """Test PaginationConfig current_page validation."""
        # Valid current pages
        config = FlextApiModels.PaginationConfig(page=1)
        assert config.current_page == 1

        config_large = FlextApiModels.PaginationConfig(page=999)
        assert config_large.current_page == 999

        # Invalid current pages
        with pytest.raises(ValidationError):
            FlextApiModels.PaginationConfig(page=0)

        with pytest.raises(ValidationError):
            FlextApiModels.PaginationConfig(page=-1)

    def test_pagination_config_validation_max_pages(self) -> None:
        """Test PaginationConfig max_pages validation."""
        # Valid max_pages
        config = FlextApiModels.PaginationConfig(max_pages=5)
        assert config.max_pages == 5

        config_none = FlextApiModels.PaginationConfig(max_pages=None)
        assert config_none.max_pages is None

        # Invalid max_pages
        with pytest.raises(ValidationError):
            FlextApiModels.PaginationConfig(max_pages=0)

        with pytest.raises(ValidationError):
            FlextApiModels.PaginationConfig(max_pages=-1)

    def test_pagination_config_validation_total(self) -> None:
        """Test PaginationConfig total validation."""
        # Valid totals
        config = FlextApiModels.PaginationConfig(total=0)
        assert config.total == 0

        config_large = FlextApiModels.PaginationConfig(total=999999)
        assert config_large.total == 999999

        # Invalid totals
        with pytest.raises(ValidationError):
            FlextApiModels.PaginationConfig(total=-1)

    # =============================================================================
    # Builder Class Tests
    # =============================================================================

    def test_builder_create_success_response(self) -> None:
        """Test Builder.create with success response type."""
        builder = FlextApiModels.Builder()

        response = builder.create(
            response_type="success",
            data={"user": "john"},
            message="User retrieved",
        )

        assert response["status"] == "success"
        assert response["data"] == {"user": "john"}
        assert response["message"] == "User retrieved"
        assert "timestamp" in response
        assert "request_id" in response

    def test_builder_create_error_response(self) -> None:
        """Test Builder.create with error response type."""
        builder = FlextApiModels.Builder()

        response = builder.create(
            response_type="error",
            message="Validation failed",
            code="VALIDATION_ERROR",
        )

        assert isinstance(response, dict)
        assert response["status"] == "error"
        assert isinstance(response["error"], dict)
        assert response["error"]["message"] == "Validation failed"
        assert response["error"]["code"] == "VALIDATION_ERROR"
        assert "timestamp" in response
        assert "request_id" in response

    def test_builder_create_default_success(self) -> None:
        """Test Builder.create defaults to success type."""
        builder = FlextApiModels.Builder()

        response = builder.create(data={"test": "value"})

        assert response["status"] == "success"
        assert response["data"] == {"test": "value"}
        assert not response["message"]

    def test_builder_success_static_method(self) -> None:
        """Test Builder.success static method."""
        response = FlextApiModels.Builder.success(
            data={"result": "ok"},
            message="Operation completed",
        )

        assert response["status"] == "success"
        assert response["data"] == {"result": "ok"}
        assert response["message"] == "Operation completed"
        assert "timestamp" in response
        assert "request_id" in response

    def test_builder_success_with_defaults(self) -> None:
        """Test Builder.success with default parameters."""
        response = FlextApiModels.Builder.success()

        assert response["status"] == "success"
        assert response["data"] is None
        assert not response["message"]
        assert "timestamp" in response
        assert "request_id" in response

    def test_builder_error_static_method(self) -> None:
        """Test Builder.error static method."""
        response = FlextApiModels.Builder.error(
            message="Something went wrong",
            code="INTERNAL_ERROR",
        )

        assert isinstance(response, dict)
        assert response["status"] == "error"
        assert isinstance(response["error"], dict)
        assert response["error"]["message"] == "Something went wrong"
        assert response["error"]["code"] == "INTERNAL_ERROR"
        assert "timestamp" in response
        assert "request_id" in response

    def test_builder_error_with_default_code(self) -> None:
        """Test Builder.error with default error code."""
        response = FlextApiModels.Builder.error("Error occurred")

        assert isinstance(response, dict)
        assert response["status"] == "error"
        assert isinstance(response["error"], dict)
        assert response["error"]["message"] == "Error occurred"
        assert response["error"]["code"] == "error"
        assert "timestamp" in response
        assert "request_id" in response

    # =============================================================================
    # Model Aliases Tests
    # =============================================================================

    def test_model_aliases(self) -> None:
        """Test that model aliases work correctly."""
        # Test that HttpRequest and HttpResponse are available
        assert hasattr(FlextApiModels, "HttpRequest")
        assert hasattr(FlextApiModels, "HttpResponse")
        assert FlextApiModels.HttpRequest is not None
        assert FlextApiModels.HttpResponse is not None

    def test_model_aliases_functional(self) -> None:
        """Test that model aliases are functionally equivalent."""
        # Create instances using main classes
        request = FlextApiModels.HttpRequest(url="https://test.com")
        api_request = FlextApiModels.HttpRequest(url="https://test.com")

        assert isinstance(request, FlextApiModels.HttpRequest)
        assert isinstance(api_request, FlextApiModels.HttpRequest)
        assert request.url == api_request.url

        response = FlextApiModels.HttpResponse(
            status_code=200,
            url="https://test.com",
            method="GET",
        )
        api_response = FlextApiModels.HttpResponse(
            status_code=200,
            url="https://test.com",
            method="GET",
        )

        assert isinstance(response, FlextApiModels.HttpResponse)
        assert isinstance(api_response, FlextApiModels.HttpResponse)
        assert response.status_code == api_response.status_code
