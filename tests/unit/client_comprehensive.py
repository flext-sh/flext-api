"""Comprehensive tests for FlextApiClient using flext_tests library.

Tests all client functionality with real HTTP operations without mocks.
Uses flext_tests patterns for validation and test data generation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json

from flext_api.client import FlextApiClient


class TestFlextApiClientReal:
    """Comprehensive HTTP client tests using real functionality."""

    def test_client_initialization_with_factory(self) -> None:
        """Test client initialization using FlextApiFactories."""
        client = FlextApiClient(
            config={"base_url": "https://httpbin.org", "timeout": 30.0}
        )

        assert client.base_url == "https://httpbin.org"
        assert client.timeout == 30.0
        assert client.max_retries == 3

    def test_get_request_with_factory(self) -> None:
        """Test GET request using factory-created client."""
        client = FlextApiClient(config={"base_url": "https://httpbin.org"})

        # Real GET request
        result = client.get("/get")

        # Use FlextTestsMatchers for validation
        assert result.is_success
        response = result.value

        # Verify response structure
        assert response.status_code == 200
        assert isinstance(response.body, dict)

    def test_post_request_real(self) -> None:
        """Test POST request with real HTTP service."""
        client = FlextApiClient(config={"base_url": "https://httpbin.org"})

        # Real POST request
        result = client.post("/post")

        assert result.is_success
        response = result.value

        # Verify POST response
        assert response.status_code == 200
        assert isinstance(response.body, dict)

    def test_put_request_real(self) -> None:
        """Test PUT request with real HTTP service."""
        client = FlextApiClient(config={"base_url": "https://httpbin.org"})
        result = client.put("/put")

        assert result.is_success
        response = result.value

        assert response.status_code == 200
        assert isinstance(response.body, dict)

    def test_delete_request_real(self) -> None:
        """Test DELETE request with real HTTP service."""
        client = FlextApiClient(config={"base_url": "https://httpbin.org"})
        result = client.delete("/delete")

        assert result.is_success
        response = result.value

        assert response.status_code == 200
        assert isinstance(response.body, dict)

    def test_network_error_handling_with_factory(self) -> None:
        """Test error handling using factory-created client."""
        # Use non-responsive endpoint to trigger error
        client = FlextApiClient(
            config={"base_url": "http://127.0.0.1:65530", "timeout": 0.3}
        )
        result = client.get("/test")

        # Should fail with network error
        assert result.is_failure
        assert result.error is not None
        assert isinstance(result.error, str)

    def test_http_error_responses_real(self) -> None:
        """Test handling of HTTP error responses."""
        client = FlextApiClient(config={"base_url": "https://httpbin.org"})
        # Request 404 endpoint
        result = client.get("/status/404")

        # Client should handle HTTP errors gracefully
        assert result.is_success  # Still successful FlextResult
        response = result.value
        assert response.status_code == 404

    def test_timeout_behavior_real(self) -> None:
        """Test timeout behavior with slow endpoints."""
        client = FlextApiClient(
            config={"base_url": "https://httpbin.org", "timeout": 2.0}
        )
        # Request endpoint that delays 3 seconds (should timeout)
        result = client.get("/delay/3")

        # Should fail due to timeout
        assert result.is_failure
        assert result.error is not None

    def test_json_response_parsing_real(self) -> None:
        """Test JSON response parsing with complex data."""
        client = FlextApiClient(config={"base_url": "https://httpbin.org"})
        result = client.get("/json")

        assert result.is_success
        response = result.value

        # Verify JSON parsing
        assert response.status_code == 200
        assert isinstance(response.body, dict)
        # httpbin.org /json endpoint returns slideshow data
        assert "slideshow" in json.dumps(response.body)

    def test_retry_behavior_real(self) -> None:
        """Test retry behavior on server errors."""
        # Use client with retry configuration
        client = FlextApiClient(
            config={"base_url": "https://httpbin.org", "max_retries": 2, "timeout": 5.0}
        )
        # Use /status/500 to simulate server error (should be retried)
        result = client.get("/status/500")

        # Should eventually succeed or fail after retries
        # The response itself will be HTTP 500, but FlextResult should be success
        assert result.is_success
        response = result.value
        assert response.status_code == 500

    def test_client_string_representation(self) -> None:
        """Test client string representation."""
        client = FlextApiClient(config={"base_url": "https://api.example.com"})
        client_str = str(client)

        # Should contain meaningful information
        assert "FlextApiClient" in client_str
        assert "object at" in client_str

    def test_multiple_requests_same_client(self) -> None:
        """Test multiple requests with the same client instance."""
        client = FlextApiClient(config={"base_url": "https://httpbin.org"})
        # Multiple GET requests
        result1 = client.get("/get")
        result2 = client.get("/json")
        result3 = client.post("/post")

        # All should succeed
        assert result1.is_success
        assert result2.is_success
        assert result3.is_success

        # Verify responses
        assert result1.value.status_code == 200
        assert result2.value.status_code == 200
        assert result3.value.status_code == 200

    def test_client_configuration_validation(self) -> None:
        """Test client configuration validation."""
        # Valid configuration should work
        client = FlextApiClient(
            config={
                "base_url": "https://httpbin.org",
                "timeout": 60.0,
                "max_retries": 5,
            }
        )

        assert client.base_url == "https://httpbin.org"
        assert client.timeout == 60.0
        assert client.max_retries == 5
