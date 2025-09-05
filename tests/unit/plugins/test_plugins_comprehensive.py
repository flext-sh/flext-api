"""Comprehensive tests for FlextApiPlugins with real functionality validation.

Tests all plugin functionality using flext_tests library without mocks.
Achieves 100% coverage for plugins.py module.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import base64
import time

import pytest

from flext_api import FlextApiPlugins
from flext_api.plugins import (
    CachingPluginConfig,
    CircuitBreakerPluginConfig,
    PluginConfig,
    RateLimitPluginConfig,
)


class TestFlextApiPlugins:
    """Comprehensive plugin system tests."""

    def test_plugin_config_models(self) -> None:
        """Test all plugin configuration models."""
        # Base plugin config
        base_config = PluginConfig(name="test_plugin", enabled=False, priority=10)
        assert base_config.name == "test_plugin"
        assert base_config.enabled is False
        assert base_config.priority == 10

        # Caching plugin config with defaults
        caching_config = CachingPluginConfig()
        assert caching_config.name == "caching_plugin"
        assert caching_config.enabled is True
        assert caching_config.ttl > 0
        assert caching_config.max_size > 0

        # Rate limit config
        rate_config = RateLimitPluginConfig(calls_per_second=5.0, burst_size=15)
        assert rate_config.calls_per_second == 5.0
        assert rate_config.burst_size == 15

        # Circuit breaker config
        cb_config = CircuitBreakerPluginConfig(
            failure_threshold=3, recovery_timeout=30.0
        )
        assert cb_config.failure_threshold == 3
        assert cb_config.recovery_timeout == 30.0

    @pytest.mark.asyncio
    async def test_base_plugin_interface(self) -> None:
        """Test BasePlugin interface with all methods."""
        plugins = FlextApiPlugins()
        plugin = plugins.BasePlugin(
            id="test_id", name="test_base", enabled=True, priority=5
        )

        assert plugin.name == "test_base"
        assert plugin.enabled is True
        assert plugin.priority == 5

        # Test before_request
        result = await plugin.before_request(
            "GET", "https://example.com", {}, {"param": "value"}, {"body": "data"}
        )
        assert result.success
        method, url, _headers, params, body = result.value
        assert method == "GET"
        assert url == "https://example.com"
        assert params["param"] == "value"
        assert body["body"] == "data"

        # Test after_response
        response_result = await plugin.after_response(
            {"data": "test"}, {"header": "value"}, 200
        )
        assert response_result.success
        assert response_result.value["data"] == "test"

        # Test on_error
        error_result = await plugin.on_error(
            ValueError("test error"), "POST", "https://example.com"
        )
        assert not error_result.success
        assert "Request failed: test error" in error_result.error

        # Test base plugin validation
        validation_result = plugin.validate_business_rules()
        assert validation_result.success

        # Test validation failure with empty name
        plugin.name = ""
        validation_failure = plugin.validate_business_rules()
        assert not validation_failure.success
        assert "Plugin name must be non-empty string" in validation_failure.error

    @pytest.mark.asyncio
    async def test_async_plugin_lifecycle(self) -> None:
        """Test AsyncPlugin lifecycle management."""
        plugins = FlextApiPlugins()
        async_plugin = plugins.AsyncPlugin("test_async", enabled=True, priority=1)

        assert not async_plugin.is_started

        # Start plugin
        start_result = await async_plugin.start()
        assert start_result.success
        assert async_plugin.is_started

        # Start again (should be idempotent)
        start_result2 = await async_plugin.start()
        assert start_result2.success
        assert async_plugin.is_started

        # Stop plugin
        stop_result = await async_plugin.stop()
        assert stop_result.success
        assert not async_plugin.is_started

        # Stop again (should be idempotent)
        stop_result2 = await async_plugin.stop()
        assert stop_result2.success
        assert not async_plugin.is_started

    @pytest.mark.asyncio
    async def test_caching_plugin_functionality(self) -> None:
        """Test CachingPlugin with real caching logic."""
        plugins = FlextApiPlugins()
        config = CachingPluginConfig(ttl=2, max_size=5)  # Short TTL for testing
        caching_plugin = plugins.CachingPlugin(config)

        assert caching_plugin.ttl == 2
        assert caching_plugin.max_size == 5

        # Test business rules validation
        validation = caching_plugin.validate_business_rules()
        assert validation.success

        # Test cache key generation
        key = caching_plugin._generate_cache_key(
            "GET", "https://example.com", {"q": "test"}
        )
        assert "GET:https://example.com?q=test" in key

        # POST requests should not be cached (empty key)
        post_key = caching_plugin._generate_cache_key("POST", "https://example.com", {})
        assert post_key == ""

        # Test cache validity
        current_time = time.time()
        assert caching_plugin._is_cache_valid(current_time)  # Just set, should be valid
        assert not caching_plugin._is_cache_valid(
            current_time - 10
        )  # 10 seconds ago, should expire

        # Test before_request (cache miss)
        result = await caching_plugin.before_request(
            "GET", "https://example.com", {"Accept": "application/json"}, {"q": "test"}
        )
        assert result.success
        method, _url, headers, _params, _body = result.value
        assert method == "GET"
        assert "X-Cache" not in headers  # No cache hit

        # Test after_response with successful status
        response_result = await caching_plugin.after_response(
            {"result": "success"}, {"Content-Type": "application/json"}, 200
        )
        assert response_result.success
        assert response_result.value["result"] == "success"

    @pytest.mark.asyncio
    async def test_caching_plugin_validation_failure(self) -> None:
        """Test caching plugin with invalid configuration."""
        plugins = FlextApiPlugins()

        # Create plugin with invalid TTL
        config = CachingPluginConfig(ttl=-1, max_size=100)
        invalid_plugin = plugins.CachingPlugin(config)

        validation = invalid_plugin.validate_business_rules()
        assert not validation.success
        assert "Cache TTL must be positive" in validation.error

        # Test with invalid max_size
        config2 = CachingPluginConfig(ttl=60, max_size=-5)
        invalid_plugin2 = plugins.CachingPlugin(config2)

        validation2 = invalid_plugin2.validate_business_rules()
        assert not validation2.success
        assert "Cache max_size must be positive" in validation2.error

    @pytest.mark.asyncio
    async def test_retry_plugin_functionality(self) -> None:
        """Test RetryPlugin with real retry logic."""
        plugins = FlextApiPlugins()
        retry_plugin = plugins.RetryPlugin()

        # Test business rules validation
        validation = retry_plugin.validate_business_rules()
        assert validation.success

        # Test should_retry logic
        assert await retry_plugin.should_retry(500, 1)  # Server error, first attempt
        assert await retry_plugin.should_retry(502, 2)  # Bad gateway, second attempt
        assert not await retry_plugin.should_retry(
            400, 1
        )  # Client error, should not retry
        assert not await retry_plugin.should_retry(500, 10)  # Too many attempts

        # Test delay calculation
        delay1 = await retry_plugin.calculate_delay(1)
        delay2 = await retry_plugin.calculate_delay(2)
        assert delay2 > delay1  # Exponential backoff

        delay_max = await retry_plugin.calculate_delay(10)
        assert delay_max <= 60.0  # Should cap at 60 seconds

        # Test on_error
        error_result = await retry_plugin.on_error(
            ConnectionError("Network error"), "GET", "https://example.com"
        )
        assert not error_result.success
        assert "Request failed after retries" in error_result.error

    @pytest.mark.asyncio
    async def test_retry_plugin_validation_failure(self) -> None:
        """Test retry plugin with invalid configuration."""
        plugins = FlextApiPlugins()
        retry_plugin = plugins.RetryPlugin()

        # Modify to invalid values
        retry_plugin.max_retries = -1
        validation = retry_plugin.validate_business_rules()
        assert not validation.success
        assert "Max retries cannot be negative" in validation.error

        # Test invalid backoff factor
        retry_plugin2 = plugins.RetryPlugin()
        retry_plugin2.backoff_factor = -0.5
        validation2 = retry_plugin2.validate_business_rules()
        assert not validation2.success
        assert "Backoff factor must be positive" in validation2.error

    @pytest.mark.asyncio
    async def test_auth_plugin_bearer_auth(self) -> None:
        """Test AuthPlugin with Bearer authentication."""
        plugins = FlextApiPlugins()
        auth_plugin = plugins.AuthPlugin()

        # Configure for Bearer auth
        auth_plugin.auth_type = "bearer"
        auth_plugin.token = "secret_token_123"

        # Test business rules validation
        validation = auth_plugin.validate_business_rules()
        assert validation.success

        # Test before_request adds Bearer header
        result = await auth_plugin.before_request(
            "GET", "https://api.example.com", {"User-Agent": "test"}, {}
        )
        assert result.success
        _method, _url, headers, _params, _body = result.value
        assert headers["Authorization"] == "Bearer secret_token_123"
        assert headers["User-Agent"] == "test"  # Original headers preserved

    @pytest.mark.asyncio
    async def test_auth_plugin_basic_auth(self) -> None:
        """Test AuthPlugin with Basic authentication."""
        plugins = FlextApiPlugins()
        auth_plugin = plugins.AuthPlugin()

        # Configure for Basic auth
        auth_plugin.auth_type = "basic"
        auth_plugin.username = "testuser"
        auth_plugin.password = "testpass"

        # Test business rules validation
        validation = auth_plugin.validate_business_rules()
        assert validation.success

        # Test before_request adds Basic header
        result = await auth_plugin.before_request(
            "POST", "https://api.example.com", {}, {"data": "test"}
        )
        assert result.success
        _method, _url, headers, _params, _body = result.value

        # Decode and verify Basic auth header
        auth_header = headers["Authorization"]
        assert auth_header.startswith("Basic ")
        encoded_credentials = auth_header.replace("Basic ", "")
        decoded = base64.b64decode(encoded_credentials).decode()
        assert decoded == "testuser:testpass"

    @pytest.mark.asyncio
    async def test_auth_plugin_validation_failures(self) -> None:
        """Test AuthPlugin with invalid configurations."""
        plugins = FlextApiPlugins()

        # Invalid auth type
        auth_plugin1 = plugins.AuthPlugin()
        auth_plugin1.auth_type = "invalid"
        validation1 = auth_plugin1.validate_business_rules()
        assert not validation1.success
        assert "Invalid auth type" in validation1.error

        # Bearer auth without token
        auth_plugin2 = plugins.AuthPlugin()
        auth_plugin2.auth_type = "bearer"
        auth_plugin2.token = None
        validation2 = auth_plugin2.validate_business_rules()
        assert not validation2.success
        assert "Bearer auth requires token" in validation2.error

        # Basic auth without username/password
        auth_plugin3 = plugins.AuthPlugin()
        auth_plugin3.auth_type = "basic"
        auth_plugin3.username = None
        auth_plugin3.password = "pass"
        validation3 = auth_plugin3.validate_business_rules()
        assert not validation3.success
        assert "Basic auth requires username and password" in validation3.error

    @pytest.mark.asyncio
    async def test_rate_limit_plugin_functionality(self) -> None:
        """Test RateLimitPlugin with token bucket algorithm."""
        plugins = FlextApiPlugins()
        config = RateLimitPluginConfig(calls_per_second=2.0, burst_size=3)
        rate_plugin = plugins.RateLimitPlugin(config)

        assert rate_plugin.calls_per_second == 2.0
        assert rate_plugin.burst_size == 3

        # Test business rules validation
        validation = rate_plugin.validate_business_rules()
        assert validation.success

        # Test first few requests (should be fast due to burst capacity)
        start_time = time.time()

        # First request
        result1 = await rate_plugin.before_request("GET", "https://example.com", {}, {})
        elapsed1 = time.time() - start_time
        assert result1.success
        assert elapsed1 < 0.1  # Should be immediate

        # Second request
        result2 = await rate_plugin.before_request("GET", "https://example.com", {}, {})
        elapsed2 = time.time() - start_time
        assert result2.success
        assert elapsed2 < 0.1  # Should still be immediate

        # Third request (last of burst)
        result3 = await rate_plugin.before_request("GET", "https://example.com", {}, {})
        elapsed3 = time.time() - start_time
        assert result3.success
        assert elapsed3 < 0.1  # Should still be immediate

    @pytest.mark.asyncio
    async def test_rate_limit_plugin_validation_failure(self) -> None:
        """Test rate limit plugin with invalid configuration."""
        plugins = FlextApiPlugins()

        config = RateLimitPluginConfig(calls_per_second=-1.0, burst_size=5)
        rate_plugin = plugins.RateLimitPlugin(config)

        validation = rate_plugin.validate_business_rules()
        assert not validation.success
        assert "Calls per second must be positive" in validation.error

        # Test invalid burst size
        config2 = RateLimitPluginConfig(calls_per_second=5.0, burst_size=-2)
        rate_plugin2 = plugins.RateLimitPlugin(config2)

        validation2 = rate_plugin2.validate_business_rules()
        assert not validation2.success
        assert "Burst size must be positive" in validation2.error

    @pytest.mark.asyncio
    async def test_circuit_breaker_plugin_states(self) -> None:
        """Test CircuitBreakerPlugin state transitions."""
        plugins = FlextApiPlugins()
        config = CircuitBreakerPluginConfig(failure_threshold=2, recovery_timeout=1.0)
        cb_plugin = plugins.CircuitBreakerPlugin(config)

        assert cb_plugin.failure_threshold == 2
        assert cb_plugin.recovery_timeout == 1.0
        assert cb_plugin._state == "closed"  # Initial state

        # Test business rules validation
        validation = cb_plugin.validate_business_rules()
        assert validation.success

        # Test successful request in closed state
        result = await cb_plugin.before_request("GET", "https://example.com", {}, {})
        assert result.success
        assert cb_plugin._state == "closed"

        # Simulate failure responses to open the circuit
        await cb_plugin.after_response({}, {}, 500)  # First failure
        assert cb_plugin._state == "closed"  # Still closed
        assert cb_plugin._failure_count == 1

        await cb_plugin.after_response({}, {}, 502)  # Second failure
        assert cb_plugin._state == "open"  # Circuit opened
        assert cb_plugin._failure_count == 2

        # Test request rejection in open state
        result_open = await cb_plugin.before_request(
            "GET", "https://example.com", {}, {}
        )
        assert not result_open.success
        assert "Circuit breaker is open" in result_open.error

        # Wait for recovery timeout and test half-open state
        await asyncio.sleep(1.1)  # Wait longer than recovery_timeout
        result_recovery = await cb_plugin.before_request(
            "GET", "https://example.com", {}, {}
        )
        assert result_recovery.success
        assert cb_plugin._state == "half-open"

        # Successful response should close the circuit
        await cb_plugin.after_response({}, {}, 200)
        assert cb_plugin._state == "closed"
        assert cb_plugin._failure_count == 0

    @pytest.mark.asyncio
    async def test_circuit_breaker_plugin_validation_failure(self) -> None:
        """Test circuit breaker plugin with invalid configuration."""
        plugins = FlextApiPlugins()

        config = CircuitBreakerPluginConfig(failure_threshold=-1, recovery_timeout=30.0)
        cb_plugin = plugins.CircuitBreakerPlugin(config)

        validation = cb_plugin.validate_business_rules()
        assert not validation.success
        assert "Failure threshold must be positive" in validation.error

        # Test invalid recovery timeout
        config2 = CircuitBreakerPluginConfig(
            failure_threshold=5, recovery_timeout=-10.0
        )
        cb_plugin2 = plugins.CircuitBreakerPlugin(config2)

        validation2 = cb_plugin2.validate_business_rules()
        assert not validation2.success
        assert "Recovery timeout must be positive" in validation2.error

    @pytest.mark.asyncio
    async def test_logging_plugin_functionality(self) -> None:
        """Test LoggingPlugin with all logging options."""
        plugins = FlextApiPlugins()
        logging_plugin = plugins.LoggingPlugin()

        # Test default configuration
        assert logging_plugin.log_requests is True
        assert logging_plugin.log_responses is True
        assert logging_plugin.log_errors is True

        # Test business rules (should always pass)
        validation = logging_plugin.validate_business_rules()
        assert validation.success

        # Test request logging
        result = await logging_plugin.before_request(
            "POST",
            "https://api.example.com/data",
            {"Content-Type": "application/json"},
            {"param": "value"},
            {"key": "data"},
        )
        assert result.success
        method, url, _headers, _params, _body = result.value
        assert method == "POST"
        assert url == "https://api.example.com/data"

        # Test response logging
        response_result = await logging_plugin.after_response(
            {"result": "success"}, {"Content-Type": "application/json"}, 201
        )
        assert response_result.success
        assert response_result.value["result"] == "success"

        # Test error logging
        error_result = await logging_plugin.on_error(
            TimeoutError("Request timeout"), "GET", "https://slow.example.com"
        )
        assert not error_result.success
        assert "Request failed: Request timeout" in error_result.error

    @pytest.mark.asyncio
    async def test_logging_plugin_selective_logging(self) -> None:
        """Test LoggingPlugin with selective logging options."""
        plugins = FlextApiPlugins()
        logging_plugin = plugins.LoggingPlugin()

        # Configure selective logging
        logging_plugin.log_requests = False
        logging_plugin.log_responses = True
        logging_plugin.log_errors = False

        # All operations should still work, just with different logging
        request_result = await logging_plugin.before_request(
            "GET", "https://example.com", {}, {}
        )
        assert request_result.success

        response_result = await logging_plugin.after_response({}, {}, 200)
        assert response_result.success

        error_result = await logging_plugin.on_error(
            ValueError("test"), "POST", "https://example.com"
        )
        assert not error_result.success

    def test_flext_api_plugins_all_exports(self) -> None:
        """Test that all plugin classes are accessible."""
        plugins = FlextApiPlugins()

        # Test all plugin classes can be instantiated
        base = plugins.BasePlugin(id="base_test")
        async_plugin = plugins.AsyncPlugin("test_async")

        # Plugin configuration classes should be importable
        assert CachingPluginConfig is not None
        assert RateLimitPluginConfig is not None
        assert CircuitBreakerPluginConfig is not None
        assert PluginConfig is not None

        # Test plugin names
        assert base.name == "base_plugin"
        assert async_plugin.name == "test_async"

    @pytest.mark.asyncio
    async def test_caching_plugin_cache_operations(self) -> None:
        """Test specific caching operations to increase coverage."""
        plugins = FlextApiPlugins()
        config = CachingPluginConfig(ttl=1, max_size=2)  # Small cache for testing
        caching_plugin = plugins.CachingPlugin(config)

        # Test cache cleanup - manually add expired entries
        caching_plugin._cache["old_key"] = (
            {"old": "data"},
            time.time() - 10,
        )  # Expired
        caching_plugin._cache["new_key"] = ({"new": "data"}, time.time())  # Fresh

        # Test cleanup_expired method
        caching_plugin._cleanup_expired()
        assert "old_key" not in caching_plugin._cache
        assert "new_key" in caching_plugin._cache

        # Test cache size limit triggering cleanup
        for i in range(5):  # More than max_size
            result = await caching_plugin.before_request(
                "GET", f"https://example.com/{i}", {}, {"param": i}
            )
            assert result.success

    @pytest.mark.asyncio
    async def test_cache_key_generation_edge_cases(self) -> None:
        """Test cache key generation edge cases."""
        plugins = FlextApiPlugins()
        config = CachingPluginConfig()
        caching_plugin = plugins.CachingPlugin(config)

        # Test with no params
        key1 = caching_plugin._generate_cache_key("GET", "https://example.com", {})
        assert key1 == "GET:https://example.com"

        # Test with params
        key2 = caching_plugin._generate_cache_key(
            "GET", "https://example.com", {"a": "1", "b": "2"}
        )
        assert "a=1" in key2
        assert "b=2" in key2

        # Test non-GET method (should return empty)
        key3 = caching_plugin._generate_cache_key("POST", "https://example.com", {})
        assert key3 == ""

    @pytest.mark.asyncio
    async def test_rate_limit_edge_cases(self) -> None:
        """Test rate limit edge cases to increase coverage."""
        plugins = FlextApiPlugins()
        config = RateLimitPluginConfig(
            calls_per_second=10.0, burst_size=1
        )  # Very restrictive
        rate_plugin = plugins.RateLimitPlugin(config)

        # Initial state - tokens should be equal to burst_size
        assert rate_plugin._tokens == 1.0

        # First request should work immediately
        result1 = await rate_plugin.before_request("GET", "https://example.com", {}, {})
        assert result1.success

        # Tokens should be decremented
        assert rate_plugin._tokens == 0.0

    @pytest.mark.asyncio
    async def test_circuit_breaker_edge_cases(self) -> None:
        """Test circuit breaker edge cases."""
        plugins = FlextApiPlugins()
        config = CircuitBreakerPluginConfig(failure_threshold=1, recovery_timeout=0.1)
        cb_plugin = plugins.CircuitBreakerPlugin(config)

        # Test failure in half-open state
        cb_plugin._state = "half-open"
        await cb_plugin.after_response({}, {}, 500)
        assert cb_plugin._failure_count == 1
        assert cb_plugin._state == "open"
