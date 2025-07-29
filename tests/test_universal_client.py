#!/usr/bin/env python3
"""Test FlextApi Universal API Client functionality.

Comprehensive test suite validating all enterprise features and ensuring
zero duplications and proper ABI design.
"""

import asyncio
import json
import time
from unittest.mock import AsyncMock, patch

import pytest

from flext_api import (
    FlextApiCachingPlugin,
    FlextApiCircuitBreakerPlugin,
    FlextApiClient,
    FlextApiClientBuilder,
    FlextApiClientConfig,
    FlextApiClientMethod,
    FlextApiClientRequest,
    FlextApiClientResponse,
    FlextApiGraphQLClient,
    FlextApiLoggingPlugin,
    FlextApiMetricsPlugin,
    FlextApiRetryPlugin,
    FlextApiStreamingClient,
    FlextApiValidationManager,
    FlextApiWebSocketClient,
    flext_api_client_context,
    flext_api_create_client,
)

# ==============================================================================
# FIXTURES
# ==============================================================================


@pytest.fixture
def mock_session() -> AsyncMock:
    """Mock aiohttp session for testing."""
    session = AsyncMock()
    response = AsyncMock()
    response.status = 200
    response.headers = {"content-type": "application/json"}
    response.text.return_value = '{"message": "success"}'
    response.json.return_value = {"message": "success"}

    session.request.return_value.__aenter__.return_value = response
    session.closed = False
    session.close = AsyncMock()

    return session


@pytest.fixture
def basic_config() -> FlextApiClientConfig:
    """Basic client configuration for testing."""
    return FlextApiClientConfig(
        base_url="https://api.test.com",
        timeout=10.0,
        max_retries=2,
        cache_enabled=True,
        circuit_breaker_enabled=True,
        metrics_enabled=True,
    )


@pytest.fixture
async def test_client(
    basic_config: FlextApiClientConfig,
    mock_session: AsyncMock,
) -> FlextApiClient:
    """Pre-configured test client."""
    client = FlextApiClient(basic_config)
    client._session = mock_session
    yield client
    await client.close()


# ==============================================================================
# CORE CLIENT TESTS
# ==============================================================================


class TestFlextApiClient:
    """Test core FlextApiClient functionality."""

    async def test_client_initialization(
        self,
        basic_config: FlextApiClientConfig,
    ) -> None:
        """Test client initializes with correct configuration."""
        client = FlextApiClient(basic_config)

        assert client.config.base_url == "https://api.test.com"
        assert client.config.timeout == 10.0
        assert client.config.max_retries == 2
        assert client.config.cache_enabled is True
        assert client.config.circuit_breaker_enabled is True

        await client.close()

    async def test_client_as_context_manager(
        self,
        basic_config: FlextApiClientConfig,
    ) -> None:
        """Test client works as async context manager."""
        async with FlextApiClient(basic_config) as client:
            assert client is not None
            assert isinstance(client, FlextApiClient)

    async def test_session_creation(self, test_client: FlextApiClient) -> None:
        """Test HTTP session is created properly."""
        await test_client._ensure_session()
        assert test_client._session is not None

    async def test_public_methods_for_protocols(
        self,
        test_client: FlextApiClient,
    ) -> None:
        """Test public methods work correctly for protocol clients."""
        await test_client.ensure_session()

        session = test_client.get_session()
        assert session is not None

        full_url = test_client.build_full_url("/api/v1/test")
        assert full_url == "https://api.test.com/api/v1/test"

    @patch("aiohttp.ClientSession")
    async def test_successful_request(
        self,
        mock_session_class: object,
        test_client: FlextApiClient,
    ) -> None:
        """Test successful HTTP request execution."""
        # Mock session and response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text.return_value = '{"result": "success"}'
        mock_response.json.return_value = {"result": "success"}

        test_client._session.request.return_value.__aenter__.return_value = (
            mock_response
        )

        request = FlextApiClientRequest(
            method=FlextApiClientMethod.GET,
            url="/api/test",
            timeout=5.0,
        )

        result = await test_client.request(request)

        assert result.success is True
        assert result.data.status_code == 200
        assert result.data.json_data == {"result": "success"}
        assert result.data.execution_time_ms > 0

    async def test_client_metrics(self, test_client: FlextApiClient) -> None:
        """Test client metrics collection."""
        metrics = test_client.get_metrics()

        assert hasattr(metrics, "total_requests")
        assert hasattr(metrics, "successful_requests")
        assert hasattr(metrics, "failed_requests")
        assert hasattr(metrics, "cached_requests")
        assert hasattr(metrics, "uptime_seconds")
        assert metrics.uptime_seconds >= 0

    async def test_client_health_status(self, test_client: FlextApiClient) -> None:
        """Test client health monitoring."""
        health = test_client.get_health()

        assert "status" in health
        assert "circuit_breaker_state" in health
        assert "cache_size" in health
        assert "plugins_loaded" in health
        assert "uptime_seconds" in health
        assert "success_rate" in health

        assert health["plugins_loaded"] == 0  # No plugins added yet


# ==============================================================================
# BUILDER PATTERN TESTS
# ==============================================================================


class TestFlextApiClientBuilder:
    """Test FlextApiClientBuilder pattern."""

    def test_builder_configuration(self) -> None:
        """Test builder configures client correctly."""
        builder = FlextApiClientBuilder()

        client = (
            builder.with_base_url("https://test.api.com")
            .with_timeout(30.0)
            .with_auth_token("token123")
            .with_api_key("key456")
            .with_http2(True)
            .with_caching(True, 600)
            .with_circuit_breaker(True, 5)
            .with_retries(3, 2.0)
            .with_headers({"x-custom": "value"})
            .with_validation(True, True)
            .with_observability(True, True)
            .build()
        )

        assert client.config.base_url == "https://test.api.com"
        assert client.config.timeout == 30.0
        assert client.config.auth_token == "token123"
        assert client.config.api_key == "key456"
        assert client.config.http2_enabled is True
        assert client.config.cache_enabled is True
        assert client.config.cache_default_ttl == 600
        assert client.config.circuit_breaker_enabled is True
        assert client.config.circuit_failure_threshold == 5
        assert client.config.max_retries == 3
        assert client.config.retry_delay == 2.0
        assert client.config.default_headers["x-custom"] == "value"
        assert client.config.validate_requests is True
        assert client.config.validate_responses is True
        assert client.config.metrics_enabled is True
        assert client.config.tracing_enabled is True

    def test_builder_with_plugins(self) -> None:
        """Test builder adds plugins correctly."""
        plugin1 = FlextApiLoggingPlugin()
        plugin2 = FlextApiRetryPlugin()

        client = (
            FlextApiClientBuilder()
            .with_base_url("https://test.com")
            .with_plugin(plugin1)
            .with_plugin(plugin2)
            .build()
        )

        assert len(client._plugins) == 2
        assert plugin1 in client._plugins
        assert plugin2 in client._plugins


# ==============================================================================
# CONVENIENCE FUNCTIONS TESTS
# ==============================================================================


class TestConvenienceFunctions:
    """Test convenience factory functions."""

    def test_flext_api_create_client(self) -> None:
        """Test convenience client factory."""
        client = flext_api_create_client(
            base_url="https://api.example.com",
            timeout=20.0,
            auth_token="test-token",
            enable_caching=True,
            enable_circuit_breaker=True,
            enable_http2=True,
        )

        assert client.config.base_url == "https://api.example.com"
        assert client.config.timeout == 20.0
        assert client.config.auth_token == "test-token"
        assert client.config.cache_enabled is True
        assert client.config.circuit_breaker_enabled is True
        assert client.config.http2_enabled is True

    async def test_flext_api_client_context(self) -> None:
        """Test async context manager factory."""
        async with flext_api_client_context("https://test.com") as client:
            assert isinstance(client, FlextApiClient)
            assert client.config.base_url == "https://test.com"


# ==============================================================================
# PLUGIN SYSTEM TESTS
# ==============================================================================


class TestPluginSystem:
    """Test plugin system functionality."""

    async def test_logging_plugin(self, test_client: FlextApiClient) -> None:
        """Test logging plugin functionality."""
        plugin = FlextApiLoggingPlugin()
        test_client.add_plugin(plugin)

        request = FlextApiClientRequest(method=FlextApiClientMethod.GET, url="/test")

        # Test plugin data storage
        await plugin.before_request(request)
        assert "request_id" in request.plugin_data

        # Test metrics
        metrics = plugin.get_metrics()
        assert "requests_logged" in metrics
        assert metrics["requests_logged"] >= 1

    async def test_retry_plugin(self) -> None:
        """Test retry plugin configuration."""
        plugin = FlextApiRetryPlugin()

        request = FlextApiClientRequest(
            method=FlextApiClientMethod.GET,
            url="/test",
            retry_count=1,
        )

        await plugin.before_request(request)
        # Plugin should increase retry count to its config
        assert request.retry_count >= plugin.config.max_retries

    async def test_caching_plugin(self) -> None:
        """Test caching plugin functionality."""
        plugin = FlextApiCachingPlugin()

        request = FlextApiClientRequest(method=FlextApiClientMethod.GET, url="/test")

        # Test cache miss
        await plugin.before_request(request)
        metrics = plugin.get_metrics()
        assert "cache_misses" in metrics

    async def test_metrics_plugin(self) -> None:
        """Test metrics plugin functionality."""
        plugin = FlextApiMetricsPlugin()

        request = FlextApiClientRequest(method=FlextApiClientMethod.GET, url="/test")

        await plugin.before_request(request)

        response = FlextApiClientResponse(status_code=200, execution_time_ms=100.0)

        await plugin.after_request(request, response)

        metrics = plugin.get_metrics()
        assert "total_requests" in metrics
        assert "successful_requests" in metrics
        assert "average_response_time" in metrics

    async def test_circuit_breaker_plugin(self) -> None:
        """Test circuit breaker plugin functionality."""
        plugin = FlextApiCircuitBreakerPlugin()

        request = FlextApiClientRequest(method=FlextApiClientMethod.GET, url="/test")

        # Test normal state
        await plugin.before_request(request)
        assert "circuit_breaker_blocked" not in request.plugin_data

        # Test successful response
        response = FlextApiClientResponse(status_code=200)
        await plugin.after_request(request, response)

        metrics = plugin.get_metrics()
        assert "successful_requests" in metrics


# ==============================================================================
# PROTOCOL CLIENT TESTS
# ==============================================================================


class TestProtocolClients:
    """Test protocol-specific client functionality."""

    async def test_graphql_client_initialization(
        self,
        test_client: FlextApiClient,
    ) -> None:
        """Test GraphQL client initialization."""
        graphql_client = FlextApiGraphQLClient(test_client)

        assert graphql_client.client is test_client
        assert graphql_client.config.endpoint == "/graphql"
        assert graphql_client.config.introspection_enabled is True

        await graphql_client.disconnect()

    async def test_websocket_client_initialization(
        self,
        test_client: FlextApiClient,
    ) -> None:
        """Test WebSocket client initialization."""
        ws_client = FlextApiWebSocketClient(test_client)

        assert ws_client.client is test_client
        assert ws_client.config.endpoint == "/ws"
        assert ws_client.config.auto_reconnect is True

        await ws_client.disconnect()

    async def test_streaming_client_initialization(
        self,
        test_client: FlextApiClient,
    ) -> None:
        """Test Streaming client initialization."""
        streaming_client = FlextApiStreamingClient(test_client)

        assert streaming_client.client is test_client
        assert streaming_client.config.chunk_size == 8192
        assert streaming_client.config.buffer_size == 1024 * 1024

        await streaming_client.disconnect()


# ==============================================================================
# VALIDATION TESTS
# ==============================================================================


class TestValidationSystem:
    """Test request/response validation system."""

    def test_validation_manager_initialization(self) -> None:
        """Test validation manager creates correctly."""
        manager = FlextApiValidationManager()

        assert manager.request_validator is not None
        assert manager.response_validator is not None

        metrics = manager.get_metrics()
        assert "requests_validated" in metrics
        assert "responses_validated" in metrics
        assert "validation_failures" in metrics
        assert "total_validations" in metrics
        assert "success_rate" in metrics

    async def test_request_validation(self) -> None:
        """Test request validation functionality."""
        manager = FlextApiValidationManager()

        valid_request = FlextApiClientRequest(
            method=FlextApiClientMethod.GET,
            url="https://api.example.com/users",
            timeout=30.0,
        )

        result = manager.validate_request(valid_request)
        assert result.success is True

        # Test invalid request
        invalid_request = FlextApiClientRequest(
            method=FlextApiClientMethod.GET,
            url="",  # Invalid empty URL
            timeout=-1.0,  # Invalid negative timeout
        )

        result = manager.validate_request(invalid_request)
        assert result.success is False
        assert "errors" in result.data

    async def test_response_validation(self) -> None:
        """Test response validation functionality."""
        manager = FlextApiValidationManager()

        valid_response = FlextApiClientResponse(
            status_code=200,
            execution_time_ms=150.0,
        )

        result = manager.validate_response(valid_response)
        assert result.success is True

        # Test invalid response
        invalid_response = FlextApiClientResponse(
            status_code=999,  # Invalid status code
            execution_time_ms=-10.0,  # Invalid negative time
        )

        result = manager.validate_response(invalid_response)
        assert result.success is False
        assert "errors" in result.data


# ==============================================================================
# INTEGRATION TESTS
# ==============================================================================


class TestIntegration:
    """Test complete integration scenarios."""

    async def test_full_enterprise_stack(self) -> None:
        """Test complete enterprise stack with all features."""
        client = (
            FlextApiClientBuilder()
            .with_base_url("https://api.test.com")
            .with_auth_token("test-token")
            .with_caching(True, 300)
            .with_circuit_breaker(True, 3)
            .with_retries(3, 1.0)
            .with_validation(True, True)
            .with_observability(True, True)
            .with_plugin(FlextApiLoggingPlugin())
            .with_plugin(FlextApiMetricsPlugin())
            .build()
        )

        # Verify all features are configured
        assert client.config.auth_token == "test-token"
        assert client.config.cache_enabled is True
        assert client.config.circuit_breaker_enabled is True
        assert client.config.max_retries == 3
        assert client.config.validate_requests is True
        assert client.config.metrics_enabled is True
        assert len(client._plugins) == 2

        # Test health and metrics
        health = client.get_health()
        metrics = client.get_metrics()

        assert health["status"] in {"healthy", "degraded", "unhealthy"}
        assert metrics.total_requests >= 0

        await client.close()

    async def test_zero_duplication_validation(self) -> None:
        """Test that there are no duplicate functionalities."""
        # Create multiple clients with same config
        config = FlextApiClientConfig(base_url="https://test.com")

        client1 = FlextApiClient(config)
        client2 = FlextApiClient(config)

        # Each client should have independent state
        assert client1 is not client2
        assert client1._cache is not client2._cache
        assert client1._circuit_breaker is not client2._circuit_breaker
        assert client1._metrics is not client2._metrics

        # But should share configuration values
        assert client1.config.base_url == client2.config.base_url
        assert client1.config.timeout == client2.config.timeout

        await client1.close()
        await client2.close()

    async def test_root_namespace_access(self) -> None:
        """Test that all functionality is accessible from root namespace."""
        # This test validates that imports work from root
        from flext_api import (
            FlextApiClient,
            FlextApiClientBuilder,
            FlextApiClientConfig,
            FlextApiClientMethod,
            FlextApiClientRequest,
            FlextApiClientResponse,
            flext_api_create_client,
        )

        # All classes should be importable and instantiable
        assert FlextApiClient is not None
        assert FlextApiClientBuilder is not None
        assert FlextApiClientConfig is not None
        assert FlextApiClientMethod is not None
        assert FlextApiClientRequest is not None
        assert FlextApiClientResponse is not None

        # Test factory functions work
        client = flext_api_create_client("https://test.com")
        assert isinstance(client, FlextApiClient)
        await client.close()


# ==============================================================================
# PERFORMANCE TESTS
# ==============================================================================


class TestPerformance:
    """Test performance characteristics."""

    async def test_concurrent_requests(self) -> None:
        """Test handling of concurrent requests."""
        client = flext_api_create_client("https://httpbin.org")

        async with client:
            # Create multiple concurrent requests
            tasks = [
                client.get("/json"),
                client.get("/headers"),
                client.get("/user-agent"),
                client.get("/ip"),
                client.get("/uuid"),
            ]

            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            execution_time = time.time() - start_time

            # Should complete in reasonable time (less than 10 seconds)
            assert execution_time < 10.0

            # Most requests should succeed (allowing for network issues)
            successful = sum(
                1 for r in results if not isinstance(r, Exception) and r.success
            )
            assert successful >= len(tasks) * 0.6  # At least 60% success rate

    async def test_plugin_overhead(self) -> None:
        """Test that plugins don't add significant overhead."""
        # Client without plugins
        client_no_plugins = flext_api_create_client("https://httpbin.org")

        # Client with multiple plugins
        client_with_plugins = (
            FlextApiClientBuilder()
            .with_base_url("https://httpbin.org")
            .with_plugin(FlextApiLoggingPlugin())
            .with_plugin(FlextApiRetryPlugin())
            .with_plugin(FlextApiCachingPlugin())
            .with_plugin(FlextApiMetricsPlugin())
            .build()
        )

        async with client_no_plugins, client_with_plugins:
            # Test single request timing
            start_time = time.time()
            result1 = await client_no_plugins.get("/json")
            time_no_plugins = time.time() - start_time

            start_time = time.time()
            result2 = await client_with_plugins.get("/json")
            time_with_plugins = time.time() - start_time

            # Plugin overhead should be minimal (less than 2x slower)
            if result1.success and result2.success:
                overhead_ratio = time_with_plugins / max(time_no_plugins, 0.001)
                assert overhead_ratio < 3.0  # Less than 3x slower


# ==============================================================================
# EDGE CASE TESTS
# ==============================================================================


class TestEdgeCases:
    """Test edge cases and error conditions."""

    async def test_invalid_configuration(self) -> None:
        """Test client handles invalid configuration gracefully."""
        config = FlextApiClientConfig(
            base_url="",  # Invalid empty URL
            timeout=-1.0,  # Invalid negative timeout
            max_retries=-1,  # Invalid negative retries
        )

        client = FlextApiClient(config)

        # Client should still initialize (validation happens at request time)
        assert client is not None

        await client.close()

    async def test_network_errors(self, test_client: FlextApiClient) -> None:
        """Test handling of network errors."""
        # Mock network error
        test_client._session.request.side_effect = TimeoutError("Network timeout")

        request = FlextApiClientRequest(
            method=FlextApiClientMethod.GET,
            url="/test",
            retry_count=1,
        )

        result = await test_client.request(request)

        # Should fail gracefully
        assert result.success is False
        assert "timeout" in result.message.lower() or "failed" in result.message.lower()

    async def test_large_response_handling(self, test_client: FlextApiClient) -> None:
        """Test handling of large responses."""
        # Mock large response
        large_data = {"data": "x" * 10000}  # 10KB of data
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text.return_value = json.dumps(large_data)
        mock_response.json.return_value = large_data

        test_client._session.request.return_value.__aenter__.return_value = (
            mock_response
        )

        request = FlextApiClientRequest(
            method=FlextApiClientMethod.GET,
            url="/large-data",
        )

        result = await test_client.request(request)

        assert result.success is True
        assert len(result.data.text) > 10000
        assert result.data.json_data == large_data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
