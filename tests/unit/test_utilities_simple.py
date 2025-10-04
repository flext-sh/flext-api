"""Simple tests for flext-api utilities module.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import cast

from flext_core import FlextTypes

from flext_api.utilities import FlextApiUtilities


class TestFlextApiUtilitiesSimple:
    """Simple tests for FlextApiUtilities class."""

    def test_utilities_inheritance(self) -> None:
        """Test that FlextApiUtilities inherits from FlextUtilities."""
        utilities = FlextApiUtilities()
        assert utilities is not None
        assert hasattr(utilities, "SECONDS_PER_MINUTE")
        assert hasattr(utilities, "SECONDS_PER_HOUR")

    def test_constants_values(self) -> None:
        """Test that constants have correct values."""
        assert FlextApiUtilities.SECONDS_PER_MINUTE == 60
        assert FlextApiUtilities.SECONDS_PER_HOUR == 3600


class TestResponseBuilderSimple:
    """Simple tests for ResponseBuilder class."""

    def test_build_error_response_default(self) -> None:
        """Test building error response with default parameters."""
        result = FlextApiUtilities.ResponseBuilder.build_error_response()

        assert result.is_success
        response = result.data
        assert response["success"] is False
        assert response["message"] == "Unknown error"
        assert response["status_code"] == 500
        assert response["data"] is None

    def test_build_error_response_custom(self) -> None:
        """Test building error response with custom parameters."""
        result = FlextApiUtilities.ResponseBuilder.build_error_response(
            message="Custom error",
            status_code=400,
            data={"key": "value"},
            error="Detailed error",
            error_code="ERR_001",
            details={"field": "value"},
        )

        assert result.is_success
        response = result.data
        assert response["success"] is False
        assert response["message"] == "Custom error"
        assert response["status_code"] == 400
        assert response["data"] == {"key": "value"}
        assert response["error"] == "Detailed error"
        assert response["error_code"] == "ERR_001"
        assert response["details"] == {"field": "value"}

    def test_build_success_response_default(self) -> None:
        """Test building success response with default parameters."""
        result = FlextApiUtilities.ResponseBuilder.build_success_response()

        assert result.is_success
        response = result.data
        assert response["success"] is True
        assert response["message"] == "Success"
        assert response["status_code"] == 200
        assert response["data"] is None
        assert "timestamp" in response
        assert "request_id" in response

    def test_build_success_response_custom(self) -> None:
        """Test building success response with custom parameters."""
        result = FlextApiUtilities.ResponseBuilder.build_success_response(
            data={"key": "value"}, message="Custom success", status_code=201
        )

        assert result.is_success
        response = result.data
        assert response["success"] is True
        assert response["message"] == "Custom success"
        assert response["status_code"] == 201
        assert response["data"] == {"key": "value"}
        assert "timestamp" in response
        assert "request_id" in response


class TestPaginationBuilderSimple:
    """Simple tests for PaginationBuilder class."""

    def test_build_paginated_response_default(self) -> None:
        """Test building paginated response with default parameters."""
        data = ["item1", "item2", "item3"]
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            cast("FlextTypes.List", data)
        )

        assert result.is_success
        response = cast("dict", result.data)
        assert response["success"] is True
        assert response["data"] == data
        assert "pagination" in response
        pagination = cast("dict", response["pagination"])
        assert pagination["page"] == 1
        assert pagination["page_size"] == 20
        assert pagination["total"] == 3
        assert pagination["total_pages"] == 1
        assert pagination["has_next"] is False
        assert pagination["has_previous"] is False

    def test_build_paginated_response_custom(self) -> None:
        """Test building paginated response with custom parameters."""
        data = list(range(50))  # 50 items
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            cast("FlextTypes.List", data),
            page=2,
            page_size=10,
            total=50,
            message="Custom message",
        )

        assert result.is_success
        response = cast("dict", result.data)
        assert response["success"] is True
        assert response["data"] == data
        assert response["message"] == "Custom message"
        assert "pagination" in response
        pagination = cast("dict", response["pagination"])
        assert pagination["page"] == 2
        assert pagination["page_size"] == 10
        assert pagination["total"] == 50
        assert pagination["total_pages"] == 5
        assert pagination["has_next"] is True
        assert pagination["has_previous"] is True

    def test_build_paginated_response_invalid_page(self) -> None:
        """Test building paginated response with invalid page."""
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            ["item1", "item2"], page=0
        )

        assert result.is_failure
        assert result.error is not None and "Page must be >= 1" in result.error

    def test_build_paginated_response_invalid_page_size(self) -> None:
        """Test building paginated response with invalid page size."""
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            ["item1", "item2"], page_size=0
        )

        assert result.is_failure
        assert result.error is not None and "Page size must be >= 1" in result.error


class TestHttpValidatorSimple:
    """Simple tests for HttpValidator class."""

    def test_validate_url_valid(self) -> None:
        """Test validating valid URLs."""
        valid_urls = [
            "https://example.com",
            "http://localhost:8080/api",
            "https://api.example.com/v1/users",
            "https://internal.invalid/REDACTED",
        ]

        for url in valid_urls:
            result = FlextApiUtilities.HttpValidator.validate_url(url)
            assert result.is_success, f"URL {url} should be valid"

    def test_validate_url_invalid_format(self) -> None:
        """Test validating invalid URL formats."""
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",  # Wrong scheme
            "example.com",  # No scheme
            "",
            "   ",
        ]

        for url in invalid_urls:
            result = FlextApiUtilities.HttpValidator.validate_url(url)
            assert result.is_failure, f"URL {url} should be invalid"

    def test_validate_url_invalid_port(self) -> None:
        """Test validating URLs with invalid ports."""
        invalid_urls = [
            "http://example.com:0",  # Port 0
            "http://example.com:70000",  # Port too high
            "https://api.com:0/endpoint",  # Port 0 with path
        ]

        for url in invalid_urls:
            result = FlextApiUtilities.HttpValidator.validate_url(url)
            assert result.is_failure, f"URL {url} should be invalid"

    def test_validate_http_method_valid(self) -> None:
        """Test validating valid HTTP methods."""
        valid_methods = [
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "PATCH",
            "HEAD",
            "OPTIONS",
            "TRACE",
            "CONNECT",
            "PROPFIND",
            "COPY",
            "MOVE",
            "LOCK",
        ]

        for method in valid_methods:
            result = FlextApiUtilities.HttpValidator.validate_http_method(method)
            assert result.is_success, f"Method {method} should be valid"
            assert result.data == method.upper()

    def test_validate_http_method_case_insensitive(self) -> None:
        """Test that HTTP method validation is case insensitive."""
        result = FlextApiUtilities.HttpValidator.validate_http_method("get")
        assert result.is_success
        assert result.data == "GET"

        result = FlextApiUtilities.HttpValidator.validate_http_method("Post")
        assert result.is_success
        assert result.data == "POST"

    def test_validate_http_method_invalid(self) -> None:
        """Test validating invalid HTTP methods."""
        invalid_methods = ["INVALID", "", None, "GETTY", "POSTMAN"]

        for method in invalid_methods:
            result = FlextApiUtilities.HttpValidator.validate_http_method(method)
            assert result.is_failure, f"Method {method} should be invalid"

    def test_validate_status_code_valid(self) -> None:
        """Test validating valid HTTP status codes."""
        valid_codes = [200, 201, 404, 500, 301, 302]

        for code in valid_codes:
            result = FlextApiUtilities.HttpValidator.validate_status_code(code)
            assert result.is_success, f"Status code {code} should be valid"
            assert result.data == code

    def test_validate_status_code_string(self) -> None:
        """Test validating status codes as strings."""
        result = FlextApiUtilities.HttpValidator.validate_status_code("200")
        assert result.is_success
        assert result.data == 200

        result = FlextApiUtilities.HttpValidator.validate_status_code("404")
        assert result.is_success
        assert result.data == 404

    def test_validate_status_code_invalid(self) -> None:
        """Test validating invalid HTTP status codes."""
        invalid_codes = [50, 1000, "invalid", "50", "1000"]

        for code in invalid_codes:
            result = FlextApiUtilities.HttpValidator.validate_status_code(code)
            assert result.is_failure, f"Status code {code} should be invalid"
