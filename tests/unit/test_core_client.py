"""Tests for FlextApiClient core functionality.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

import pytest

from flext_api.core.client import (
    FlextApiCachingPlugin,
    FlextApiCircuitBreakerPlugin,
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiRetryPlugin,
    create_client,
    create_client_with_plugins,
)


class TestFlextApiClientConfig:
    """Test client configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = FlextApiClientConfig("https://api.example.com")

        assert config.base_url == "https://api.example.com"
        assert config.timeout == 30.0
        assert config.headers == {}
        assert config.verify_ssl is True
        assert config.follow_redirects is True

    def test_custom_config(self):
        """Test custom configuration values."""
        config = FlextApiClientConfig(
            "https://api.example.com",
            timeout=60.0,
            headers={"Authorization": "Bearer token"},
            verify_ssl=False,
        )

        assert config.timeout == 60.0
        assert config.headers["Authorization"] == "Bearer token"
        assert config.verify_ssl is False


class TestFlextApiClient:
    """Test main client functionality."""

    def test_client_initialization(self):
        """Test client initialization."""
        config = FlextApiClientConfig("https://api.example.com")
        client = FlextApiClient(config)

        assert client.config == config
        assert client._session is None
        assert client._plugins == []
        assert client._request_count == 0

    def test_plugin_management(self):
        """Test adding and removing plugins."""
        client = create_client("https://api.example.com")
        plugin = FlextApiCachingPlugin()

        # Add plugin
        client.add_plugin(plugin)
        assert len(client._plugins) == 1
        assert client._plugins[0] == plugin

        # Remove plugin
        result = client.remove_plugin("CachingPlugin")
        assert result is True
        assert len(client._plugins) == 0

        # Try to remove non-existent plugin
        result = client.remove_plugin("NonExistent")
        assert result is False

    def test_url_building(self):
        """Test URL building."""
        client = create_client("https://api.example.com")

        # Test basic path
        assert client.build_full_url("/users") == "https://api.example.com/users"
        assert client.build_full_url("users") == "https://api.example.com/users"

        # Test with base URL ending in slash
        client = create_client("https://api.example.com/")
        assert client.build_full_url("/users") == "https://api.example.com/users"

    @pytest.mark.asyncio
    async def test_session_management(self):
        """Test session creation and cleanup."""
        client = create_client("https://httpbin.org")

        # Initially no session
        assert client.get_session() is None

        # Create session
        session = await client.ensure_session()
        assert session is not None
        assert not session.closed

        # Same session returned
        session2 = await client.ensure_session()
        assert session2 is session

        # Close client
        await client.close()
        assert session.closed

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test client health check."""
        client = create_client("https://httpbin.org")

        health_result = await client.get_health()
        assert health_result.is_success

        health_data = health_result.data
        assert health_data["status"] == "idle"
        assert health_data["request_count"] == 0
        assert health_data["average_response_time"] == 0
        assert health_data["active_plugins"] == []
        assert health_data["session_closed"] is True

    @pytest.mark.asyncio
    async def test_metrics(self):
        """Test client metrics."""
        client = create_client("https://httpbin.org")
        plugin = FlextApiCachingPlugin()
        client.add_plugin(plugin)

        metrics_result = await client.get_metrics()
        assert metrics_result.is_success

        metrics = metrics_result.data
        assert "client" in metrics
        assert "plugins" in metrics
        assert "CachingPlugin" in metrics["plugins"]

    @pytest.mark.asyncio
    async def test_real_http_request(self):
        """Test real HTTP requests (integration test)."""
        client = create_client("https://httpbin.org")

        try:
            # Test GET request
            result = await client.get("/json")
            assert result.is_success

            response = result.data
            assert response.status_code == 200
            assert response.data is not None
            assert response.elapsed_time > 0

            # Verify metrics updated
            health_result = await client.get_health()
            health_data = health_result.data
            assert health_data["request_count"] == 1
            assert health_data["average_response_time"] > 0

        finally:
            await client.close()


class TestFlextApiCachingPlugin:
    """Test caching plugin."""

    def test_plugin_initialization(self):
        """Test plugin initialization."""
        plugin = FlextApiCachingPlugin(ttl_seconds=600)

        assert plugin.name == "CachingPlugin"
        assert plugin.ttl_seconds == 600
        assert plugin.enabled is True
        assert plugin.metrics["hits"] == 0
        assert plugin.metrics["misses"] == 0

    def test_cache_key_generation(self):
        """Test cache key generation."""
        plugin = FlextApiCachingPlugin()

        from flext_api.core.client import FlextApiClientMethod, FlextApiClientRequest

        request = FlextApiClientRequest(
            method=FlextApiClientMethod.GET,
            url="https://api.example.com/users",
            params={"page": 1},
        )

        key = plugin._cache_key(request)
        assert isinstance(key, str)
        assert "GET" in key
        assert "users" in key

    def test_cacheable_check(self):
        """Test cacheable request check."""
        plugin = FlextApiCachingPlugin()

        from flext_api.core.client import FlextApiClientMethod, FlextApiClientRequest

        get_request = FlextApiClientRequest(
            method=FlextApiClientMethod.GET,
            url="https://api.example.com/users",
        )

        post_request = FlextApiClientRequest(
            method=FlextApiClientMethod.POST,
            url="https://api.example.com/users",
        )

        assert plugin._is_cacheable(get_request) is True
        assert plugin._is_cacheable(post_request) is False

    def test_cache_stats(self):
        """Test cache statistics."""
        plugin = FlextApiCachingPlugin(ttl_seconds=300)

        stats = plugin.get_cache_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["evictions"] == 0
        assert stats["cache_size"] == 0
        assert stats["ttl_seconds"] == 300


class TestFlextApiRetryPlugin:
    """Test retry plugin."""

    def test_plugin_initialization(self):
        """Test plugin initialization."""
        plugin = FlextApiRetryPlugin(max_retries=5, backoff_factor=2.0)

        assert plugin.name == "RetryPlugin"
        assert plugin.max_retries == 5
        assert plugin.backoff_factor == 2.0
        assert plugin.metrics["total_retries"] == 0

    def test_should_retry_logic(self):
        """Test retry logic."""
        plugin = FlextApiRetryPlugin()

        assert plugin._should_retry(500) is True  # Server error
        assert plugin._should_retry(502) is True  # Bad gateway
        assert plugin._should_retry(429) is True  # Rate limited
        assert plugin._should_retry(404) is False # Not found
        assert plugin._should_retry(200) is False # Success


class TestFlextApiCircuitBreakerPlugin:
    """Test circuit breaker plugin."""

    def test_plugin_initialization(self):
        """Test plugin initialization."""
        plugin = FlextApiCircuitBreakerPlugin(
            failure_threshold=3,
            timeout_seconds=30,
            success_threshold=2,
        )

        assert plugin.name == "CircuitBreakerPlugin"
        assert plugin.failure_threshold == 3
        assert plugin.timeout_seconds == 30
        assert plugin.success_threshold == 2
        assert plugin.state == "closed"

    @pytest.mark.asyncio
    async def test_failure_recording(self):
        """Test failure recording."""
        plugin = FlextApiCircuitBreakerPlugin(failure_threshold=2)

        # Record failures
        await plugin._record_failure()
        assert plugin.failure_count == 1
        assert plugin.state == "closed"

        await plugin._record_failure()
        assert plugin.failure_count == 2
        assert plugin.state == "open"  # Should trip
        assert plugin.metrics["trips"] == 1

    @pytest.mark.asyncio
    async def test_success_recording(self):
        """Test success recording."""
        plugin = FlextApiCircuitBreakerPlugin()

        # Record success in closed state
        await plugin._record_success()
        assert plugin.failure_count == 0

        # Test half-open to closed transition
        plugin.state = "half-open"
        plugin.success_threshold = 1

        await plugin._record_success()
        assert plugin.state == "closed"


class TestFactoryFunctions:
    """Test factory functions."""

    def test_create_client(self):
        """Test basic client creation."""
        client = create_client("https://api.example.com", timeout=60)

        assert isinstance(client, FlextApiClient)
        assert client.config.base_url == "https://api.example.com"
        assert client.config.timeout == 60

    def test_create_client_with_plugins(self):
        """Test client creation with plugins."""
        client = create_client_with_plugins(
            "https://api.example.com",
            enable_cache=True,
            enable_retry=True,
            enable_circuit_breaker=False,
        )

        assert len(client._plugins) == 2
        plugin_names = [p.name for p in client._plugins]
        assert "CachingPlugin" in plugin_names
        assert "RetryPlugin" in plugin_names
        assert "CircuitBreakerPlugin" not in plugin_names


@pytest.mark.integration
class TestIntegrationScenarios:
    """Integration tests with real HTTP calls."""

    @pytest.mark.asyncio
    async def test_client_with_caching(self):
        """Test client with caching plugin."""
        client = create_client_with_plugins(
            "https://httpbin.org",
            enable_cache=True,
            enable_retry=False,
            enable_circuit_breaker=False,
        )

        try:
            # First request - cache miss
            result1 = await client.get("/uuid")
            assert result1.is_success

            # Get cache stats
            cache_plugin = client._plugins[0]
            stats = cache_plugin.get_cache_stats()
            assert stats["misses"] >= 1

            # Second request to same endpoint - potential cache hit
            result2 = await client.get("/uuid")
            assert result2.is_success

        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_streaming_response(self):
        """Test streaming response."""
        client = create_client("https://httpbin.org")

        try:
            from flext_api.core.client import FlextApiClientMethod

            chunks = []
            async for chunk in client.stream(FlextApiClientMethod.GET, "/stream/3"):
                chunks.append(chunk)
                if len(chunks) >= 3:  # Limit chunks for test
                    break

            assert len(chunks) > 0
            assert all(isinstance(chunk, bytes) for chunk in chunks)

        finally:
            await client.close()
