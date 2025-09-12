"""Advanced tests for FlextApiUtilities to improve coverage.

Tests for utility methods, validation, and edge cases.
Focuses on HTTP validation, response building, and pagination.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from urllib.parse import ParseResult

from flext_core import FlextModels
from flext_tests import FlextTestsMatchers

from flext_api import FlextApiUtilities


class TestFlextApiUtilitiesAdvanced:
    """Advanced tests for FlextApiUtilities to improve coverage."""

    def test_validate_config_http_request(self) -> None:
        """Test validate_config with HttpRequestConfig."""
        config = FlextModels.Http.HttpRequestConfig(
            url="https://test.example.com/api", method="GET"
        )

        result = FlextApiUtilities.validate_config(config)
        FlextTestsMatchers.assert_result_success(result)
        assert isinstance(result.value, dict)

    def test_validate_config_http_error(self) -> None:
        """Test validate_config with HttpErrorConfig."""
        config = FlextModels.Http.HttpErrorConfig(
            status_code=404, error_message="Not found"
        )

        result = FlextApiUtilities.validate_config(config)
        FlextTestsMatchers.assert_result_success(result)
        assert isinstance(result.value, dict)

    def test_validate_config_validation(self) -> None:
        """Test validate_config with ValidationConfig."""
        config = FlextModels.Http.ValidationConfig(validate_ssl=True, timeout=30.0)

        result = FlextApiUtilities.validate_config(config)
        FlextTestsMatchers.assert_result_success(result)
        assert isinstance(result.value, dict)

    def test_validate_url_type_checking(self) -> None:
        """Test validate_url with different input types."""
        # Test with non-string input
        result1 = FlextApiUtilities.validate_url(123)
        FlextTestsMatchers.assert_result_failure(result1)
        assert "Invalid URL format" in result1.error

        result2 = FlextApiUtilities.validate_url([])
        FlextTestsMatchers.assert_result_failure(result2)
        assert "Invalid URL format" in result2.error

        result3 = FlextApiUtilities.validate_url({})
        FlextTestsMatchers.assert_result_failure(result3)
        assert "Invalid URL format" in result3.error

    def test_http_validator_validate_string_empty(self) -> None:
        """Test HttpValidator._validate_string with empty string."""
        result = FlextApiUtilities.HttpValidator._validate_string("")
        FlextTestsMatchers.assert_result_failure(result)
        assert "URL must be a non-empty string" in result.error

    def test_http_validator_validate_string_whitespace(self) -> None:
        """Test HttpValidator._validate_string with whitespace only."""
        result = FlextApiUtilities.HttpValidator._validate_string("   ")
        FlextTestsMatchers.assert_result_success(result)
        # Should pass initial validation, fail later in cleaning

    def test_http_validator_clean_url(self) -> None:
        """Test HttpValidator._clean_url method."""
        result = FlextApiUtilities.HttpValidator._clean_url("  https://test.com  ")
        FlextTestsMatchers.assert_result_success(result)
        assert result.value == "https://test.com"

    def test_http_validator_clean_url_empty_after_cleaning(self) -> None:
        """Test HttpValidator._clean_url with empty result."""
        result = FlextApiUtilities.HttpValidator._clean_url("   ")
        FlextTestsMatchers.assert_result_failure(result)
        assert "URL cannot be empty after cleaning" in result.error

    def test_http_validator_validate_parsed_url_no_scheme(self) -> None:
        """Test HttpValidator._validate_parsed_url without scheme."""
        result = FlextApiUtilities.HttpValidator._validate_parsed_url("example.com")
        FlextTestsMatchers.assert_result_failure(result)
        assert "Invalid URL format" in result.error

    def test_http_validator_validate_parsed_url_invalid_scheme(self) -> None:
        """Test HttpValidator._validate_parsed_url with invalid scheme."""
        result = FlextApiUtilities.HttpValidator._validate_parsed_url(
            "ftp://example.com"
        )
        FlextTestsMatchers.assert_result_failure(result)
        assert "Invalid URL format" in result.error

    def test_http_validator_validate_parsed_url_no_hostname(self) -> None:
        """Test HttpValidator._validate_parsed_url without hostname."""
        result = FlextApiUtilities.HttpValidator._validate_parsed_url("http://")
        FlextTestsMatchers.assert_result_failure(result)
        assert "URL must include hostname" in result.error

    def test_http_validator_validate_url_components_long_hostname(self) -> None:
        """Test HttpValidator._validate_url_components with long hostname."""
        # Create a ParseResult with a very long hostname
        parsed = ParseResult(
            scheme="http",
            netloc="a" * 300,  # Very long hostname
            path="/",
            params="",
            query="",
            fragment="",
        )

        result = FlextApiUtilities.HttpValidator._validate_url_components(
            parsed, "http://" + "a" * 300 + "/"
        )
        FlextTestsMatchers.assert_result_failure(result)
        assert "Hostname too long" in result.error

    def test_http_validator_validate_url_components_invalid_port(self) -> None:
        """Test HttpValidator._validate_url_components with invalid port."""
        # Create a ParseResult with invalid port
        parsed = ParseResult(
            scheme="http",
            netloc="example.com:99999",  # Invalid port
            path="/",
            params="",
            query="",
            fragment="",
        )

        result = FlextApiUtilities.HttpValidator._validate_url_components(
            parsed, "http://example.com:99999/"
        )
        FlextTestsMatchers.assert_result_failure(result)
        assert "Invalid port" in result.error

    def test_http_validator_validate_url_components_long_url(self) -> None:
        """Test HttpValidator._validate_url_components with long URL."""
        # Create a ParseResult with a very long URL
        long_path = "/" + "a" * 10000
        parsed = ParseResult(
            scheme="http",
            netloc="example.com",
            path=long_path,
            params="",
            query="",
            fragment="",
        )

        long_url = "http://example.com" + long_path
        result = FlextApiUtilities.HttpValidator._validate_url_components(
            parsed, long_url
        )
        FlextTestsMatchers.assert_result_failure(result)
        assert "URL too long" in result.error

    def test_http_validator_normalize_url(self) -> None:
        """Test HttpValidator.normalize_url method."""
        result = FlextApiUtilities.HttpValidator.normalize_url(
            "https://example.com/path/"
        )
        FlextTestsMatchers.assert_result_success(result)
        assert result.value == "https://example.com/path"

    def test_http_validator_normalize_url_with_scheme_only(self) -> None:
        """Test HttpValidator.normalize_url with scheme only."""
        result = FlextApiUtilities.HttpValidator.normalize_url("https://")
        FlextTestsMatchers.assert_result_success(result)
        assert result.value == "https://"

    def test_http_validator_validate_http_method_empty(self) -> None:
        """Test HttpValidator.validate_http_method with empty string."""
        result = FlextApiUtilities.HttpValidator.validate_http_method("")
        FlextTestsMatchers.assert_result_failure(result)
        assert "HTTP method must be a non-empty string" in result.error

    def test_http_validator_validate_http_method_case_insensitive(self) -> None:
        """Test HttpValidator.validate_http_method is case insensitive."""
        methods = ["get", "POST", "Put", "delete", "PATCH"]

        for method in methods:
            result = FlextApiUtilities.HttpValidator.validate_http_method(method)
            FlextTestsMatchers.assert_result_success(result)
            assert result.value == method.upper()

    def test_http_validator_validate_http_method_webdav(self) -> None:
        """Test HttpValidator.validate_http_method with WebDAV methods."""
        webdav_methods = ["PROPFIND", "PROPPATCH", "COPY", "MOVE", "LOCK"]

        for method in webdav_methods:
            result = FlextApiUtilities.HttpValidator.validate_http_method(method)
            FlextTestsMatchers.assert_result_success(result)
            assert result.value == method

    def test_http_validator_validate_http_method_invalid(self) -> None:
        """Test HttpValidator.validate_http_method with invalid method."""
        result = FlextApiUtilities.HttpValidator.validate_http_method("INVALID")
        FlextTestsMatchers.assert_result_failure(result)
        assert "Invalid HTTP method" in result.error

    def test_http_validator_validate_status_code_invalid_type(self) -> None:
        """Test HttpValidator.validate_status_code with invalid type."""
        result = FlextApiUtilities.HttpValidator.validate_status_code("not_a_number")
        FlextTestsMatchers.assert_result_failure(result)
        assert "Status code must be a valid integer" in result.error

    def test_http_validator_validate_status_code_ranges(self) -> None:
        """Test HttpValidator.validate_status_code with different ranges."""
        # Test various status codes in different ranges
        status_codes = [
            (100, "1xx Informational"),
            (200, "2xx Success"),
            (300, "3xx Redirection"),
            (400, "4xx Client Error"),
            (500, "5xx Server Error"),
        ]

        for code, _description in status_codes:
            result = FlextApiUtilities.HttpValidator.validate_status_code(code)
            FlextTestsMatchers.assert_result_success(result)
            assert result.value == code

    def test_http_validator_validate_status_code_invalid_range(self) -> None:
        """Test HttpValidator.validate_status_code with invalid range."""
        result = FlextApiUtilities.HttpValidator.validate_status_code(999)
        FlextTestsMatchers.assert_result_failure(result)
        assert "Invalid HTTP status code" in result.error

    def test_response_builder_build_success_response_with_data(self) -> None:
        """Test ResponseBuilder.build_success_response with data."""
        data = {"key": "value", "number": 42}
        result = FlextApiUtilities.ResponseBuilder.build_success_response(
            data=data, message="Success with data", status_code=200
        )

        FlextTestsMatchers.assert_result_success(result)
        response = result.value
        assert response["success"] is True
        assert response["message"] == "Success with data"
        assert response["status_code"] == 200
        assert response["data"] == data
        assert "timestamp" in response
        assert "request_id" in response

    def test_response_builder_build_error_response_with_details(self) -> None:
        """Test ResponseBuilder.build_error_response with details."""
        details = {"field": "email", "reason": "invalid format"}
        result = FlextApiUtilities.ResponseBuilder.build_error_response(
            error="Validation failed",
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details,
        )

        FlextTestsMatchers.assert_result_success(result)
        response = result.value
        assert response["success"] is False
        assert response["message"] == "Validation failed"
        assert response["status_code"] == 422
        assert response["error_code"] == "VALIDATION_ERROR"
        assert response["details"] == details

    def test_pagination_builder_invalid_page(self) -> None:
        """Test PaginationBuilder with invalid page number."""
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=[], total=100, page=0
        )
        FlextTestsMatchers.assert_result_failure(result)
        assert "Page must be >= 1" in result.error

    def test_pagination_builder_invalid_page_size(self) -> None:
        """Test PaginationBuilder with invalid page size."""
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=[], total=100, page_size=0
        )
        FlextTestsMatchers.assert_result_failure(result)
        assert "Page size must be >= 1" in result.error

    def test_pagination_builder_max_page_size_exceeded(self) -> None:
        """Test PaginationBuilder with page size exceeding maximum."""
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=[], total=100, page_size=10000
        )
        FlextTestsMatchers.assert_result_failure(result)
        assert "Page size cannot exceed" in result.error

    def test_pagination_builder_custom_message(self) -> None:
        """Test PaginationBuilder with custom message."""
        data = [{"id": 1}, {"id": 2}]
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=data, total=50, message="Custom success message"
        )

        FlextTestsMatchers.assert_result_success(result)
        response = result.value
        assert response["message"] == "Custom success message"
        assert response["data"] == data
        assert response["pagination"]["total"] == 50

    def test_pagination_builder_edge_case_zero_total(self) -> None:
        """Test PaginationBuilder with zero total."""
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=[], total=0
        )

        FlextTestsMatchers.assert_result_success(result)
        response = result.value
        pagination = response["pagination"]
        assert pagination["total"] == 0
        assert pagination["total_pages"] == 1  # Should have at least 1 page

    def test_pagination_builder_edge_case_single_item(self) -> None:
        """Test PaginationBuilder with single item."""
        data = [{"id": 1}]
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=data, total=1, page_size=10
        )

        FlextTestsMatchers.assert_result_success(result)
        response = result.value
        pagination = response["pagination"]
        assert pagination["total"] == 1
        assert pagination["total_pages"] == 1
        assert pagination["has_next"] is False
        assert pagination["has_previous"] is False

    def test_pagination_builder_edge_case_exact_division(self) -> None:
        """Test PaginationBuilder with exact division."""
        data = [{"id": i} for i in range(20)]
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=data, total=100, page_size=20
        )

        FlextTestsMatchers.assert_result_success(result)
        response = result.value
        pagination = response["pagination"]
        assert pagination["total"] == 100
        assert pagination["total_pages"] == 5  # 100/20 = 5 exactly
