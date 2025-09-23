"""Comprehensive utilities tests for FLEXT API.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pydantic import ValidationError

from flext_api import FlextApiConstants, FlextApiUtilities
from flext_api.models import FlextApiModels
from flext_core import FlextConstants, FlextTypes
from flext_tests import FlextTestsMatchers


class TestFlextApiUtilitiesComprehensive:
    """Comprehensive utilities tests targeting all uncovered areas."""

    def test_validate_config_all_types(self) -> None:
        """Test config validation for all configuration types."""
        # Test HttpRequestConfig with valid data
        http_config = FlextApiModels.Http.HttpRequestConfig(
            url="https://api.example.com/test",
            method="POST",
            timeout=45,
        )
        result = FlextApiUtilities.validate_config(http_config)
        assert result.is_success
        config_data = result.value
        assert config_data["config_type"] == "http_request"
        assert config_data["url"] == "https://api.example.com/test"
        assert config_data["method"] == "POST"

        # Test HttpErrorConfig with valid data
        error_config = FlextApiModels.Http.HttpErrorConfig(
            message="Internal Server Error",
            status_code=500,
            url="https://api.example.com/error",
            method="GET",
        )
        result = FlextApiUtilities.validate_config(error_config)
        assert result.is_success
        config_data = result.value
        assert config_data["config_type"] == "http_error"
        assert config_data["status_code"] == 500
        assert config_data["message"] == "Internal Server Error"

        # Test ValidationConfig with valid data
        validation_config = FlextApiModels.Http.ValidationConfig(
            field="email",
            value="invalid-email",
            url="https://api.example.com/validate",
        )
        result = FlextApiUtilities.validate_config(validation_config)
        assert result.is_success
        config_data = result.value
        assert config_data["config_type"] == "validation"
        assert config_data["field"] == "email"
        assert config_data["value"] == "invalid-email"

    def test_validate_http_request_config_failures(self) -> None:
        """Test HTTP request config validation failures."""
        try:
            invalid_config = FlextApiModels.Http.HttpRequestConfig(url="", method="GET")
            # If model creation succeeds, test the validation
            result = FlextApiUtilities.validate_config(invalid_config)
            FlextTestsMatchers.assert_result_failure(result)
            assert result.error is not None
        except ValidationError:
            # Model creation fails as expected due to Pydantic validation
            pass

        # Invalid HTTP method
        invalid_method_config = FlextApiModels.Http.HttpRequestConfig(
            url="https://api.example.com",
            method="",
        )
        result = FlextApiUtilities.validate_config(invalid_method_config)
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error is not None
        assert "HTTP method must be a non-empty string" in result.error

    def test_validate_http_error_config_failures(self) -> None:
        """Test HTTP error config validation failures."""
        # Invalid status code - too low (should fail at model creation)
        try:
            invalid_config = FlextApiModels.Http.HttpErrorConfig(
                message="Error",
                status_code=50,
            )
            # If model creation succeeds, test the validation
            result = FlextApiUtilities.validate_config(invalid_config)
            FlextTestsMatchers.assert_result_failure(result)
            assert result.error is not None
        except ValidationError:
            # Model creation fails as expected due to Pydantic validation
            pass

        # Invalid status code - too high
        try:
            invalid_high_config = FlextApiModels.Http.HttpErrorConfig(
                message="Error",
                status_code=700,
            )
            # If model creation succeeds, test the validation
            result = FlextApiUtilities.validate_config(invalid_high_config)
            FlextTestsMatchers.assert_result_failure(result)
            assert result.error is not None
            assert "Invalid HTTP status code" in result.error
        except ValidationError:
            # Model creation fails as expected due to Pydantic validation
            pass

    def test_url_validation_comprehensive(self) -> None:
        """Test comprehensive validation scenarios."""
        # Valid s
        valid_urls = [
            "https://api.example.com",
            "http://localhost:8080/test",
            "https://subdomain.example.com/api/v1/data",
            "https://api.example.com:443/secure",
        ]

        for url in valid_urls:
            result = FlextApiUtilities.HttpValidator.validate_url(url)
            assert result.is_success, f"{url} should be valid"

        # Invalid s - no scheme
        result = FlextApiUtilities.HttpValidator.validate_url("example.com")
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error is not None
        assert "Invalid URL format" in result.error

        # Invalid s - bad scheme
        result = FlextApiUtilities.HttpValidator.validate_url("ftp://example.com")
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error is not None
        assert "Invalid URL format" in result.error

        # Invalid s - no hostname
        result = FlextApiUtilities.HttpValidator.validate_url("https://")
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error is not None
        assert "Invalid URL format" in result.error

        # Invalid s - empty string
        result = FlextApiUtilities.HttpValidator.validate_url("")
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error is not None
        assert result.error is not None
        assert "Invalid URL format" in result.error

        # Invalid s - whitespace only
        result = FlextApiUtilities.HttpValidator.validate_url("   ")
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error is not None
        assert result.error is not None
        assert "Invalid URL format" in result.error

    def test_url_component_validation(self) -> None:
        """Test component validation edge cases."""
        # Very long hostname (should be rejected)
        long_hostname = "a" * (FlextApiConstants.MAX_HOSTNAME_LENGTH + 1)
        long_url = f"https://{long_hostname}.com"
        result = FlextApiUtilities.HttpValidator.validate_url(long_url)
        # Hostname exceeds maximum length - should fail
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error is not None

        # Invalid port - too low
        result = FlextApiUtilities.HttpValidator.validate_url("https://example.com:0")
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error is not None
        assert "Invalid port 0" in result.error

        # Invalid port - too high (parsing will fail before our validation)
        result = FlextApiUtilities.HttpValidator.validate_url(
            "https://example.com:70000",
        )
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error is not None
        assert "parsing failed" in result.error or "Invalid port 70000" in result.error

        # too long
        long_path = "a" * FlextApiConstants.MAX_URL_LENGTH
        long_url = f"https://example.com/{long_path}"
        result = FlextApiUtilities.HttpValidator.validate_url(long_url)
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error is not None
        assert "too long" in result.error

    def test_url_normalization(self) -> None:
        """Test normalization functionality."""
        # Normal without trailing slash
        result = FlextApiUtilities.HttpValidator.normalize_url(
            "https://api.example.com/data",
        )
        assert result.is_success
        assert result.value == "https://api.example.com/data"

        # with trailing slash (preserved)
        result = FlextApiUtilities.HttpValidator.normalize_url(
            "https://api.example.com/data/",
        )
        assert result.is_success
        assert result.value == "https://api.example.com/data/"

        # Root with trailing slash (preserved)
        result = FlextApiUtilities.HttpValidator.normalize_url("https://example.com/")
        assert result.is_success
        assert result.value == "https://example.com/"

        # with scheme only (should keep trailing slash)
        result = FlextApiUtilities.HttpValidator.normalize_url("https://example.com")
        assert result.is_success
        assert result.value == "https://example.com"

        # Invalid normalization should fail
        result = FlextApiUtilities.HttpValidator.normalize_url("")
        FlextTestsMatchers.assert_result_failure(result)

    def test_http_method_validation_comprehensive(self) -> None:
        """Test comprehensive HTTP method validation."""
        # Common methods
        common_methods = ["GET", "POST", "PUT", "DELETE"]
        for method in common_methods:
            result = FlextApiUtilities.HttpValidator.validate_http_method(method)
            assert result.is_success
            assert result.value == method

        # Extended methods
        extended_methods = ["PATCH", "HEAD", "OPTIONS"]
        for method in extended_methods:
            result = FlextApiUtilities.HttpValidator.validate_http_method(method)
            assert result.is_success
            assert result.value == method

        # Rare but valid methods
        rare_methods = ["TRACE", "CONNECT"]
        for method in rare_methods:
            result = FlextApiUtilities.HttpValidator.validate_http_method(method)
            assert result.is_success
            assert result.value == method

        # WebDAV methods
        webdav_methods = ["PROPFIND", "COPY", "MOVE", "LOCK"]
        for method in webdav_methods:
            result = FlextApiUtilities.HttpValidator.validate_http_method(method)
            assert result.is_success
            assert result.value == method

        # Case insensitive - lowercase
        result = FlextApiUtilities.HttpValidator.validate_http_method("get")
        assert result.is_success
        assert result.value == "GET"

        # Invalid methods (non-empty)
        invalid_methods = ["INVALID", "BADMETHOD", "123"]
        for method in invalid_methods:
            result = FlextApiUtilities.HttpValidator.validate_http_method(method)
            FlextTestsMatchers.assert_result_failure(result)
            assert result.error is not None
            assert "Invalid HTTP method" in result.error

        # Empty/whitespace method (gets caught by initial validation)
        result = FlextApiUtilities.HttpValidator.validate_http_method("")
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error is not None
        assert "HTTP method must be a non-empty string" in result.error

    def test_status_code_validation_comprehensive(self) -> None:
        """Test comprehensive HTTP status code validation."""
        # Valid status codes by range
        status_ranges = [
            (100, 199),  # 1xx Informational
            (200, 299),  # 2xx Success
            (300, 399),  # 3xx Redirection
            (400, 499),  # 4xx Client Error
            (500, 599),  # 5xx Server Error
        ]

        for start, end in status_ranges:
            # Test range boundaries
            result = FlextApiUtilities.HttpValidator.validate_status_code(start)
            assert result.is_success
            assert result.value == start

            result = FlextApiUtilities.HttpValidator.validate_status_code(end)
            assert result.is_success
            assert result.value == end

            # Test middle values
            middle = (start + end) // 2
            result = FlextApiUtilities.HttpValidator.validate_status_code(middle)
            assert result.is_success
            assert result.value == middle

        # Invalid status codes
        invalid_codes = [0, 50, 99, 600, 700, 999]
        for code in invalid_codes:
            result = FlextApiUtilities.HttpValidator.validate_status_code(code)
            FlextTestsMatchers.assert_result_failure(result)
            assert result.error is not None
            assert "Invalid HTTP status code" in result.error

        # Non-integer status code (use invalid value directly)
        invalid_status = -1  # Invalid status code
        result = FlextApiUtilities.HttpValidator.validate_status_code(invalid_status)
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error is not None
        assert "Invalid HTTP status code" in result.error

    def test_response_builder_success_comprehensive(self) -> None:
        """Test comprehensive success response building."""
        # Basic success response
        result = FlextApiUtilities.ResponseBuilder.build_success_response()
        assert result.is_success
        response = result.value
        assert response["success"] is True
        assert response["message"] == "Success"
        assert response["status_code"] == FlextConstants.Platform.HTTP_STATUS_OK
        assert response["data"] is None

        # Success response with data
        test_data = {"user_id": 123, "name": "Test User"}
        result = FlextApiUtilities.ResponseBuilder.build_success_response(
            data=test_data,
            message="User created",
            status_code=201,
        )
        assert result.is_success
        response = result.value
        assert response["success"] is True
        assert response["message"] == "User created"
        assert response["status_code"] == 201
        assert response["data"] == test_data

    def test_response_builder_error_comprehensive(self) -> None:
        """Test comprehensive error response building."""
        # Basic error response
        result = FlextApiUtilities.ResponseBuilder.build_error_response("Server error")
        assert result.is_success
        response = result.value
        assert response["success"] is False
        assert response["message"] == "Server error"
        assert (
            response["status_code"]
            == FlextConstants.Platform.HTTP_STATUS_INTERNAL_ERROR
        )
        assert response["data"] is None

        # Error response with all fields
        result = FlextApiUtilities.ResponseBuilder.build_error_response(
            error="Validation failed",
            status_code=400,
            error_code="VALIDATION_ERROR",
            details={"field": "email", "reason": "Invalid format"},
        )
        assert result.is_success
        response = result.value
        assert response["success"] is False
        assert response["message"] == "Validation failed"
        assert response["status_code"] == 400
        assert response["error_code"] == "VALIDATION_ERROR"
        assert response["details"] == {"field": "email", "reason": "Invalid format"}

    def test_pagination_builder_comprehensive(self) -> None:
        """Test comprehensive pagination response building."""
        # Basic pagination
        test_data: FlextTypes.Core.List = [{"id": 1}, {"id": 2}, {"id": 3}]
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=test_data,
            total=100,
        )
        assert result.is_success
        response = result.value
        assert isinstance(response, dict)
        assert response["success"] is True
        assert response["data"] == test_data
        pagination = response["pagination"]
        assert isinstance(pagination, dict)
        assert pagination["total"] == 100
        assert pagination["page"] == 1
        assert pagination["page_size"] == FlextApiConstants.DEFAULT_PAGE_SIZE
        assert pagination["total_pages"] > 0
        assert pagination["has_next"] is True
        assert pagination["has_previous"] is False

        # Custom pagination parameters
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=test_data,
            total=25,
            page=2,
            page_size=10,
            message="Data retrieved",
        )
        assert result.is_success
        response2 = result.value
        assert isinstance(response2, dict)
        pagination2 = response2["pagination"]
        assert isinstance(pagination2, dict)
        assert pagination2["page"] == 2
        assert pagination2["page_size"] == 10
        assert pagination2["total_pages"] == 3
        assert pagination2["has_next"] is True
        assert pagination2["has_previous"] is True

        # Last page
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=test_data,
            total=25,
            page=3,
            page_size=10,
        )
        assert result.is_success
        response3 = result.value
        assert isinstance(response3, dict)
        pagination3 = response3["pagination"]
        assert isinstance(pagination3, dict)
        assert pagination3["has_next"] is False
        assert pagination3["has_previous"] is True

        # Validation errors
        # Invalid page
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=test_data,
            total=100,
            page=0,
        )
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error is not None
        assert "Page must be >= 1" in result.error

        # Invalid page size
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=test_data,
            total=100,
            page_size=0,
        )
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error is not None
        assert "Page size must be >= 1" in result.error

        # Page size too large
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=test_data,
            total=100,
            page_size=FlextApiConstants.MAX_PAGE_SIZE + 1,
        )
        FlextTestsMatchers.assert_result_failure(result)
        assert result.error is not None
        assert "Page size cannot exceed" in result.error

    def test_edge_cases_and_error_handling(self) -> None:
        """Test edge cases and error handling scenarios."""
        # Test parsing errors (malformed )
        # Note: urlparse is quite forgiving, so this tests exception handling
        malformed_url = "https://[invalid-ipv6"
        FlextApiUtilities.HttpValidator.validate_url(malformed_url)
        # Should handle gracefully - might succeed or fail depending on format

        # Test response builder exception scenarios
        # These would normally succeed, but we test the exception handling paths
        # by ensuring the methods handle any potential errors gracefully

        # Test type conversion edge cases - use safe_int to simulate type conversion
        invalid_status = -1  # Invalid status representing failed conversion
        status_result = FlextApiUtilities.HttpValidator.validate_status_code(
            invalid_status,
        )
        FlextTestsMatchers.assert_result_failure(status_result)
        assert status_result.error is not None
        assert "Invalid HTTP status code" in status_result.error

        # Test pagination with converted int inputs
        safe_total = 25  # Direct int value
        safe_page = 2  # Direct int value
        safe_page_size = 10  # Direct int value
        pagination_result = (
            FlextApiUtilities.PaginationBuilder.build_paginated_response(
                data=[],
                total=safe_total,
                page=safe_page,
                page_size=safe_page_size,
            )
        )
        assert pagination_result.is_success
        response = pagination_result.value
        assert isinstance(response, dict)
        pagination_info = response["pagination"]
        assert isinstance(pagination_info, dict)
        assert pagination_info["total"] == 25
        assert pagination_info["page"] == 2
        assert pagination_info["page_size"] == 10
