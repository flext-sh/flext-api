#!/usr/bin/env python3
"""Tests for FlextApi Microservices Helpers - Comprehensive validation of microservices functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Comprehensive tests for microservices helpers that provide massive code reduction
for microservices architecture patterns. Tests all components without mocks.
"""

import time

import pytest

from flext_api.helpers.flext_api_microservices import (
    FlextApiCircuitBreaker,
    FlextApiMicroservicesPlatform,
    FlextApiRateLimiter,
    FlextApiServiceClient,
    FlextApiServiceRegistry,
    flext_api_create_circuit_breaker,
    flext_api_create_microservices_platform,
    flext_api_create_rate_limiter,
    flext_api_create_service_client,
    flext_api_create_service_registry,
)


class TestFlextApiServiceRegistry:
    """Test service registry functionality."""

    def test_create_service_registry(self) -> None:
        """Test service registry creation."""
        registry = flext_api_create_service_registry()
        assert isinstance(registry, FlextApiServiceRegistry)

    def test_register_service_success(self) -> None:
        """Test successful service registration."""
        registry = FlextApiServiceRegistry()

        result = registry.flext_api_register_service(
            service_name="test-service",
            host="localhost",
            port=8080,
            protocol="http",
            version="v1",
        )

        assert result.is_success
        assert result.data is True

    def test_discover_registered_service(self) -> None:
        """Test service discovery for registered service."""
        registry = FlextApiServiceRegistry()

        # Register service
        registry.flext_api_register_service(
            "api-service",
            "api.example.com",
            443,
            "https",
            "v2",
        )

        # Discover service
        result = registry.flext_api_discover_service("api-service")

        assert result.is_success
        endpoint = result.data
        assert endpoint["service_name"] == "api-service"
        assert endpoint["host"] == "api.example.com"
        assert endpoint["port"] == 443
        assert endpoint["protocol"] == "https"
        assert endpoint["version"] == "v2"

    def test_discover_nonexistent_service(self) -> None:
        """Test service discovery for non-existent service."""
        registry = FlextApiServiceRegistry()

        result = registry.flext_api_discover_service("missing-service")

        assert not result.is_success
        assert "not found" in result.error.lower()

    def test_list_services(self) -> None:
        """Test listing all registered services."""
        registry = FlextApiServiceRegistry()

        # Register multiple services
        registry.flext_api_register_service("service-1", "host1", 8001)
        registry.flext_api_register_service("service-2", "host2", 8002)
        registry.flext_api_register_service("service-3", "host3", 8003)

        result = registry.flext_api_list_services()

        assert result.is_success
        services = result.data
        assert len(services) == 3
        assert "service-1" in services
        assert "service-2" in services
        assert "service-3" in services

    def test_get_service_url(self) -> None:
        """Test getting complete service URL."""
        registry = FlextApiServiceRegistry()

        registry.flext_api_register_service(
            "web-service",
            "web.example.com",
            9000,
            "https",
        )

        result = registry.flext_api_get_service_url("web-service")

        assert result.is_success
        assert result.data == "https://web.example.com:9000"


class TestFlextApiCircuitBreaker:
    """Test circuit breaker functionality."""

    def test_create_circuit_breaker(self) -> None:
        """Test circuit breaker creation."""
        breaker = flext_api_create_circuit_breaker(
            failure_threshold=3,
            timeout_seconds=30,
            success_threshold=2,
        )
        assert isinstance(breaker, FlextApiCircuitBreaker)

    def test_initial_circuit_closed(self) -> None:
        """Test circuit breaker starts in closed state."""
        breaker = FlextApiCircuitBreaker()

        assert breaker.flext_api_can_execute("test-service")

        state = breaker.flext_api_get_state("test-service")
        assert state["state"] == "closed"
        assert state["failure_count"] == 0

    def test_circuit_opens_after_failures(self) -> None:
        """Test circuit breaker opens after threshold failures."""
        breaker = FlextApiCircuitBreaker(failure_threshold=2)

        # Record failures
        breaker.flext_api_record_failure("failing-service")
        assert breaker.flext_api_can_execute("failing-service")

        breaker.flext_api_record_failure("failing-service")
        assert not breaker.flext_api_can_execute("failing-service")

        state = breaker.flext_api_get_state("failing-service")
        assert state["state"] == "open"
        assert state["failure_count"] == 2

    def test_circuit_half_open_after_timeout(self) -> None:
        """Test circuit breaker goes to half-open after timeout."""
        breaker = FlextApiCircuitBreaker(failure_threshold=1, timeout_seconds=1)

        # Open circuit
        breaker.flext_api_record_failure("service")
        assert not breaker.flext_api_can_execute("service")

        # Wait for timeout
        time.sleep(1.1)

        # Should now allow execution (half-open)
        assert breaker.flext_api_can_execute("service")

        state = breaker.flext_api_get_state("service")
        assert state["state"] == "half_open"

    def test_circuit_closes_after_success(self) -> None:
        """Test circuit breaker closes after successful execution."""
        breaker = FlextApiCircuitBreaker(failure_threshold=1)

        # Open circuit
        breaker.flext_api_record_failure("service")

        # Record success in half-open state
        state = breaker.flext_api_get_state("service")
        state["state"] = "half_open"

        breaker.flext_api_record_success("service")

        state = breaker.flext_api_get_state("service")
        assert state["state"] == "closed"
        assert state["failure_count"] == 0


class TestFlextApiRateLimiter:
    """Test rate limiter functionality."""

    def test_create_rate_limiter(self) -> None:
        """Test rate limiter creation."""
        limiter = flext_api_create_rate_limiter()
        assert isinstance(limiter, FlextApiRateLimiter)

    def test_rate_limit_allows_initial_requests(self) -> None:
        """Test rate limiter allows initial requests within limit."""
        limiter = FlextApiRateLimiter()

        # Should allow first few requests
        assert limiter.flext_api_can_proceed("service", requests_per_second=5)
        assert limiter.flext_api_can_proceed("service", requests_per_second=5)
        assert limiter.flext_api_can_proceed("service", requests_per_second=5)

    def test_rate_limit_blocks_excess_requests(self) -> None:
        """Test rate limiter blocks requests exceeding limit."""
        limiter = FlextApiRateLimiter()

        # Fill up the rate limit
        for _ in range(2):
            assert limiter.flext_api_can_proceed("service", requests_per_second=2)

        # Next request should be blocked
        assert not limiter.flext_api_can_proceed("service", requests_per_second=2)

    @pytest.mark.asyncio
    async def test_rate_limit_context_manager(self) -> None:
        """Test rate limiter context manager."""
        limiter = FlextApiRateLimiter()

        async with limiter.flext_api_rate_limit_context("service", 10) as can_proceed:
            assert isinstance(can_proceed, bool)


class TestFlextApiServiceClient:
    """Test service client functionality."""

    def test_create_service_client(self) -> None:
        """Test service client creation."""
        registry = flext_api_create_service_registry()
        client = flext_api_create_service_client(registry)
        assert isinstance(client, FlextApiServiceClient)

    def test_create_request(self) -> None:
        """Test creating service request."""
        registry = FlextApiServiceRegistry()
        client = FlextApiServiceClient(registry)

        request = client.flext_api_create_request(
            target_service="api-service",
            method="POST",
            path="/users",
            body={"name": "John Doe"},
            source_service="web-app",
        )

        assert request["target_service"] == "api-service"
        assert request["method"] == "POST"
        assert request["path"] == "/users"
        assert request["body"] == {"name": "John Doe"}
        assert request["source_service"] == "web-app"
        assert request["request_id"]
        assert request["correlation_id"]

    @pytest.mark.asyncio
    async def test_execute_request_service_not_found(self) -> None:
        """Test executing request when service not found."""
        registry = FlextApiServiceRegistry()
        client = FlextApiServiceClient(registry)

        request = client.flext_api_create_request(
            "missing-service",
            "GET",
            "/health",
        )

        result = await client.flext_api_execute_request(request)

        assert not result.is_success
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execute_request_success(self) -> None:
        """Test successful request execution."""
        registry = FlextApiServiceRegistry()
        registry.flext_api_register_service("test-service", "localhost", 8080)

        client = FlextApiServiceClient(registry)

        request = client.flext_api_create_request(
            "test-service",
            "GET",
            "/health",
        )

        result = await client.flext_api_execute_request(request)

        assert result.is_success
        response = result.data
        assert response["success"]
        assert response["status_code"] == 200
        assert response["request_id"] == request["request_id"]

    @pytest.mark.asyncio
    async def test_convenience_methods(self) -> None:
        """Test convenience methods for HTTP verbs."""
        registry = FlextApiServiceRegistry()
        registry.flext_api_register_service("api", "api.test.com", 443, "https")

        client = FlextApiServiceClient(registry)

        # Test GET
        get_result = await client.flext_api_get("api", "/status")
        assert get_result.is_success

        # Test POST
        post_result = await client.flext_api_post("api", "/data", {"key": "value"})
        assert post_result.is_success

    @pytest.mark.asyncio
    async def test_health_check(self) -> None:
        """Test health check functionality."""
        registry = FlextApiServiceRegistry()
        registry.flext_api_register_service("healthy-service", "health.test.com", 8080)

        client = FlextApiServiceClient(registry)

        result = await client.flext_api_health_check("healthy-service")

        assert result.is_success
        assert result.data is True

    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self) -> None:
        """Test circuit breaker integration with service client."""
        registry = FlextApiServiceRegistry()
        breaker = FlextApiCircuitBreaker(failure_threshold=1)
        client = FlextApiServiceClient(registry, breaker)

        # Force circuit open
        breaker.flext_api_record_failure("circuit-test")

        request = client.flext_api_create_request("circuit-test", "GET", "/test")

        result = await client.flext_api_execute_request(request)

        assert not result.is_success
        assert "circuit breaker open" in result.error.lower()


class TestFlextApiMicroservicesPlatform:
    """Test complete microservices platform."""

    def test_create_microservices_platform(self) -> None:
        """Test microservices platform creation."""
        platform = flext_api_create_microservices_platform()
        assert isinstance(platform, FlextApiMicroservicesPlatform)

    def test_register_service_through_platform(self) -> None:
        """Test service registration through platform."""
        platform = FlextApiMicroservicesPlatform()

        result = platform.flext_api_register_service(
            "platform-service",
            "platform.test.com",
            9090,
        )

        assert result.is_success

    @pytest.mark.asyncio
    async def test_call_service_through_platform(self) -> None:
        """Test calling service through platform."""
        platform = FlextApiMicroservicesPlatform()

        # Register a service
        platform.flext_api_register_service("echo-service", "echo.test.com", 8080)

        # Call the service
        result = await platform.flext_api_call_service(
            service_name="echo-service",
            method="POST",
            path="/echo",
            data={"message": "hello"},
            source_service="test-client",
            rate_limit=5,
        )

        assert result.is_success
        response = result.data
        assert response["success"]

    @pytest.mark.asyncio
    async def test_health_check_all_services(self) -> None:
        """Test health check for all registered services."""
        platform = FlextApiMicroservicesPlatform()

        # Register multiple services
        platform.flext_api_register_service("service-1", "s1.test.com", 8001)
        platform.flext_api_register_service("service-2", "s2.test.com", 8002)
        platform.flext_api_register_service("service-3", "s3.test.com", 8003)

        result = await platform.flext_api_health_check_all()

        assert result.is_success
        health_status = result.data
        assert len(health_status) == 3
        assert "service-1" in health_status
        assert "service-2" in health_status
        assert "service-3" in health_status


class TestMicroservicesIntegration:
    """Test integration between microservices components."""

    @pytest.mark.asyncio
    async def test_complete_microservices_workflow(self) -> None:
        """Test complete workflow with all microservices components."""
        # Create platform
        platform = FlextApiMicroservicesPlatform()

        # Register services
        platform.flext_api_register_service("user-service", "users.api.com", 8080)
        platform.flext_api_register_service("order-service", "orders.api.com", 8081)
        platform.flext_api_register_service("payment-service", "payments.api.com", 8082)

        # Test service calls with rate limiting and circuit breaker
        user_result = await platform.flext_api_call_service(
            "user-service",
            "GET",
            "/users/123",
            rate_limit=10,
        )
        assert user_result.is_success

        order_result = await platform.flext_api_call_service(
            "order-service",
            "POST",
            "/orders",
            data={"user_id": 123, "items": ["item1", "item2"]},
            rate_limit=5,
        )
        assert order_result.is_success

        # Health check all services
        health_result = await platform.flext_api_health_check_all()
        assert health_result.is_success
        assert len(health_result.data) == 3

    def test_real_world_service_configuration(self) -> None:
        """Test realistic service configuration scenarios."""
        platform = FlextApiMicroservicesPlatform()

        # Register production-like services
        services = [
            ("auth-service", "auth.internal.com", 8080, "https", "v1"),
            ("user-service", "users.internal.com", 8081, "https", "v2"),
            ("inventory-service", "inventory.internal.com", 8082, "https", "v1"),
            ("notification-service", "notifications.internal.com", 8083, "https", "v1"),
        ]

        for service_name, host, port, protocol, version in services:
            result = platform.flext_api_register_service(
                service_name,
                host,
                port,
                protocol=protocol,
                version=version,
            )
            assert result.is_success

        # Verify all services are registered
        services_result = platform.service_registry.flext_api_list_services()
        assert services_result.is_success
        assert len(services_result.data) == 4

    def test_error_handling_and_resilience(self) -> None:
        """Test error handling and resilience patterns."""
        # Test circuit breaker configuration
        breaker = flext_api_create_circuit_breaker(
            failure_threshold=3,
            timeout_seconds=30,
            success_threshold=2,
        )
        assert breaker.failure_threshold == 3
        assert breaker.timeout_seconds == 30
        assert breaker.success_threshold == 2

        # Test rate limiter configuration
        limiter = flext_api_create_rate_limiter()
        assert isinstance(limiter, FlextApiRateLimiter)

        # Test service registry resilience
        registry = flext_api_create_service_registry()

        # Try to discover non-existent service
        result = registry.flext_api_discover_service("non-existent")
        assert not result.is_success

        # Registry should still work for other operations
        register_result = registry.flext_api_register_service(
            "working-service",
            "localhost",
            8080,
        )
        assert register_result.is_success


if __name__ == "__main__":
    # Run basic functionality tests

    # Test service registry
    registry = flext_api_create_service_registry()

    # Test service registration
    result = registry.flext_api_register_service("test", "localhost", 8080)

    # Test service discovery
    discovery_result = registry.flext_api_discover_service("test")

    # Test circuit breaker
    breaker = flext_api_create_circuit_breaker()

    # Test rate limiter
    limiter = flext_api_create_rate_limiter()

    # Test complete platform
    platform = flext_api_create_microservices_platform()
