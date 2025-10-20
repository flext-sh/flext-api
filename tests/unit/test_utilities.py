"""FLEXT API Utilities Tests - Testing ONLY methods that actually exist.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

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
        assert response["success"] is False
        assert response["error"]["message"] == "Test error"
        assert response["error"]["status_code"] == 400

    def test_response_builder_success(self) -> None:
        """Test ResponseBuilder success response - returns FlextResult."""
        result = FlextApiUtilities.ResponseBuilder.build_success_response(
            data={"test": "data"},
            message="Success",
            status_code=200,
        )

        # API returns FlextResult[dict]
        assert result.is_success
        response = result.unwrap()
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
        response_obj = result.unwrap()
        assert isinstance(response_obj, dict)
        response: dict[str, object] = response_obj
        assert response["success"] is True
        assert response["data"] == [1, 2, 3]
        pagination_obj = response["pagination"]
        assert isinstance(pagination_obj, dict)
        pagination: dict[str, object] = pagination_obj
        assert pagination["page"] == 1
        assert pagination["total"] == 3

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
        assert result.unwrap() == "https://example.com"

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
            "https://example.com:0"
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
            "https://example.com/"
        )
        assert normalized.startswith("https://")
        assert "example.com" in normalized

    def test_http_validator_normalize_url_empty(self) -> None:
        """Test FlextWebValidator URL normalization with empty URL."""
        # API returns empty string for empty input
        normalized = FlextApiUtilities.FlextWebValidator.normalize_url("")
        assert not normalized
