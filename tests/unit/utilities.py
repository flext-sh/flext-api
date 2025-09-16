"""FLEXT API Utilities Tests - Testing ONLY methods that actually exist.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.utilities import FlextApiUtilities


class TestFlextApiUtilitiesReal:
    """Test FlextApiUtilities using ONLY methods that actually exist."""

    def test_response_builder_error(self) -> None:
        """Test ResponseBuilder error response."""
        result = FlextApiUtilities.ResponseBuilder.build_error_response(
            message="Test error", status_code=400
        )

        assert result.is_success
        response = result.unwrap()
        assert response["success"] is False
        assert response["message"] == "Test error"
        assert response["status_code"] == 400

    def test_response_builder_success(self) -> None:
        """Test ResponseBuilder success response."""
        result = FlextApiUtilities.ResponseBuilder.build_success_response(
            data={"test": "data"}, message="Success", status_code=200
        )

        assert result.is_success
        response = result.unwrap()
        assert response["success"] is True
        assert response["message"] == "Success"
        assert response["status_code"] == 200
        assert response["data"] == {"test": "data"}

    def test_pagination_builder(self) -> None:
        """Test PaginationBuilder functionality."""
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=[1, 2, 3], page=1, page_size=10, total=3
        )

        assert result.is_success
        response = result.unwrap()
        assert response["success"] is True
        assert response["data"] == [1, 2, 3]
        pagination = response["pagination"]
        assert pagination["page"] == 1
        assert pagination["total"] == 3

    def test_pagination_builder_invalid_page(self) -> None:
        """Test PaginationBuilder with invalid page."""
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=[1, 2, 3], page=0, page_size=10
        )

        assert result.is_failure
        assert result.error is not None
        assert "Page must be >= 1" in result.error

    def test_pagination_builder_invalid_page_size(self) -> None:
        """Test PaginationBuilder with invalid page size."""
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=[1, 2, 3], page=1, page_size=0
        )

        assert result.is_failure
        assert result.error is not None
        assert "Page size must be >= 1" in result.error

    def test_http_validator_url_valid(self) -> None:
        """Test HttpValidator URL validation with valid URL."""
        result = FlextApiUtilities.HttpValidator.validate_url("https://example.com")
        assert result.is_success
        assert result.unwrap() == "https://example.com"

    def test_http_validator_url_invalid(self) -> None:
        """Test HttpValidator URL validation with invalid URL."""
        result = FlextApiUtilities.HttpValidator.validate_url("not-a-url")
        assert result.is_failure

    def test_http_validator_url_with_port(self) -> None:
        """Test HttpValidator URL validation with port."""
        result = FlextApiUtilities.HttpValidator.validate_url(
            "https://example.com:8080"
        )
        assert result.is_success

    def test_http_validator_url_invalid_port(self) -> None:
        """Test HttpValidator URL validation with invalid port."""
        result = FlextApiUtilities.HttpValidator.validate_url("https://example.com:0")
        assert result.is_failure
        assert result.error is not None
        assert "Invalid port 0" in result.error

    def test_http_validator_method_valid(self) -> None:
        """Test HttpValidator HTTP method validation with valid method."""
        result = FlextApiUtilities.HttpValidator.validate_http_method("GET")
        assert result.is_success
        assert result.unwrap() == "GET"

    def test_http_validator_method_invalid(self) -> None:
        """Test HttpValidator HTTP method validation with invalid method."""
        result = FlextApiUtilities.HttpValidator.validate_http_method("INVALID")
        assert result.is_failure

    def test_http_validator_method_case_insensitive(self) -> None:
        """Test HttpValidator HTTP method validation case insensitive."""
        result = FlextApiUtilities.HttpValidator.validate_http_method("post")
        assert result.is_success
        assert result.unwrap() == "POST"

    def test_http_validator_status_code_valid(self) -> None:
        """Test HttpValidator status code validation with valid code."""
        result = FlextApiUtilities.HttpValidator.validate_status_code(200)
        assert result.is_success
        assert result.unwrap() == 200

    def test_http_validator_status_code_string(self) -> None:
        """Test HttpValidator status code validation with string."""
        result = FlextApiUtilities.HttpValidator.validate_status_code("404")
        assert result.is_success
        assert result.unwrap() == 404

    def test_http_validator_status_code_invalid(self) -> None:
        """Test HttpValidator status code validation with invalid code."""
        result = FlextApiUtilities.HttpValidator.validate_status_code(9999)
        assert result.is_failure

    def test_http_validator_normalize_url(self) -> None:
        """Test HttpValidator URL normalization."""
        result = FlextApiUtilities.HttpValidator.normalize_url("https://example.com/")
        assert result.is_success
        assert result.unwrap() == "https://example.com"

    def test_http_validator_normalize_url_empty(self) -> None:
        """Test HttpValidator URL normalization with empty URL."""
        result = FlextApiUtilities.HttpValidator.normalize_url("")
        assert result.is_failure
        assert result.error is not None
        assert "URL cannot be empty" in result.error
