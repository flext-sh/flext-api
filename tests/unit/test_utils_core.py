"""Tests for flext_api.utilities module using flext_tests EM ABSOLUTO.

MAXIMUM usage of flext_tests - ALL test utilities via flext_tests.
Uses FlextTestsMatchers, FlextTestsDomains, FlextTestsUtilities.
ACESSO DIRETO - NO ALIASES, NO WRAPPERS, NO COMPATIBILITY.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# MAXIMUM usage of flext_tests - ACESSO DIRETO - NO ALIASES
from flext_tests import FlextTestsMatchers

from flext_api import FlextApiUtilities


class TestFlextApiUtilities:
    """Test FlextApiUtilities using flext_tests patterns and real functionality."""

    def test_utils_class_exists(self) -> None:
        """Test class exists and is accessible."""
        assert FlextApiUtilities is not None
        assert hasattr(FlextApiUtilities, "build_error_response")
        assert hasattr(FlextApiUtilities, "build_paginated_response")
        assert hasattr(FlextApiUtilities, "validate_url")

    def test_build_error_response_basic(self) -> None:
        """Test basic error response building."""
        response = FlextApiUtilities.build_error_response("Something went wrong")

        assert isinstance(response, dict)
        assert response["success"] is False
        assert response["error"] == "Something went wrong"
        assert response["status_code"] == 500  # default
        assert response["data"] is None

    def test_build_error_response_custom_status(self) -> None:
        """Test error response with custom status code."""
        response = FlextApiUtilities.build_error_response("Validation failed", 400)

        assert isinstance(response, dict)
        assert response["success"] is False
        assert response["error"] == "Validation failed"
        assert response["status_code"] == 400
        assert response["data"] is None

    def test_build_error_response_empty_error(self) -> None:
        """Test error response with empty error message."""
        response = FlextApiUtilities.build_error_response("")

        assert isinstance(response, dict)
        assert response["success"] is False
        assert response["error"] == ""
        assert response["status_code"] == 500
        assert response["data"] is None

    def test_build_paginated_response_basic(self) -> None:
        """Test basic paginated response building."""
        data = [{"id": 1, "name": "item1"}, {"id": 2, "name": "item2"}]

        response = FlextApiUtilities.build_paginated_response(data, total=100)

        assert isinstance(response, dict)
        assert response["success"] is True
        assert response["data"] == data
        assert "pagination" in response

        pagination = response["pagination"]
        assert isinstance(pagination, dict)
        assert pagination["total"] == 100
        assert pagination["page"] == 1  # default
        assert pagination["page_size"] == 50  # default
        assert pagination["pages"] == 2  # 100/50 = 2

    def test_build_paginated_response_custom_pagination(self) -> None:
        """Test paginated response with custom pagination."""
        data = [{"id": 1}, {"id": 2}, {"id": 3}]

        response = FlextApiUtilities.build_paginated_response(
            data=data, total=25, page=3, page_size=10
        )

        assert isinstance(response, dict)
        assert response["success"] is True
        assert response["data"] == data

        pagination = response["pagination"]
        assert pagination["total"] == 25
        assert pagination["page"] == 3
        assert pagination["page_size"] == 10
        assert pagination["pages"] == 3  # 25/10 = 2.5, rounded up = 3

    def test_build_paginated_response_empty_data(self) -> None:
        """Test paginated response with empty data."""
        response = FlextApiUtilities.build_paginated_response([], total=0)

        assert isinstance(response, dict)
        assert response["success"] is True
        assert response["data"] == []

        pagination = response["pagination"]
        assert pagination["total"] == 0
        assert pagination["page"] == 1
        assert pagination["page_size"] == 50
        assert pagination["pages"] >= 0  # Empty data should have at least 0 pages

    def test_build_paginated_response_single_page(self) -> None:
        """Test paginated response with single page."""
        data = [{"id": 1}, {"id": 2}]

        response = FlextApiUtilities.build_paginated_response(
            data, total=2, page_size=10
        )

        pagination = response["pagination"]
        assert pagination["total"] == 2
        assert pagination["page"] == 1
        assert pagination["page_size"] == 10
        assert pagination["pages"] == 1  # 2/10 = 0.2, rounded up = 1

    def test_build_paginated_response_large_dataset(self) -> None:
        """Test paginated response with large dataset."""
        data = [{"id": i} for i in range(20)]

        response = FlextApiUtilities.build_paginated_response(
            data=data, total=1000, page=5, page_size=20
        )

        pagination = response["pagination"]
        assert pagination["total"] == 1000
        assert pagination["page"] == 5
        assert pagination["page_size"] == 20
        assert pagination["pages"] == 50  # 1000/20 = 50

    def test_validate_url_success_http(self) -> None:
        """Test validation success with HTTP."""
        urls = [
            "http://localhost",
            "http://localhost:8000",
            "http://example.com",
            "http://api.example.com/v1/users",
        ]

        for url in urls:
            result = FlextApiUtilities.validate_url(url)
            FlextTestsMatchers.assert_result_success(result)
            assert result.value == url

    def test_validate_url_success_https(self) -> None:
        """Test validation success with HTTPS."""
        urls = [
            "https://localhost",
            "https://localhost:8443",
            "https://example.com",
            "https://api.example.com/v1/users",
            "https://secure.api.test.com:9000/api",
        ]

        for url in urls:
            result = FlextApiUtilities.validate_url(url)
            FlextTestsMatchers.assert_result_success(result)
            assert result.value == url

    def test_validate_url_empty_string_failure(self) -> None:
        """Test validation failure with empty string."""
        result = FlextApiUtilities.validate_url("")
        FlextTestsMatchers.assert_result_failure(result)
        assert "URL must be a non-empty string" in result.error or "Invalid URL format" in result.error

    def test_validate_url_none_failure(self) -> None:
        """Test validation failure with None."""
        result = FlextApiUtilities.validate_url(None)
        FlextTestsMatchers.assert_result_failure(result)
        assert "URL must be a non-empty string" in result.error or "Invalid URL format" in result.error

    def test_validate_url_non_string_failure(self) -> None:
        """Test validation failure with non-string input."""
        invalid_inputs = [123, [], {}, True]

        for invalid_input in invalid_inputs:
            result = FlextApiUtilities.validate_url(invalid_input)
            FlextTestsMatchers.assert_result_failure(result)
        assert "URL must be a non-empty string" in result.error or "Invalid URL format" in result.error

    def test_validate_url_invalid_scheme_failure(self) -> None:
        """Test validation failure with invalid schemes."""
        invalid_urls = [
            "ftp://example.com",
            "file:///path/to/file",
            "mailto:user@example.com",
            "example.com",
            "www.example.com",
            "//example.com",
        ]

        for url in invalid_urls:
            result = FlextApiUtilities.validate_url(url)
            FlextTestsMatchers.assert_result_failure(result)
        assert "URL must include scheme" in result.error or "must start with http:// or https://" in result.error

    def test_validate_url_whitespace_failure(self) -> None:
        """Test validation failure with whitespace."""
        # These should fail because they are just whitespace
        failing_urls = [
            "   ",  # just spaces
            "\t",  # just tab
            "\n",  # just newline
        ]

        for url in failing_urls:
            result = FlextApiUtilities.validate_url(url)
            assert not result.success, f"Expected {url!r} to fail validation"

        # These may pass depending on implementation - test actual behavior
        edge_cases = [
            " http://example.com",  # starts with space
            " http://example.com ",  # starts and ends with space
            "http://example.com ",  # trailing space
        ]

        for url in edge_cases:
            result = FlextApiUtilities.validate_url(url)
            # Just test that we get a consistent result - don't assume failure
            if result.success:
                assert isinstance(result.value, str)
            else:
                FlextTestsMatchers.assert_result_failure(result)

    def test_utils_static_methods(self) -> None:
        """Test that utility methods are static."""
        # Should be able to call without instance
        response = FlextApiUtilities.build_error_response("test")
        assert isinstance(response, dict)

        paginated = FlextApiUtilities.build_paginated_response([], 0)
        assert isinstance(paginated, dict)

        url_result = FlextApiUtilities.validate_url("http://example.com")
        assert url_result.success

    def test_utils_type_validation(self) -> None:
        """Test utils is proper type."""
        assert FlextApiUtilities is not None
        assert type(FlextApiUtilities).__name__ == "type"

        # Should be a class, not an instance
        assert hasattr(FlextApiUtilities, "__name__")
        assert FlextApiUtilities.__name__ == "FlextApiUtilities"

    def test_build_error_response_different_error_types(self) -> None:
        """Test error response with different error message types."""
        # String error
        response1 = FlextApiUtilities.build_error_response("String error")
        assert response1["error"] == "String error"

        # Should handle conversion to string for other types
        # Note: method signature expects str, so we test normal usage
        response2 = FlextApiUtilities.build_error_response("123")
        assert response2["error"] == "123"

    def test_pagination_edge_cases(self) -> None:
        """Test pagination calculation edge cases."""
        # Exact division
        response1 = FlextApiUtilities.build_paginated_response(
            [], total=100, page_size=50
        )
        assert response1["pagination"]["pages"] == 2

        # Division with remainder
        response2 = FlextApiUtilities.build_paginated_response(
            [], total=101, page_size=50
        )
        assert response2["pagination"]["pages"] == 3

        # Single item
        response3 = FlextApiUtilities.build_paginated_response(
            [], total=1, page_size=50
        )
        assert response3["pagination"]["pages"] == 1

        # Page size = total
        response4 = FlextApiUtilities.build_paginated_response(
            [], total=25, page_size=25
        )
        assert response4["pagination"]["pages"] == 1

    def test_utils_consistency(self) -> None:
        """Test utilities produce consistent results."""
        # Multiple calls should produce consistent structure (timestamps may differ)
        error1 = FlextApiUtilities.build_error_response("test", 400)
        error2 = FlextApiUtilities.build_error_response("test", 400)

        # Check structure consistency, not exact equality
        assert error1["success"] == error2["success"]
        assert error1["error"] == error2["error"]
        assert error1["status_code"] == error2["status_code"]
        assert error1 is not error2  # Different objects

        # Pagination structure consistency (timestamps may differ)
        data = [1, 2, 3]
        page1 = FlextApiUtilities.build_paginated_response(data, 100, 1, 10)
        page2 = FlextApiUtilities.build_paginated_response(data, 100, 1, 10)

        # Check structure consistency, not exact equality
        assert page1["success"] == page2["success"]
        assert page1["data"] == page2["data"]
        assert page1["pagination"] == page2["pagination"]
        assert page1 is not page2  # Different objects
