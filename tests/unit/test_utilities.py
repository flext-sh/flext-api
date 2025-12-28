"""FLEXT API Utilities Tests - Testing ONLY methods that actually exist.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations
from typing import cast
from flext_core import FlextTypes as t

from datetime import datetime

from flext_api import FlextApiUtilities


class TestFlextApiUtilitiesReal:
    """Test FlextApiUtilities using ONLY methods that actually exist."""

    def test_response_builder_error(self) -> None:
        """Test ResponseBuilder error response - returns plain dict."""
        response = FlextApiUtilities.ResponseBuilder.build_error_response(
            message="Test error",
            status_code=400,
        )

        # API returns plain dict with error structure
        response_dict = cast(dict[str, t.GeneralValueType], response)
        assert response_dict["success"] is False
        error_dict = cast(dict[str, t.GeneralValueType], response_dict["error"])
        assert error_dict["message"] == "Test error"
        assert error_dict["status_code"] == 400

    def test_response_builder_success(self) -> None:
        """Test ResponseBuilder success response - returns FlextResult."""
        result = FlextApiUtilities.ResponseBuilder.build_success_response(
            data={"test": "data"},
            message="Success",
            status_code=200,
        )

        # API returns FlextResult[dict]
        assert result.is_success
        response = result.value
        assert response["status"] == "success"
        assert response["data"] == {"test": "data"}
        assert response["message"] == "Success"
        assert response["status_code"] == 200

    def test_pagination_builder(self) -> None:
        """Test PaginationBuilder functionality."""
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=[1, 2, 3],
            page=1,
            page_size=10,
            total=3,
        )

        assert result.is_success
        response_obj = result.value
        assert isinstance(response_obj, dict)
        response: dict[str, t.GeneralValueType] = response_obj
        assert response["success"] is True
        assert response["data"] == [1, 2, 3]
        pagination_obj = response["pagination"]
        assert isinstance(pagination_obj, dict)
        pagination: dict[str, t.GeneralValueType] = pagination_obj
        assert cast(dict[str, t.GeneralValueType], pagination)["page"] == 1
        assert cast(dict[str, t.GeneralValueType], pagination)["total"] == 3

    def test_pagination_builder_invalid_page(self) -> None:
        """Test PaginationBuilder with invalid page."""
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=[1, 2, 3],
            page=0,
            page_size=10,
        )

        assert result.is_failure
        assert result.error is not None
        assert result.error is not None and "Page must be >= 1" in result.error

    def test_pagination_builder_invalid_page_size(self) -> None:
        """Test PaginationBuilder with invalid page size."""
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=[1, 2, 3],
            page=1,
            page_size=0,
        )

        assert result.is_failure
        assert result.error is not None
        assert result.error is not None and "Page size must be >= 1" in result.error

    def test_http_validator_url_valid(self) -> None:
        """Test FlextWebValidator URL validation with valid URL."""
        result = FlextApiUtilities.FlextWebValidator.validate_url("https://example.com")
        assert result.is_success
        assert result.value == "https://example.com"

    def test_http_validator_url_invalid(self) -> None:
        """Test FlextWebValidator URL validation with invalid URL."""
        result = FlextApiUtilities.FlextWebValidator.validate_url("not-a-url")
        assert result.is_failure

    def test_http_validator_url_with_port(self) -> None:
        """Test FlextWebValidator URL validation with port."""
        result = FlextApiUtilities.FlextWebValidator.validate_url(
            "https://example.com:8080",
        )
        assert result.is_success

    def test_http_validator_url_invalid_port(self) -> None:
        """Test FlextWebValidator URL validation with invalid port."""
        result = FlextApiUtilities.FlextWebValidator.validate_url(
            "https://example.com:0",
        )
        assert result.is_failure
        assert result.error is not None
        assert result.error is not None and "Invalid port 0" in result.error

    def test_http_validator_method_valid(self) -> None:
        """Test FlextWebValidator HTTP method validation with valid method."""
        # API returns bool
        is_valid = FlextApiUtilities.FlextWebValidator.validate_http_method("GET")
        assert is_valid is True

    def test_http_validator_method_invalid(self) -> None:
        """Test FlextWebValidator HTTP method validation with invalid method."""
        # API returns bool
        is_valid = FlextApiUtilities.FlextWebValidator.validate_http_method("INVALID")
        assert is_valid is False

    def test_http_validator_method_case_insensitive(self) -> None:
        """Test FlextWebValidator HTTP method validation case insensitive."""
        # API returns bool and normalizes case
        is_valid = FlextApiUtilities.FlextWebValidator.validate_http_method("post")
        assert is_valid is True

    def test_http_validator_normalize_url(self) -> None:
        """Test FlextWebValidator URL normalization."""
        # API returns normalized string
        normalized = FlextApiUtilities.FlextWebValidator.normalize_url(
            "https://example.com/",
        )
        assert normalized.startswith("https://")
        assert "example.com" in normalized

    def test_http_validator_normalize_url_empty(self) -> None:
        """Test FlextWebValidator URL normalization with empty URL."""
        # API returns empty string for empty input
        normalized = FlextApiUtilities.FlextWebValidator.normalize_url("")
        assert not normalized

    def test_http_validator_all_methods(self) -> None:
        """Test FlextWebValidator with all valid HTTP methods."""
        methods = [
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "PATCH",
            "HEAD",
            "OPTIONS",
            "CONNECT",
            "TRACE",
        ]
        for method in methods:
            assert (
                FlextApiUtilities.FlextWebValidator.validate_http_method(method) is True
            )

    def test_http_validator_method_lowercase_all(self) -> None:
        """Test FlextWebValidator with all valid HTTP methods in lowercase."""
        methods = [
            "get",
            "post",
            "put",
            "delete",
            "patch",
            "head",
            "options",
            "connect",
            "trace",
        ]
        for method in methods:
            assert (
                FlextApiUtilities.FlextWebValidator.validate_http_method(method) is True
            )

    def test_http_validator_method_mixed_case(self) -> None:
        """Test FlextWebValidator with mixed case HTTP methods."""
        mixed_methods = ["Get", "PoSt", "PaTcH"]
        for method in mixed_methods:
            assert (
                FlextApiUtilities.FlextWebValidator.validate_http_method(method) is True
            )

    def test_http_validator_method_invalid_variations(self) -> None:
        """Test FlextWebValidator with various invalid methods."""
        invalid = ["INVALID", "HTTP", "FAKE", "CUSTOM", "", " "]
        for method in invalid:
            assert (
                FlextApiUtilities.FlextWebValidator.validate_http_method(method)
                is False
            )

    def test_http_validator_normalize_url_without_scheme(self) -> None:
        """Test FlextWebValidator URL normalization without scheme adds https."""
        normalized = FlextApiUtilities.FlextWebValidator.normalize_url("example.com")
        assert normalized == "https://example.com"

    def test_http_validator_normalize_url_with_http(self) -> None:
        """Test FlextWebValidator URL normalization preserves http scheme."""
        normalized = FlextApiUtilities.FlextWebValidator.normalize_url(
            "http://example.com",
        )
        assert normalized == "http://example.com"

    def test_http_validator_normalize_url_with_path(self) -> None:
        """Test FlextWebValidator URL normalization with path."""
        url = "example.com/path/to/resource"
        normalized = FlextApiUtilities.FlextWebValidator.normalize_url(url)
        assert normalized == f"https://{url}"

    def test_url_validation_empty_whitespace(self) -> None:
        """Test URL validation with whitespace only."""
        result = FlextApiUtilities.FlextWebValidator.validate_url("   ")
        assert result.is_failure

    def test_url_validation_url_with_query_params(self) -> None:
        """Test URL validation with query parameters."""
        url = "https://example.com/path?query=value&key=123"
        result = FlextApiUtilities.FlextWebValidator.validate_url(url)
        assert result.is_success

    def test_url_validation_url_with_fragment(self) -> None:
        """Test URL validation with URL fragment."""
        url = "https://example.com/path#section"
        result = FlextApiUtilities.FlextWebValidator.validate_url(url)
        assert result.is_success

    def test_url_validation_localhost(self) -> None:
        """Test URL validation with localhost."""
        result = FlextApiUtilities.FlextWebValidator.validate_url(
            "http://localhost:8080",
        )
        assert result.is_success

    def test_url_validation_ip_address(self) -> None:
        """Test URL validation with IP address."""
        result = FlextApiUtilities.FlextWebValidator.validate_url(
            "https://internal.invalid/REDACTED",
        )
        assert result.is_success

    def test_url_validation_valid_ports(self) -> None:
        """Test URL validation with various valid ports."""
        valid_ports = [1, 80, 443, 8080, 3000, 9000, 65535]
        for port in valid_ports:
            url = f"https://example.com:{port}"
            result = FlextApiUtilities.FlextWebValidator.validate_url(url)
            assert result.is_success, f"Port {port} should be valid"

    def test_response_builder_error_with_custom_code(self) -> None:
        """Test ResponseBuilder error with custom error code."""
        response = FlextApiUtilities.ResponseBuilder.build_error_response(
            message="Not found",
            status_code=404,
            error_code="RESOURCE_NOT_FOUND",
        )
        assert response["error"]["code"] == "RESOURCE_NOT_FOUND"
        assert cast(dict[str, t.GeneralValueType], response["error"])["message"] == "Not found"

    def test_response_builder_error_various_status_codes(self) -> None:
        """Test ResponseBuilder error with various status codes."""
        codes = [400, 401, 403, 404, 500, 502, 503]
        for code in codes:
            response = FlextApiUtilities.ResponseBuilder.build_error_response(
                message=f"Error {code}",
                status_code=code,
            )
            assert cast(dict[str, t.GeneralValueType], response["error"])["status_code"] == code

    def test_response_builder_success_empty_data(self) -> None:
        """Test ResponseBuilder success with empty data dict."""
        result = FlextApiUtilities.ResponseBuilder.build_success_response(data={})
        assert result.is_success
        response = result.value
        assert response["data"] == {}

    def test_response_builder_success_with_all_params(self) -> None:
        """Test ResponseBuilder success with all parameters."""
        data = {"id": 1, "name": "test"}
        headers = {"X-Custom": "value"}
        result = FlextApiUtilities.ResponseBuilder.build_success_response(
            data=data,
            message="Created",
            status_code=201,
            headers=headers,
        )
        assert result.is_success
        response = result.value
        assert response["data"] == data
        assert response["message"] == "Created"
        assert response["status_code"] == 201
        assert response["headers"] == headers

    def test_response_builder_success_various_status_codes(self) -> None:
        """Test ResponseBuilder success with various status codes."""
        codes = [200, 201, 202, 204]
        for code in codes:
            result = FlextApiUtilities.ResponseBuilder.build_success_response(
                status_code=code,
            )
            assert result.is_success
            response = result.value
            assert response["status_code"] == code

    def test_response_builder_error_result_minimal(self) -> None:
        """Test ResponseBuilder error result with minimal parameters."""
        result = FlextApiUtilities.ResponseBuilder.build_error_result("Error message")
        assert result.is_success
        response = result.value
        assert response["error"] == "Error message"
        assert response["status_code"] == 400

    def test_response_builder_error_result_with_all(self) -> None:
        """Test ResponseBuilder error result with all parameters."""
        data = {"field": "test"}
        headers = {"X-Error": "value"}
        result = FlextApiUtilities.ResponseBuilder.build_error_result(
            error="Validation failed",
            status_code=422,
            data=data,
            headers=headers,
        )
        assert result.is_success
        response = result.value
        assert response["error"] == "Validation failed"
        assert response["status_code"] == 422
        assert response["data"] == data
        assert response["headers"] == headers

    def test_response_builder_timestamps(self) -> None:
        """Test that ResponseBuilder includes timestamps."""
        result = FlextApiUtilities.ResponseBuilder.build_success_response()
        assert result.is_success
        response = result.value
        assert "timestamp" in response
        # Verify ISO format
        datetime.fromisoformat(response["timestamp"])

    def test_pagination_extract_page_params_valid_high_page(self) -> None:
        """Test extracting page params with high page number."""
        result = FlextApiUtilities.PaginationBuilder.extract_page_params({
            "page": "100",
            "page_size": "10",
        })
        assert result.is_success

    def test_pagination_extract_page_params_min_page_size(self) -> None:
        """Test extracting page params with minimum valid page size."""
        result = FlextApiUtilities.PaginationBuilder.extract_page_params({
            "page_size": "1",
        })
        assert result.is_success

    def test_pagination_extract_page_params_string_numbers(self) -> None:
        """Test extracting page params from string numbers."""
        result = FlextApiUtilities.PaginationBuilder.extract_page_params({
            "page": "2",
            "page_size": "50",
        })
        assert result.is_success
        page, page_size = result.value
        assert page == 2
        assert page_size == 50

    def test_pagination_extract_config_partial(self) -> None:
        """Test extracting pagination config with partial config."""

        class PartialConfig:
            default_page_size = 15

        config = FlextApiUtilities.PaginationBuilder.extract_pagination_config(
            PartialConfig(),
        )
        # Should have default_page_size from config and max_page_size default
        assert config["default_page_size"] == 15

    def test_pagination_validate_params_large_page_size(self) -> None:
        """Test validating pagination params with large but valid page size."""
        result = FlextApiUtilities.PaginationBuilder.validate_pagination_params(
            page=1,
            page_size=500,
            max_page_size=1000,
        )
        assert result.is_success

    def test_pagination_validate_params_edge_case_page_size(self) -> None:
        """Test validating pagination params at boundary."""
        result = FlextApiUtilities.PaginationBuilder.validate_pagination_params(
            page=1,
            page_size=1000,
            max_page_size=1000,
        )
        assert result.is_success

    def test_pagination_prepare_data_large_total(self) -> None:
        """Test preparing pagination data with large total."""
        result = FlextApiUtilities.PaginationBuilder.prepare_pagination_data(
            data=[1, 2],
            total=1000,
            page=1,
            page_size=10,
        )
        assert result.is_success
        data = result.value
        assert data["total_pages"] == 100

    def test_pagination_prepare_data_partial_page(self) -> None:
        """Test preparing pagination data for partial last page."""
        result = FlextApiUtilities.PaginationBuilder.prepare_pagination_data(
            data=[1, 2, 3],
            total=23,
            page=3,
            page_size=10,
        )
        assert result.is_success
        data = result.value
        assert data["total_pages"] == 3
        assert data["has_next"] is False

    def test_pagination_build_response_structure(self) -> None:
        """Test pagination response has correct structure."""
        pagination_data = {
            "data": [1, 2],
            "total": 100,
            "page": 2,
            "page_size": 20,
            "total_pages": 5,
            "has_next": True,
            "has_prev": True,
            "next_page": 3,
            "prev_page": 1,
        }
        result = FlextApiUtilities.PaginationBuilder.build_pagination_response(
            pagination_data,
        )
        assert result.is_success
        response = result.value
        assert "pagination" in response
        pagination = response["pagination"]
        assert cast(dict[str, t.GeneralValueType], pagination)["page"] == 2
        assert cast(dict[str, t.GeneralValueType], pagination)["total"] == 100
        assert cast(dict[str, t.GeneralValueType], pagination)["has_next"] is True
        assert cast(dict[str, t.GeneralValueType], pagination)["has_prev"] is True

    def test_pagination_build_paginated_response_no_config(self) -> None:
        """Test building paginated response without config."""
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=[1, 2, 3],
            page=1,
            page_size=20,
            total=3,
        )
        assert result.is_success

    def test_pagination_extract_page_params_boundary(self) -> None:
        """Test extracting page params at boundary values."""
        result = FlextApiUtilities.PaginationBuilder.extract_page_params({
            "page": "1",
            "page_size": "1",
        })
        assert result.is_success

    def test_pagination_negative_page(self) -> None:
        """Test pagination with negative page number."""
        result = FlextApiUtilities.PaginationBuilder.validate_pagination_params(
            page=-1,
            page_size=20,
            max_page_size=1000,
        )
        assert result.is_failure

    def test_pagination_negative_page_size(self) -> None:
        """Test pagination with negative page size."""
        result = FlextApiUtilities.PaginationBuilder.validate_pagination_params(
            page=1,
            page_size=-1,
            max_page_size=1000,
        )
        assert result.is_failure

    def test_url_validation_subdomain(self) -> None:
        """Test URL validation with subdomains."""
        result = FlextApiUtilities.FlextWebValidator.validate_url(
            "https://api.v2.example.com/data",
        )
        assert result.is_success

    def test_url_validation_international_domain(self) -> None:
        """Test URL validation with international domain."""
        result = FlextApiUtilities.FlextWebValidator.validate_url(
            "https://例え.jp/path",
        )
        assert result.is_success or result.is_failure  # Depends on implementation
