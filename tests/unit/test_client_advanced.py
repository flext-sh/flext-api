"""Advanced tests for FlextApiClient to improve coverage.

Tests for methods that are not covered in basic tests.
Focuses on error handling, edge cases, and advanced features.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_tests import FlextTestsMatchers

from flext_api import FlextApiClient, FlextApiModels


class TestFlextApiClientAdvanced:
    """Advanced tests for FlextApiClient to improve coverage."""

    def test_client_create_method(self) -> None:
        """Test FlextApiClient.create() class method."""
        config_data = {"base_url": "https://test.example.com", "timeout": 15.0}

        result = FlextApiClient.create(config_data)
        FlextTestsMatchers.assert_result_success(result)

        client = result.value
        assert isinstance(client, FlextApiClient)
        assert client.base_url == "https://test.example.com"
        assert client.timeout == 15.0

    def test_client_create_with_model_config(self) -> None:
        """Test FlextApiClient.create() with FlextApiModels.ClientConfig."""
        config = FlextApiModels.ClientConfig(
            base_url="https://model.example.com", timeout=20.0, max_retries=5
        )

        result = FlextApiClient.create(config)
        FlextTestsMatchers.assert_result_success(result)

        client = result.value
        assert isinstance(client, FlextApiClient)
        assert client.base_url == "https://model.example.com"
        assert client.timeout == 20.0
        assert client.max_retries == 5

    def test_client_create_invalid_config(self) -> None:
        """Test FlextApiClient.create() with invalid config."""
        invalid_config = {"base_url": "invalid-url"}

        result = FlextApiClient.create(invalid_config)
        FlextTestsMatchers.assert_result_failure(result)
        assert "Failed to create client" in result.error

    def test_client_properties(self) -> None:
        """Test client property accessors."""
        client = FlextApiClient(
            base_url="https://props.example.com", timeout=25.0, max_retries=7
        )

        assert client.base_url == "https://props.example.com"
        assert client.timeout == 25.0
        assert client.max_retries == 7

    def test_client_httpx_client_property(self) -> None:
        """Test httpx_client property."""
        client = FlextApiClient(base_url="https://httpx.example.com")

        httpx_client = client.httpx_client
        assert httpx_client is not None
        # Should return the same instance on subsequent calls
        assert client.httpx_client is httpx_client

    @pytest.mark.asyncio
    async def test_client_aiohttp_session_property(self) -> None:
        """Test aiohttp_session property."""
        client = FlextApiClient(base_url="https://aiohttp.example.com")

        session = client.aiohttp_session
        assert session is not None
        # Should return the same instance on subsequent calls
        assert client.aiohttp_session is session

    def test_client_build_headers(self) -> None:
        """Test _build_headers method."""
        client = FlextApiClient(
            base_url="https://headers.example.com", api_key="test-key-123"
        )

        headers = client._build_headers()
        assert isinstance(headers, dict)
        assert "User-Agent" in headers
        assert headers["User-Agent"].startswith("FlextAPI/")

    def test_client_build_headers_with_auth(self) -> None:
        """Test _build_headers with authentication."""
        client = FlextApiClient(
            base_url="https://auth.example.com",
            auth_type="bearer",
            auth_token="secret-key-456",
        )

        headers = client._build_headers()
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Bearer ")

    def test_client_generate_cache_key(self) -> None:
        """Test _generate_cache_key method."""
        client = FlextApiClient(base_url="https://cache.example.com")

        key1 = client._generate_cache_key("GET", "https://test.com/api", {"page": 1})
        key2 = client._generate_cache_key("GET", "https://test.com/api", {"page": 2})

        assert isinstance(key1, str)
        assert isinstance(key2, str)
        assert key1 != key2  # Different params should generate different keys

    def test_client_calculate_retry_delay(self) -> None:
        """Test _calculate_retry_delay method."""
        client = FlextApiClient(base_url="https://retry.example.com")

        delay1 = client._calculate_retry_delay(1)
        delay2 = client._calculate_retry_delay(2)
        delay3 = client._calculate_retry_delay(3)

        assert isinstance(delay1, float)
        assert isinstance(delay2, float)
        assert isinstance(delay3, float)
        assert delay1 < delay2 < delay3  # Exponential backoff

    def test_client_record_circuit_success(self) -> None:
        """Test _record_circuit_success method."""
        client = FlextApiClient(
            base_url="https://circuit.example.com", enable_circuit_breaker=True
        )

        # Should not raise any exceptions
        client._record_circuit_success()

    def test_client_record_circuit_failure(self) -> None:
        """Test _record_circuit_failure method."""
        client = FlextApiClient(
            base_url="https://circuit.example.com", enable_circuit_breaker=True
        )

        # Should not raise any exceptions
        client._record_circuit_failure()

    def test_client_get_metrics(self) -> None:
        """Test get_metrics method."""
        client = FlextApiClient(base_url="https://metrics.example.com")

        metrics = client.get_metrics()
        assert isinstance(metrics, list)
        # Initially should be empty
        assert len(metrics) == 0

    def test_client_clear_cache(self) -> None:
        """Test clear_cache method."""
        client = FlextApiClient(base_url="https://cache.example.com")

        # Should not raise any exceptions
        client.clear_cache()

    def test_client_health_check(self) -> None:
        """Test health_check method."""
        client = FlextApiClient(base_url="https://health.example.com")

        health = client.health_check()
        assert isinstance(health, dict)
        assert "data" in health
        assert "message" in health
        assert "status_code" in health
        assert health["status_code"] == 200

    def test_client_string_representations(self) -> None:
        """Test string representations of client."""
        client = FlextApiClient(base_url="https://repr.example.com")

        str_repr = str(client)
        repr_repr = repr(client)

        assert isinstance(str_repr, str)
        assert isinstance(repr_repr, str)
        assert "FlextApiClient" in repr_repr
        # String representation may not include URL directly
        assert len(str_repr) > 0

    @pytest.mark.asyncio
    async def test_client_async_context_manager(self) -> None:
        """Test client as async context manager."""
        async with FlextApiClient(base_url="https://context.example.com") as client:
            assert isinstance(client, FlextApiClient)
            assert client.base_url == "https://context.example.com"

    @pytest.mark.asyncio
    async def test_client_start_method(self) -> None:
        """Test client start method."""
        client = FlextApiClient(base_url="https://start.example.com")

        result = await client.start()
        FlextTestsMatchers.assert_result_success(result)

    @pytest.mark.asyncio
    async def test_client_stop_method(self) -> None:
        """Test client stop method."""
        client = FlextApiClient(base_url="https://stop.example.com")

        result = await client.stop()
        FlextTestsMatchers.assert_result_success(result)

    @pytest.mark.asyncio
    async def test_client_close_method(self) -> None:
        """Test client close method."""
        client = FlextApiClient(base_url="https://close.example.com")

        result = await client.close()
        FlextTestsMatchers.assert_result_success(result)

    def test_client_with_different_configurations(self) -> None:
        """Test client with various configuration options."""
        configs = [
            {"base_url": "https://config1.example.com", "timeout": 10.0},
            {"base_url": "https://config2.example.com", "max_retries": 5},
            {"base_url": "https://config3.example.com", "enable_caching": True},
            {"base_url": "https://config4.example.com", "enable_rate_limit": True},
            {"base_url": "https://config5.example.com", "enable_circuit_breaker": True},
        ]

        for config in configs:
            client = FlextApiClient(**config)
            assert isinstance(client, FlextApiClient)
            assert client.base_url == config["base_url"]

    def test_client_edge_cases(self) -> None:
        """Test client edge cases."""
        # Test with minimal config
        client = FlextApiClient(base_url="https://minimal.example.com")
        assert isinstance(client, FlextApiClient)

        # Test with different configurations
        client2 = FlextApiClient(base_url="https://edge.example.com", timeout=5.0)
        assert isinstance(client2, FlextApiClient)
