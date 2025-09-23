"""Focused utilities tests for maximum coverage improvement.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api import FlextApiUtilities


class TestFlextApiUtilitiesFocused:
    """Focused tests to improve utilities.py coverage from 27% to 80%+."""

    def test_response_builder_build_error_response(self) -> None:
        """Test ResponseBuilder.build_error_response with all parameters."""
        # Test with all parameters
        result = FlextApiUtilities.ResponseBuilder.build_error_response(
            message="Custom error message",
            status_code=400,
            data={"field": "value"},
            error="Validation error",
            error_code="VALIDATION_ERROR",
            details={"field": "email", "reason": "invalid format"},
        )

        assert result.is_success
        response = result.value
        assert isinstance(response, dict)
        assert response["success"] is False
        assert response["message"] == "Custom error message"
        assert response["status_code"] == 400
        assert response["data"] == {"field": "value"}
        assert response["error"] == "Validation error"
        assert response["error_code"] == "VALIDATION_ERROR"
        assert response["details"] == {"field": "email", "reason": "invalid format"}

    def test_response_builder_build_error_response_with_error_fallback(self) -> None:
        """Test error response when message is None but error is provided."""
        result = FlextApiUtilities.ResponseBuilder.build_error_response(
            message=None,
            error="Fallback error message",
        )

        assert result.is_success
        response = result.value
        assert isinstance(response, dict)
        assert response["message"] == "Fallback error message"

    def test_response_builder_build_error_response_default_fallback(self) -> None:
        """Test error response with no message and no error - uses default."""
        result = FlextApiUtilities.ResponseBuilder.build_error_response()

        assert result.is_success
        response = result.value
        assert isinstance(response, dict)
        assert response["message"] == "Unknown error"

    def test_response_builder_build_success_response(self) -> None:
        """Test ResponseBuilder.build_success_response with custom parameters."""
        test_data = {"user_id": 123, "name": "Test User"}
        result = FlextApiUtilities.ResponseBuilder.build_success_response(
            data=test_data,
            message="User created successfully",
            status_code=201,
        )

        assert result.is_success
        response = result.value
        assert isinstance(response, dict)
        assert response["success"] is True
        assert response["message"] == "User created successfully"
        assert response["status_code"] == 201
        assert response["data"] == test_data
        assert "timestamp" in response
        assert "request_id" in response

    def test_pagination_builder_build_paginated_response_basic(self) -> None:
        """Test PaginationBuilder basic functionality."""
        test_data: list[object] = [{"id": 1}, {"id": 2}, {"id": 3}]
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=test_data,
            page=1,
            page_size=20,
            total=100,
        )

        assert result.is_success
        response = result.value
        assert isinstance(response, dict)
        assert response["success"] is True
        assert response["data"] == test_data

        pagination = response["pagination"]
        assert isinstance(pagination, dict)
        assert pagination["page"] == 1
        assert pagination["page_size"] == 20
        assert pagination["total"] == 100
        assert pagination["total_pages"] == 5  # 100 / 20 = 5
        assert pagination["has_next"] is True
        assert pagination["has_previous"] is False

    def test_pagination_builder_with_message(self) -> None:
        """Test PaginationBuilder with custom message."""
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=[],
            message="Custom pagination message",
        )

        assert result.is_success
        response = result.value
        assert isinstance(response, dict)
        assert response["message"] == "Custom pagination message"

    def test_pagination_builder_validation_errors(self) -> None:
        """Test PaginationBuilder validation error paths."""
        # Page must be >= 1
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=[],
            page=0,
        )
        assert not result.is_success
        assert result.error is not None
        assert "Page must be >= 1" in result.error

        # Page size must be >= 1
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=[],
            page_size=0,
        )
        assert not result.is_success
        assert result.error is not None
        assert "Page size must be >= 1" in result.error

        # Page size cannot exceed max
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=[],
            page_size=2000,  # Assuming MAX_PAGE_SIZE is 1000
        )
        assert not result.is_success
        assert result.error is not None
        assert "Page size cannot exceed" in result.error

    def test_pagination_builder_none_data_handling(self) -> None:
        """Test PaginationBuilder with None data."""
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=None,
            total=50,
        )

        assert result.is_success
        response = result.value
        assert isinstance(response, dict)
        assert response["data"] == []  # None converted to empty list
        assert isinstance(response["pagination"], dict)
        assert response["pagination"]["total"] == 50

    def test_pagination_builder_no_total_uses_data_length(self) -> None:
        """Test PaginationBuilder uses data length when total is None."""
        test_data: list[object] = [1, 2, 3, 4, 5]
        result = FlextApiUtilities.PaginationBuilder.build_paginated_response(
            data=test_data,
            total=None,
        )

        assert result.is_success
        response = result.value
        assert isinstance(response, dict)
        assert isinstance(response["pagination"], dict)
        assert response["pagination"]["total"] == 5  # Length of test_data

    def test_http_validator_validate_http_method(self) -> None:
        """Test HttpValidator.validate_http_method."""
        # Valid methods
        valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        for method in valid_methods:
            result = FlextApiUtilities.HttpValidator.validate_http_method(method)
            assert result.is_success
            assert result.value == method

        # Case insensitive
        result = FlextApiUtilities.HttpValidator.validate_http_method("get")
        assert result.is_success
        assert result.value == "GET"

    def test_http_validator_validate_http_method_failures(self) -> None:
        """Test HttpValidator.validate_http_method failure cases."""
        # Empty method
        result = FlextApiUtilities.HttpValidator.validate_http_method("")
        assert not result.is_success
        assert result.error is not None
        assert "HTTP method must be a non-empty string" in result.error

        # None method
        none_method: str | None = None
        result = FlextApiUtilities.HttpValidator.validate_http_method(none_method)
        assert not result.is_success
        assert result.error is not None
        assert "HTTP method must be a non-empty string" in result.error

        # Invalid method
        result = FlextApiUtilities.HttpValidator.validate_http_method("INVALID")
        assert not result.is_success
        assert result.error is not None
        assert "Invalid HTTP method" in result.error

    def test_http_validator_validate_status_code(self) -> None:
        """Test HttpValidator.validate_status_code."""
        # Valid status codes
        valid_codes = [200, 404, 500, 100, 599]
        for code in valid_codes:
            result = FlextApiUtilities.HttpValidator.validate_status_code(code)
            assert result.is_success
            assert result.value == code

        # String status code
        result = FlextApiUtilities.HttpValidator.validate_status_code("200")
        assert result.is_success
        assert result.value == 200

    def test_http_validator_validate_status_code_failures(self) -> None:
        """Test HttpValidator.validate_status_code failure cases."""
        # Out of range
        invalid_codes = [99, 600, 700]
        for code in invalid_codes:
            result = FlextApiUtilities.HttpValidator.validate_status_code(code)
            assert not result.is_success
            assert result.error is not None
            assert "Invalid HTTP status code" in result.error

        # Invalid string
        result = FlextApiUtilities.HttpValidator.validate_status_code("invalid")
        assert not result.is_success
        assert result.error is not None
        assert "Invalid status code format" in result.error

    def test_http_validator_normalize_url(self) -> None:
        """Test HttpValidator.normalize_url."""
        # Normal URL without trailing slash
        result = FlextApiUtilities.HttpValidator.normalize_url(
            "https://api.example.com/data",
        )
        assert result.is_success
        assert result.value == "https://api.example.com/data"

        # URL with trailing slash (preserved in normalization)
        result = FlextApiUtilities.HttpValidator.normalize_url(
            "https://api.example.com/data/",
        )
        assert result.is_success
        assert result.value == "https://api.example.com/data/"

        # Root URL (preserve trailing slash)
        result = FlextApiUtilities.HttpValidator.normalize_url("https://example.com/")
        assert result.is_success
        assert result.value == "https://example.com/"

    def test_validate_url_static_method(self) -> None:
        """Test static validate_url method."""
        result = FlextApiUtilities.validate_url("https://api.example.com")
        assert result.is_success

        result = FlextApiUtilities.validate_url("invalid-url")
        assert not result.is_success

    def test_validate_config_static_method(self) -> None:
        """Test static validate_config method."""
        # Test with dictionary config
        config = {"base_url": "https://api.example.com", "timeout": 30}
        result = FlextApiUtilities.validate_config(config)
        assert result.is_success
        assert isinstance(result.value, dict)

        # Test with object that has model_dump
        class MockConfig:
            def model_dump(self) -> dict[str, object]:
                return {"base_url": "https://test.com", "timeout": 60}

        mock_config = MockConfig()
        result = FlextApiUtilities.validate_config(mock_config)
        assert result.is_success
        assert result.value["base_url"] == "https://test.com"
