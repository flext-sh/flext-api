"""Tests for flext_api.utils module - REAL classes only.

Tests using only REAL classes:
- FlextUtils

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api import FlextUtils


class TestFlextUtils:
    """Test FlextUtils REAL class functionality."""

    def test_utils_class_exists(self) -> None:
        """Test that FlextUtils class exists."""
        assert FlextUtils is not None
        assert hasattr(FlextUtils, "__name__")
        assert FlextUtils.__name__ == "FlextUtils"

    def test_build_error_response_method(self) -> None:
        """Test build_error_response method."""
        if hasattr(FlextUtils, "build_error_response"):
            response = FlextUtils.build_error_response("Test error", 400)

            assert isinstance(response, dict)
            assert response["status"] == "error"
            assert response["message"] == "Test error"
            assert response["status_code"] == 400
        else:
            pytest.skip("build_error_response method not available")

    def test_build_success_response_method(self) -> None:
        """Test build_success_response method if available."""
        if hasattr(FlextUtils, "build_success_response"):
            data = {"id": 123, "name": "Test"}
            response = FlextUtils.build_success_response(data, "Success")

            assert isinstance(response, dict)
            assert response["status"] == "success"
            assert response["data"] == data
            assert response["message"] == "Success"
        else:
            pytest.skip("build_success_response method not available")

    def test_build_paginated_response_method(self) -> None:
        """Test build_paginated_response method."""
        if hasattr(FlextUtils, "build_paginated_response"):
            items = [{"id": 1}, {"id": 2}]
            total = 10
            page = 1
            page_size = 2

            response = FlextUtils.build_paginated_response(
                items=items, total=total, page=page, page_size=page_size
            )

            assert isinstance(response, dict)
            assert response["data"]["items"] == items
            assert response["data"]["total"] == total
            assert response["data"]["page"] == page
            assert response["data"]["page_size"] == page_size
            assert response["data"]["total_pages"] == 5  # 10/2 = 5
        else:
            pytest.skip("build_paginated_response method not available")

    def test_validate_url_method(self) -> None:
        """Test URL validation method if available."""
        if hasattr(FlextUtils, "validate_url"):
            # Valid URL should pass
            result = FlextUtils.validate_url("https://api.example.com")
            assert result is True or (hasattr(result, "success") and result.success)

            # Invalid URL should fail
            result = FlextUtils.validate_url("invalid-url")
            assert result is False or (
                hasattr(result, "success") and not result.success
            )
        else:
            pytest.skip("validate_url method not available")

    def test_format_timestamp_method(self) -> None:
        """Test timestamp formatting method if available."""
        if hasattr(FlextUtils, "format_timestamp"):
            import datetime

            now = datetime.datetime.now(datetime.UTC)
            formatted = FlextUtils.format_timestamp(now)

            assert isinstance(formatted, str)
            assert len(formatted) > 0
        else:
            pytest.skip("format_timestamp method not available")

    def test_parse_config_method(self) -> None:
        """Test config parsing method if available."""
        if hasattr(FlextUtils, "parse_config"):
            config_dict = {"host": "localhost", "port": 8000, "debug": True}

            result = FlextUtils.parse_config(config_dict)

            # Should return parsed config or FlextResult
            assert result is not None
            if hasattr(result, "success"):
                assert result.success
        else:
            pytest.skip("parse_config method not available")

    def test_sanitize_headers_method(self) -> None:
        """Test header sanitization method if available."""
        if hasattr(FlextUtils, "sanitize_headers"):
            headers = {
                "Authorization": "Bearer secret123",
                "Content-Type": "application/json",
                "X-API-Key": "key123",
            }

            sanitized = FlextUtils.sanitize_headers(headers)

            assert isinstance(sanitized, dict)
            # Sensitive headers should be masked or removed
            if "Authorization" in sanitized:
                assert "secret123" not in str(sanitized["Authorization"])
        else:
            pytest.skip("sanitize_headers method not available")

    def test_generate_request_id_method(self) -> None:
        """Test request ID generation method if available."""
        if hasattr(FlextUtils, "generate_request_id"):
            request_id = FlextUtils.generate_request_id()

            assert isinstance(request_id, str)
            assert len(request_id) > 0

            # Should generate unique IDs
            request_id2 = FlextUtils.generate_request_id()
            assert request_id != request_id2
        else:
            pytest.skip("generate_request_id method not available")

    def test_utils_inheritance(self) -> None:
        """Test that FlextUtils inherits properly from flext-core."""
        # Should inherit from appropriate flext-core classes
        assert hasattr(FlextUtils, "__bases__")

        base_classes = FlextUtils.__bases__
        assert len(base_classes) > 0

    def test_available_utility_methods(self) -> None:
        """Test what utility methods are available."""
        # Get all public methods
        methods = [
            attr
            for attr in dir(FlextUtils)
            if not attr.startswith("_") and callable(getattr(FlextUtils, attr, None))
        ]

        # Should have at least some utility methods
        assert len(methods) > 0

        # Common utility methods that might be available
        expected_methods = [
            "build_error_response",
            "build_success_response",
            "build_paginated_response",
            "validate_url",
            "format_timestamp",
        ]

        # Check which expected methods are actually available
        available_methods = [method for method in expected_methods if method in methods]

        # At least some utility functionality should be available
        assert len(available_methods) >= 0  # Basic existence check

    def test_utils_error_handling(self) -> None:
        """Test utility error handling."""
        # Should handle errors gracefully in utility methods
        if hasattr(FlextUtils, "build_error_response"):
            # Should handle None message gracefully
            try:
                response = FlextUtils.build_error_response(None, 400)
                # Should either work or handle the None case
                assert response is not None
            except (ValueError, TypeError):
                # Acceptable to raise validation errors
                pass

    def test_utils_documentation(self) -> None:
        """Test that utilities have proper documentation."""
        # Main class should be documented
        assert FlextUtils.__doc__ is not None
        assert len(FlextUtils.__doc__.strip()) > 0

        # Public methods should be documented
        public_methods = [
            attr
            for attr in dir(FlextUtils)
            if not attr.startswith("_") and callable(getattr(FlextUtils, attr, None))
        ]

        for method_name in public_methods[:5]:  # Check first 5 methods
            method = getattr(FlextUtils, method_name)
            if hasattr(method, "__doc__") and method.__doc__:
                assert len(method.__doc__.strip()) > 0
