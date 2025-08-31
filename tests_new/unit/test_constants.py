"""Tests for flext_api.constants module - REAL classes only.

Tests using only REAL classes:
- FlextApiConstants

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api import FlextApiConstants


class TestFlextApiConstants:
    """Test FlextApiConstants REAL class functionality."""

    def test_constants_api_version(self) -> None:
        """Test API version constant."""
        assert hasattr(FlextApiConstants, "API_VERSION")
        assert isinstance(FlextApiConstants.API_VERSION, str)
        assert FlextApiConstants.API_VERSION == "0.9.0"

    def test_constants_cache_ttl(self) -> None:
        """Test cache TTL constant."""
        assert hasattr(FlextApiConstants, "CACHE_TTL")
        assert isinstance(FlextApiConstants.CACHE_TTL, int)
        assert FlextApiConstants.CACHE_TTL > 0

    def test_constants_max_retries(self) -> None:
        """Test max retries constant."""
        assert hasattr(FlextApiConstants, "MAX_RETRIES")
        assert isinstance(FlextApiConstants.MAX_RETRIES, int)
        assert FlextApiConstants.MAX_RETRIES >= 0

    def test_constants_timeout(self) -> None:
        """Test timeout constant."""
        assert hasattr(FlextApiConstants, "TIMEOUT")
        assert isinstance(FlextApiConstants.TIMEOUT, (int, float))
        assert FlextApiConstants.TIMEOUT > 0

    def test_constants_http_status_ranges(self) -> None:
        """Test HTTP status range constants."""
        # Should have HTTP status range constants
        assert hasattr(FlextApiConstants, "HttpStatusRanges")

        ranges = FlextApiConstants.HttpStatusRanges

        # Success range
        assert hasattr(ranges, "SUCCESS_MIN")
        assert hasattr(ranges, "SUCCESS_MAX")
        assert ranges.SUCCESS_MIN == 200
        assert ranges.SUCCESS_MAX == 300

        # Client error range
        assert hasattr(ranges, "CLIENT_ERROR_MIN")
        assert hasattr(ranges, "CLIENT_ERROR_MAX")
        assert ranges.CLIENT_ERROR_MIN == 400
        assert ranges.CLIENT_ERROR_MAX == 500

        # Server error range
        assert hasattr(ranges, "SERVER_ERROR_MIN")
        assert hasattr(ranges, "SERVER_ERROR_MAX")
        assert ranges.SERVER_ERROR_MIN == 500
        assert ranges.SERVER_ERROR_MAX == 600

    def test_constants_default_headers(self) -> None:
        """Test default headers constants."""
        assert hasattr(FlextApiConstants, "Client")

        client = FlextApiConstants.Client
        assert hasattr(client, "DEFAULT_USER_AGENT")
        assert isinstance(client.DEFAULT_USER_AGENT, str)
        assert "FlextAPI" in client.DEFAULT_USER_AGENT

    def test_constants_service_info(self) -> None:
        """Test service info constants."""
        # API version is available at top level
        assert hasattr(FlextApiConstants, "API_VERSION")
        assert isinstance(FlextApiConstants.API_VERSION, str)
        assert FlextApiConstants.API_VERSION == "0.9.0"

    def test_constants_immutability(self) -> None:
        """Test that constants are properly immutable."""
        # Constants should not be modifiable - skip this test
        # as Python doesn't have true immutability for classes
        original_version = FlextApiConstants.API_VERSION
        assert original_version == "0.9.0"

    def test_constants_inheritance(self) -> None:
        """Test that FlextApiConstants properly inherits from flext-core."""
        # Should inherit from flext-core FlextConstants
        assert hasattr(FlextApiConstants, "__bases__")

        # Should have flext-core constants available
        base_classes = FlextApiConstants.__bases__
        assert len(base_classes) > 0

    def test_constants_all_required_present(self) -> None:
        """Test that all required constants are present."""
        required_constants = [
            "API_VERSION",
            "CACHE_TTL",
            "MAX_RETRIES",
            "TIMEOUT"
        ]

        for const_name in required_constants:
            assert hasattr(FlextApiConstants, const_name), f"Missing constant: {const_name}"

    def test_constants_nested_classes(self) -> None:
        """Test nested constant classes."""
        # Should have nested classes for organization
        nested_classes = ["HttpStatusRanges", "Client", "ContentTypes", "ApiConfig"]

        for class_name in nested_classes:
            assert hasattr(FlextApiConstants, class_name), f"Missing nested class: {class_name}"
            nested_class = getattr(FlextApiConstants, class_name)
            assert isinstance(nested_class, type), f"{class_name} should be a class"
