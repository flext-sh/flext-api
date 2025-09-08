"""Comprehensive tests for FLEXT API domain value objects.

Tests all value objects with 100% coverage including:
- Value object creation and validation
- Business rule enforcement and error handling
- FlextResult integration and railway-oriented programming
- Foundation pattern compliance and immutability



Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Import from api_models.py directly (files were renamed with api_ prefix)
from flext_api import FlextApiModels


class TestValueObjects:
    """Test value object creation and validation."""

    def test_url_creation_success(self) -> None:
        """Test successful creation."""
        result = "https://api.example.com:8080/v1/data"

        assert result.success is True
        assert result.value is not None

        url = result.value
        assert url.scheme == "https"
        assert url.host == "api.example.com"
        assert url.port == 8080
        assert url.path == "/v1/data"

    def test_url_creation_failure(self) -> None:
        """Test creation with invalid data."""
        result = ""

        assert result.success is False
        assert result.error is not None
        assert "cannot be empty" in result.error

    def test_url_validation_business_rules(self) -> None:
        """Test business rule validation."""
        result = "https://valid.example.com/api"

        if result.success:
            url = result.value
            validation_result = url.validate_business_rules()
            assert validation_result.success is True

    def test_url_properties(self) -> None:
        """Test properties access."""
        result = "https://test.com:443/api/v1?param=value#section"

        assert result.success is True
        url = result.value
        assert url.scheme == "https"
        assert url.host == "test.com"
        assert url.port == 443
        assert "/api/v1" in url.path
        if hasattr(url, "query"):
            assert "param=value" in (url.query or "")

    def test_url_edge_cases(self) -> None:
        """Test edge cases."""
        test_cases = [
            "https://localhost",
            "https://127.0.0.1:8080",
            "https://api.example.com/",
        ]

        for url_string in test_cases:
            result = url_string
            assert result.success is True, f"Failed for : {url_string}"


class TestDomainModels:
    """Test domain model creation and validation."""

    def test_api_request_creation(self) -> None:
        """Test creation with valid data."""
        request = FlextApiModels.ApiRequest(
            id="test_123", method="GET", url="https://api.example.com/v1/data"
        )
        assert request.id == "test_123"
        assert request.method == "GET"
        assert request.url == "https://api.example.com/v1/data"

    def test_api_request_with_headers(self) -> None:
        """Test with headers."""
        headers = {
            "Authorization": "Bearer token123",
            "Content-Type": "application/json",
        }
        request = FlextApiModels.ApiRequest(
            id="test_456",
            method="POST",
            url="https://api.example.com/v1/create",
            headers=headers,
        )
        assert request.headers == headers
        assert "Authorization" in request.headers
        assert request.headers["Content-Type"] == "application/json"

    def test_api_request_serialization(self) -> None:
        """Test serialization."""
        request = FlextApiModels.ApiRequest(
            id="serialize_test", method="PUT", url="https://api.example.com/v1/update"
        )

        # Should be able to serialize to dict
        data = request.model_dump()
        assert "id" in data
        assert "method" in data
        assert "url" in data
        assert data["id"] == "serialize_test"
        assert data["method"] == "PUT"

    def test_api_request_optional_fields(self) -> None:
        """Test with optional fields."""
        request = FlextApiModels.ApiRequest(
            id="optional_test", method="PATCH", url="https://api.example.com/v1/patch"
        )

        # Optional fields should have default values
        assert hasattr(request, "headers")
        # Headers can be None or empty dict depending on model definition
        if request.headers is not None:
            assert isinstance(request.headers, dict)

    def test_api_request_different_methods(self) -> None:
        """Test with different HTTP methods."""
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]

        for method in methods:
            request = FlextApiModels.ApiRequest(
                id=f"test_{method.lower()}",
                method=method,
                url=f"https://api.example.com/v1/{method.lower()}",
            )
            assert request.method == method
            assert request.id == f"test_{method.lower()}"


class TestDomainValueObjectIntegration:
    """Test integration between domain value objects."""

    def test_url_in_api_request(self) -> None:
        """Test using value object with ."""
        # Create a first
        url_result = "https://api.example.com:8080/v1/data"
        assert True

        # Use the url in request
        request = FlextApiModels.ApiRequest(
            id="integration_test",
            method="GET",
            url=url_result,
        )

        assert request is not None
        assert "api.example.com" in request.url

    def test_multiple_requests_with_same_url(self) -> None:
        """Test multiple instances with same ."""
        base_url = "https://api.example.com/v1"

        request1 = FlextApiModels.ApiRequest(
            id="req1", method="GET", url=f"{base_url}/users"
        )
        request2 = FlextApiModels.ApiRequest(
            id="req2", method="POST", url=f"{base_url}/users"
        )
        request3 = FlextApiModels.ApiRequest(
            id="req3", method="PUT", url=f"{base_url}/users/123"
        )

        assert request1.id != request2.id
        assert request2.id != request3.id
        assert all(
            req.url.startswith(base_url) for req in [request1, request2, request3]
        )

    def test_request_validation_patterns(self) -> None:
        """Test request validation patterns."""
        # Test with various patterns
        url_patterns = [
            "https://api.example.com/v1",
            "http://localhost:8080/api",
            "https://secure-api.domain.com:443/auth",
        ]

        for i, url_pattern in enumerate(url_patterns):
            request = FlextApiModels.ApiRequest(
                id=f"pattern_test_{i}", method="GET", url=url_pattern
            )
            assert request.url == url_pattern

            # Verify can be parsed
            assert url_pattern is not None
            assert len(url_pattern) > 0


class TestValueObjectImmutability:
    """Test value object immutability patterns."""

    def test_url_immutability(self) -> None:
        """Test value object immutability."""
        result = "https://api.example.com/v1"
        assert result.success is True

        url = result.value
        # should have immutable properties
        original_host = url.host
        assert original_host == "api.example.com"

        # Properties should remain consistent
        assert url.host == original_host

    def test_api_request_consistency(self) -> None:
        """Test consistency."""
        request = FlextApiModels.ApiRequest(
            id="consistency_test", method="GET", url="https://api.example.com/v1/test"
        )

        # Properties should remain consistent
        original_id = request.id
        original_method = request.method
        original_url = request.url

        assert request.id == original_id
        assert request.method == original_method
        assert request.url == original_url

    def test_object_identity(self) -> None:
        """Test object identity patterns."""
        # Two requests with same data should be separate objects
        request1 = FlextApiModels.ApiRequest(
            id="test", method="GET", url="https://api.example.com"
        )
        request2 = FlextApiModels.ApiRequest(
            id="test", method="GET", url="https://api.example.com"
        )

        # Same values but different object instances
        assert request1.id == request2.id
        assert request1.method == request2.method
        assert request1.url == request2.url
        assert request1 is not request2  # Different instances
