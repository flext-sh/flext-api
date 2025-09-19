"""Comprehensive tests for FlextApiClient using flext_tests library.

Tests all client functionality with real HTTP operations without mocks.
Uses flext_tests patterns for validation and test data generation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json

import pytest
from flext_tests import FlextTestsMatchers

from tests.factories import FlextApiFactories


class TestFlextApiClientReal:
    """Comprehensive HTTP client tests using real functionality."""

    def test_client_initialization_with_factory(self) -> None:
        """Test client initialization using FlextApiFactories."""
        client = FlextApiFactories.create_client(
            base_url="https://httpbin.org",
            timeout=30.0,
        )

        assert client.base_url == "https://httpbin.org"
        assert client.timeout == 30.0
        assert client.max_retries == 3

    @pytest.mark.asyncio
    async def test_get_request_with_factory(self) -> None:
        """Test GET request using factory-created client."""
        client = FlextApiFactories.create_client(base_url="https://httpbin.org")
        await client.start()

        try:
            # Real GET request
            result = await client.get("/get")

            # Use FlextTestsMatchers for validation
            FlextTestsMatchers.assert_result_success(result)
            response = result.value

            # Verify response structure
            assert response.status_code == 200
            assert isinstance(response.body, dict)
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_post_request_real(self) -> None:
        """Test POST request with real HTTP service."""
        client = FlextApiFactories.create_client(base_url="https://httpbin.org")
        await client.start()

        try:
            # Real POST request
            result = await client.post("/post")

            FlextTestsMatchers.assert_result_success(result)
            response = result.value

            # Verify POST response
            assert response.status_code == 200
            assert isinstance(response.body, dict)
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_put_request_real(self) -> None:
        """Test PUT request with real HTTP service."""
        client = FlextApiFactories.create_client(base_url="https://httpbin.org")
        await client.start()

        try:
            result = await client.put("/put")

            FlextTestsMatchers.assert_result_success(result)
            response = result.value

            assert response.status_code == 200
            assert isinstance(response.body, dict)
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_delete_request_real(self) -> None:
        """Test DELETE request with real HTTP service."""
        client = FlextApiFactories.create_client(base_url="https://httpbin.org")
        await client.start()

        try:
            result = await client.delete("/delete")

            FlextTestsMatchers.assert_result_success(result)
            response = result.value

            assert response.status_code == 200
            assert isinstance(response.body, dict)
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_network_error_handling_with_factory(self) -> None:
        """Test error handling using factory-created client."""
        # Use non-responsive endpoint to trigger error
        client = FlextApiFactories.create_client(
            base_url="http://127.0.0.1:65530",
            timeout=0.3,
        )
        await client.start()

        try:
            result = await client.get("/test")

            # Should fail with network error
            FlextTestsMatchers.assert_result_failure(result)
            assert result.error is not None
            assert isinstance(result.error, str)
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_http_error_responses_real(self) -> None:
        """Test handling of HTTP error responses."""
        client = FlextApiFactories.create_client(base_url="https://httpbin.org")
        await client.start()

        try:
            # Request 404 endpoint
            result = await client.get("/status/404")

            # Client should handle HTTP errors gracefully
            FlextTestsMatchers.assert_result_success(
                result,
            )  # Still successful FlextResult
            response = result.value
            assert response.status_code == 404
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_timeout_behavior_real(self) -> None:
        """Test timeout behavior with slow endpoints."""
        client = FlextApiFactories.create_client(
            base_url="https://httpbin.org",
            timeout=2.0,  # 2 second timeout
        )
        await client.start()

        try:
            # Request endpoint that delays 3 seconds (should timeout)
            result = await client.get("/delay/3")

            # Should fail due to timeout
            FlextTestsMatchers.assert_result_failure(result)
            assert result.error is not None
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_json_response_parsing_real(self) -> None:
        """Test JSON response parsing with complex data."""
        client = FlextApiFactories.create_client(base_url="https://httpbin.org")
        await client.start()

        try:
            result = await client.get("/json")

            FlextTestsMatchers.assert_result_success(result)
            response = result.value

            # Verify JSON parsing
            assert response.status_code == 200
            assert isinstance(response.body, dict)
            # httpbin.org /json endpoint returns slideshow data
            assert "slideshow" in json.dumps(response.body)
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_retry_behavior_real(self) -> None:
        """Test retry behavior on server errors."""
        # Use client with retry configuration
        client = FlextApiFactories.create_client(
            base_url="https://httpbin.org",
            max_retries=2,
            timeout=5.0,
        )
        await client.start()

        try:
            # Use /status/500 to simulate server error (should be retried)
            result = await client.get("/status/500")

            # Should eventually succeed or fail after retries
            # The response itself will be HTTP 500, but FlextResult should be success
            FlextTestsMatchers.assert_result_success(result)
            response = result.value
            assert response.status_code == 500
        finally:
            await client.close()

    def test_client_string_representation(self) -> None:
        """Test client string representation."""
        client = FlextApiFactories.create_client(base_url="https://api.example.com")
        client_str = str(client)

        # Should contain meaningful information
        assert "FlextApiClient" in client_str
        assert "object at" in client_str

    @pytest.mark.asyncio
    async def test_multiple_requests_same_client(self) -> None:
        """Test multiple requests with the same client instance."""
        client = FlextApiFactories.create_client(base_url="https://httpbin.org")
        await client.start()

        try:
            # Multiple GET requests
            result1 = await client.get("/get")
            result2 = await client.get("/json")
            result3 = await client.post("/post")

            # All should succeed
            FlextTestsMatchers.assert_result_success(result1)
            FlextTestsMatchers.assert_result_success(result2)
            FlextTestsMatchers.assert_result_success(result3)

            # Verify responses
            assert result1.value.status_code == 200
            assert result2.value.status_code == 200
            assert result3.value.status_code == 200
        finally:
            await client.close()

    def test_client_configuration_validation(self) -> None:
        """Test client configuration validation."""
        # Valid configuration should work
        client = FlextApiFactories.create_client(
            base_url="https://httpbin.org",
            timeout=60.0,
            max_retries=5,
        )

        assert client.base_url == "https://httpbin.org"
        assert client.timeout == 60.0
        assert client.max_retries == 5
